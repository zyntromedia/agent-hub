"""
Workflow จัดระเบียบไฟล์ - Automated File Management System (v2, fixed)
Monitors a folder, converts (txt->md, wav->mp3), organizes by category,
git-commits, and logs to a JSON dashboard.

Fixes vs v1:
- All syntax/indentation errors corrected
- Optional deps (GitPython, pydub) guarded — script runs without them
- shutil.move (not copy) + temp cleanup -> no infinite reprocessing
- All 7 categories mapped + 'other' fallback; every file gets a name
- Path-consistent: everything lives under output_dir (git repo sees files)
- File-stability wait (no truncated WAV/MP3) + handles on_moved (drag-in)
- Worker queue (observer never blocked) + dedupe + symlink/path safety
- Dashboard capped + utf-8 + specific exceptions
- Conservative txt->md (no false headings), argparse CLI
"""

import os
import json
import time
import shutil
import logging
import argparse
import queue
import re
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

# --- Core dependency (required) ---
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Optional dependencies ---
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

try:
    from pydub import AudioSegment
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("file_workflow.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EXTENSION_CATEGORY = {
    # documents
    ".txt": "documents", ".md": "documents", ".pdf": "documents",
    ".doc": "documents", ".docx": "documents", ".odt": "documents",
    ".rtf": "documents", ".epub": "documents", ".csv": "documents",
    # audio
    ".wav": "audio", ".mp3": "audio", ".flac": "audio", ".ogg": "audio",
    ".m4a": "audio", ".aac": "audio", ".wma": "audio",
    # images
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".bmp": "images", ".svg": "images", ".webp": "images", ".tiff": "images",
    ".heic": "images",
    # videos
    ".mp4": "videos", ".mkv": "videos", ".avi": "videos", ".mov": "videos",
    ".wmv": "videos", ".flv": "videos", ".webm": "videos", ".m4v": "videos",
    # archives
    ".zip": "archives", ".rar": "archives", ".7z": "archives", ".tar": "archives",
    ".gz": "archives", ".bz2": "archives", ".xz": "archives",
    # code
    ".py": "code", ".js": "code", ".jsx": "code", ".ts": "code", ".tsx": "code",
    ".java": "code", ".c": "code", ".cpp": "code", ".h": "code", ".cs": "code",
    ".go": "code", ".rs": "code", ".rb": "code", ".php": "code", ".sh": "code",
    ".html": "code", ".css": "code", ".json": "code", ".xml": "code", ".yml": "code",
    ".yaml": "code", ".sql": "code",
}

CATEGORY_DIR = {
    "documents": "Documents", "audio": "Audio", "images": "Images",
    "videos": "Videos", "archives": "Archives", "code": "Code", "other": "Other",
}

CONVERSIONS = {".txt": ".md", ".wav": ".mp3"}

TEMP_EXTENSIONS = {".part", ".crdownload", ".tmp", ".download", "~"}
MAX_DASHBOARD_ENTRIES = 2000
STABILITY_POLLS = 3          # consecutive equal-size reads before processing
STABILITY_INTERVAL = 0.8     # seconds between polls


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
class FileWorkflowConfig:
    def __init__(self, watch_dir: str, output_dir: str = "organized_output",
                 git_repo_path: Optional[str] = None):
        self.watch_dir = Path(watch_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        # Everything organized under output_dir so git (at output_dir) sees it
        self.organized_root = self.output_dir / "organized_files"
        self.tmp_dir = self.output_dir / ".tmp_convert"
        self.git_repo_path = Path(git_repo_path).resolve() if git_repo_path else self.output_dir
        self.dashboard_log = self.output_dir / "workflow_dashboard.json"

        for d in (self.watch_dir, self.output_dir, self.organized_root, self.tmp_dir):
            d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Step 1: Analyze (rule-based — rename kept for compatibility)
# ---------------------------------------------------------------------------
class FileRuleAnalyzer:
    @staticmethod
    def analyze_file(file_path: Path) -> Dict:
        ext = file_path.suffix.lower()
        category = EXTENSION_CATEGORY.get(ext, "other")
        target_ext = CONVERSIONS.get(ext)
        needs_conversion = target_ext is not None and (
            (target_ext == ".md") or (target_ext == ".mp3" and AUDIO_AVAILABLE)
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = re.sub(r"[^\w\-]+", "_", file_path.stem).strip("_").lower() or "file"
        suggested_name = f"{category}_{timestamp}_{stem}"

        analysis = {
            "original_name": file_path.name,
            "extension": ext,
            "needs_conversion": needs_conversion,
            "target_extension": target_ext if needs_conversion else None,
            "suggested_name": suggested_name,
            "category": category,
            "actions": [],
        }
        if needs_conversion:
            analysis["actions"].append(f"convert_{ext.lstrip('.')}_to_{target_ext.lstrip('.')}")
        else:
            analysis["actions"].append("organize_only")
        logger.info("Analyzed %s -> category=%s, convert=%s",
                    file_path.name, category, analysis["target_extension"])
        return analysis


# ---------------------------------------------------------------------------
# Step 2: Convert
# ---------------------------------------------------------------------------
class FileConverter:
    @staticmethod
    def convert_txt_to_md(source_path: Path, dest_path: Path) -> bool:
        """Conservative TXT->MD: first non-empty line becomes # heading only if
        it looks like a title (short, no terminal punctuation). Rest is plain
        paragraphs; existing list markers preserved."""
        try:
            with open(source_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except Exception as e:
            logger.error("Read failed for %s: %s", source_path, e)
            return False

        md_lines = []
        title_done = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                md_lines.append("")
                continue
            if not title_done and len(stripped) <= 80 and not stripped[-1] in ".!?:;" \
                    and not stripped.startswith(("#", "-", "*", ">")):
                md_lines.append(f"# {stripped}")
                md_lines.append("")
                title_done = True
            else:
                md_lines.append(line)
            title_done = True  # only the very first line can be a title

        try:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines).strip() + "\n")
        except Exception as e:
            logger.error("Write MD failed: %s", e)
            return False
        logger.info("Converted TXT->MD: %s -> %s", source_path.name, dest_path.name)
        return True

    @staticmethod
    def convert_wav_to_mp3(source_path: Path, dest_path: Path, bitrate: str = "128k") -> bool:
        if not AUDIO_AVAILABLE:
            logger.warning("pydub not installed; skipping WAV->MP3 for %s", source_path.name)
            return False
        try:
            audio = AudioSegment.from_wav(str(source_path))
            audio.export(str(dest_path), format="mp3", bitrate=bitrate)
            logger.info("Converted WAV->MP3: %s -> %s (%s)", source_path.name, dest_path.name, bitrate)
            return True
        except Exception as e:
            logger.error("WAV->MP3 failed for %s: %s", source_path.name, e)
            return False


# ---------------------------------------------------------------------------
# Step 3: Organize (move, not copy)
# ---------------------------------------------------------------------------
class FileOrganizer:
    def __init__(self, organized_root: Path):
        self.organized_root = organized_root

    def category_dir(self, category: str) -> Path:
        return self.organized_root / CATEGORY_DIR.get(category, "Other")

    def place_file(self, source_file: Path, suggested_name: str, category: str) -> Path:
        target_dir = self.category_dir(category)
        target_dir.mkdir(parents=True, exist_ok=True)
        ext = source_file.suffix.lower()
        dest = target_dir / f"{suggested_name}{ext}"
        counter = 1
        while dest.exists():
            dest = target_dir / f"{suggested_name}_{counter}{ext}"
            counter += 1
        shutil.move(str(source_file), str(dest))
        logger.info("Organized: %s -> %s", source_file.name, dest)
        return dest


# ---------------------------------------------------------------------------
# Step 4: Git
# ---------------------------------------------------------------------------
class GitCommitManager:
    def __init__(self, repo_path: Path):
        self.repo = None
        if not GIT_AVAILABLE:
            logger.warning("GitPython not installed (pip install GitPython) — commits skipped")
            return
        try:
            if (repo_path / ".git").exists():
                self.repo = git.Repo(repo_path)
            else:
                self.repo = git.Repo.init(repo_path)
                (repo_path / ".gitignore").write_text(
                    "*.log\n.tmp_convert/\n__pycache__/\n*.pyc\nwatch_folder/\n",
                    encoding="utf-8",
                )
            logger.info("Git repo ready: %s", repo_path)
        except Exception as e:
            logger.error("Git init failed: %s", e)

    def commit_file(self, file_path: Path, message: str = "Auto-organized file") -> bool:
        if not self.repo:
            return False
        try:
            rel = str(file_path.relative_to(self.repo.working_dir))
            self.repo.index.add([rel])
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.repo.index.commit(f"{message}\n\nTimestamp: {ts}\nFile: {file_path.name}")
            logger.info("Committed: %s", file_path.name)
            return True
        except Exception as e:
            logger.error("Git commit failed for %s: %s", file_path.name, e)
            return False


# ---------------------------------------------------------------------------
# Step 5: Dashboard
# ---------------------------------------------------------------------------
class DashboardLogger:
    def __init__(self, dashboard_file: Path):
        self.dashboard_file = dashboard_file
        self.data = self._load()

    def _load(self) -> Dict:
        if self.dashboard_file.exists():
            try:
                with open(self.dashboard_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Dashboard unreadable, starting fresh: %s", e)
        return {"files_processed": [], "statistics": {}, "compliance_logs": []}

    def log(self, info: Dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "original_file": info.get("original_name"),
            "final_path": str(info.get("final_path")),
            "actions": info.get("actions", []),
            "category": info.get("category"),
            "status": "completed",
        }
        self.data["files_processed"].append(entry)
        if len(self.data["files_processed"]) > MAX_DASHBOARD_ENTRIES:
            self.data["files_processed"] = self.data["files_processed"][-MAX_DASHBOARD_ENTRIES:]
        self._update_stats(entry)
        self._check_compliance(entry)
        self._save()
        logger.info("Dashboard updated: %s", entry["original_file"])

    def _update_stats(self, entry: Dict):
        stats = self.data["statistics"]
        cat = entry["category"] or "other"
        if cat not in stats:
            stats[cat] = {"count": 0, "files": []}
        stats[cat]["count"] += 1
        stats[cat]["files"].append(entry["original_file"])
        stats["total_processed"] = len(self.data["files_processed"])
        stats["last_updated"] = entry["timestamp"]

    def _check_compliance(self, entry: Dict):
        checks = {
            "file_named": bool(entry["final_path"]),
            "categorized": bool(entry["category"]),
            "actions_documented": len(entry["actions"]) > 0,
        }
        self.data["compliance_logs"].append({
            "timestamp": entry["timestamp"],
            "file": entry["original_file"],
            "checks": checks,
            "compliant": all(checks.values()),
        })

    def _save(self):
        tmp = self.dashboard_file.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.dashboard_file)


# ---------------------------------------------------------------------------
# Event handler + worker queue
# ---------------------------------------------------------------------------
class FileWorkflowHandler(FileSystemEventHandler):
    def __init__(self, config: FileWorkflowConfig):
        self.config = config
        self.analyzer = FileRuleAnalyzer()
        self.converter = FileConverter()
        self.organizer = FileOrganizer(config.organized_root)
        self.git_manager = GitCommitManager(config.git_repo_path)
        self.dashboard = DashboardLogger(config.dashboard_log)
        self._q: "queue.Queue[Path]" = queue.Queue()
        self._seen: set = set()  # (path, size, mtime) dedupe
        self._lock = threading.Lock()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    # --- event entry points ---
    def on_created(self, event):
        if not event.is_directory:
            self._enqueue(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._enqueue(Path(event.dest_path))

    def _enqueue(self, path: Path):
        if path.suffix.lower() in TEMP_EXTENSIONS or path.name.startswith("."):
            return
        self._q.put(path)
        logger.info("Queued: %s", path.name)

    # --- background worker ---
    def _worker_loop(self):
        while True:
            path = self._q.get()
            try:
                if not self._wait_stable(path):
                    continue
                if not self._safe(path):
                    logger.warning("Skipped (outside watch dir / symlink escape): %s", path)
                    continue
                self.process_file(path)
            except Exception as e:
                logger.error("Processing failed for %s: %s", path, e, exc_info=True)
            finally:
                self._q.task_done()

    def _wait_stable(self, path: Path, timeout: float = 60.0) -> bool:
        """Wait until file size is stable (still being copied/downloaded)."""
        deadline = time.time() + timeout
        last_size = -1
        equal = 0
        while time.time() < deadline:
            try:
                size = path.stat().st_size
            except OSError:
                return False
            if size == last_size:
                equal += 1
                if equal >= STABILITY_POLLS and size > 0:
                    return True
            else:
                equal = 0
                last_size = size
            time.sleep(STABILITY_INTERVAL)
        logger.warning("File never stabilized, skipped: %s", path)
        return False

    def _safe(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
        except OSError:
            return False
        return str(resolved).startswith(str(self.config.watch_dir))

    def _dedupe(self, path: Path) -> bool:
        """Return True if already processed."""
        try:
            st = path.stat()
            key = (str(path.resolve()), st.st_size, int(st.st_mtime))
        except OSError:
            return True
        with self._lock:
            if key in self._seen:
                return True
            self._seen.add(key)
        return False

    def process_file(self, file_path: Path):
        if self._dedupe(file_path):
            logger.info("Duplicate, skipped: %s", file_path.name)
            return

        logger.info("Workflow start: %s", file_path.name)
        analysis = self.analyzer.analyze_file(file_path)
        working = file_path
        converted_ok = False

        # Step 2: convert into tmp dir
        if analysis["needs_conversion"]:
            tmp_out = self.config.tmp_dir / f"{analysis['suggested_name']}{analysis['target_extension']}"
            if analysis["target_extension"] == ".md":
                converted_ok = self.converter.convert_txt_to_md(file_path, tmp_out)
            elif analysis["target_extension"] == ".mp3":
                converted_ok = self.converter.convert_wav_to_mp3(file_path, tmp_out)
            if converted_ok:
                working = tmp_out
                analysis["actions"].append(f"converted_to_{analysis['target_extension'].lstrip('.')}")

        # Step 3: move into organized category dir
        organized_path = self.organizer.place_file(
            working, analysis["suggested_name"], analysis["category"]
        )
        analysis["final_path"] = organized_path

        # If converted, original source is still in watch dir -> remove it
        if converted_ok and file_path.exists() and file_path != working:
            try:
                file_path.unlink()
                analysis["actions"].append("original_removed")
            except OSError as e:
                logger.warning("Could not remove original %s: %s", file_path, e)

        # Step 4: git commit
        if self.git_manager.repo:
            self.git_manager.commit_file(organized_path)

        # Step 5: dashboard
        self.dashboard.log(analysis)
        logger.info("Workflow done: %s -> %s", file_path.name, organized_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def start_workflow(config: FileWorkflowConfig):
    handler = FileWorkflowHandler(config)
    observer = Observer()
    observer.schedule(handler, str(config.watch_dir), recursive=False)
    observer.start()
    logger.info("Workflow started. Watching: %s", config.watch_dir)
    logger.info("Output: %s | Git: %s | Press Ctrl+C to stop",
                config.output_dir, config.git_repo_path)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping…")
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(description="Automated file organization workflow")
    parser.add_argument("watch_dir", nargs="?", default="./watch_folder",
                        help="Directory to monitor (default: ./watch_folder)")
    parser.add_argument("-o", "--output", default="organized_output",
                        help="Output directory (default: organized_output)")
    parser.add_argument("--git-repo", default=None,
                        help="Git repo path (default: same as output dir)")
    args = parser.parse_args()

    print("=" * 60)
    print("Workflow จัดระเบียบไฟล์ - Automated File Management (v2)")
    print("=" * 60)
    print(f"  Watch : {args.watch_dir}")
    print(f"  Output: {args.output}")
    print(f"  Git   : {'enabled' if GIT_AVAILABLE else 'disabled (GitPython missing)'}")
    print(f"  Audio : {'enabled' if AUDIO_AVAILABLE else 'disabled (pydub missing)'}")
    print("  Steps: analyze -> convert -> organize -> commit -> dashboard")
    print("=" * 60)

    start_workflow(FileWorkflowConfig(args.watch_dir, args.output, args.git_repo))


if __name__ == "__main__":
    main()
