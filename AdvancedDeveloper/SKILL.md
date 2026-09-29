Advanced Developer

# Advanced Developer

สำหรับ Obsidian plugin ระดับ advanced ให้คิดว่า plugin เป็น application ขนาดเล็กที่มี lifecycle, state, UI surfaces, data indexes และ write-safety boundaries ของตัวเอง—not just a collection of commands. จุดสำคัญคือการควบคุม lifecycle ให้ถูกต้อง, ทำ UI แบบ reactive แต่ประหยัดทรัพยากร, และแยก editor extension ออกจาก vault-level logic อย่างชัดเจน.[1][2][3][4]

## Architecture

```text
Plugin
│
├── Domain services
│   ├── Vault queries
│   ├── Metadata indexes
│   ├── Validation
│   ├── Safe write operations
│   └── External-service client
│
├── Application layer
│   ├── Commands
│   ├── Event coordination
│   ├── State management
│   └── Background refresh
│
├── UI layer
│   ├── Settings tab
│   ├── Modals
│   ├── ItemView dashboards
│   ├── Status bar
│   └── Editor decorations/widgets
│
└── Infrastructure
    ├── Persistent settings
    ├── In-memory indexes
    ├── Logging
    └── Cleanup / lifecycle handling
```

A maintainable structure:

```text
src/
├── core/
│   ├── types.ts
│   ├── settings.ts
│   ├── logger.ts
│   ├── result.ts
│   └── validation.ts
├── services/
│   ├── note-index.ts
│   ├── metadata-query-service.ts
│   ├── vault-write-service.ts
│   └── agent-service.ts
├── commands/
│   └── register-commands.ts
├── views/
│   ├── dashboard-view.ts
│   └── inspector-view.ts
├── modals/
│   ├── confirm-modal.ts
│   └── diff-preview-modal.ts
├── editor/
│   ├── decorations.ts
│   ├── state-fields.ts
│   └── view-plugin.ts
└── ui/
    ├── renderers.ts
    └── components.ts
```

## Lifecycle management

ใช้ `registerEvent()`, `registerDomEvent()`, `registerInterval()` และ `register()` สำหรับทุก resource ที่มี lifecycle เพื่อให้ Obsidian cleanup เมื่อ plugin หรือ view ถูก unload. `Component`/`ItemView` รองรับ registration methods เหล่านี้โดยตรง.[2][3][4][5]

```ts
import {
  Notice,
  Plugin,
  TFile
} from 'obsidian';

export default class AdvancedPlugin extends Plugin {
  async onload(): Promise<void> {
    this.registerEvent(
      this.app.vault.on('modify', (file) => {
        if (file instanceof TFile && file.extension === 'md') {
          this.handleMarkdownChange(file);
        }
      })
    );

    this.registerInterval(
      window.setInterval(() => {
        this.refreshIfNeeded();
      }, 60_000)
    );

    this.app.workspace.onLayoutReady(() => {
      this.initializeWorkspaceFeatures();
    });
  }

  private handleMarkdownChange(file: TFile): void {
    console.debug('Modified:', file.path);
  }

  private refreshIfNeeded(): void {
    // Keep this lightweight.
  }

  private initializeWorkspaceFeatures(): void {
    new Notice('Workspace features ready.');
  }
}
```

### Avoid unmanaged listeners

```ts
// Avoid: listener may survive unload if not detached manually.
window.addEventListener('resize', this.handleResize);
```

```ts
// Prefer: auto-detached with plugin/view lifecycle.
this.registerDomEvent(
  window,
  'resize',
  this.handleResize.bind(this)
);
```

### Use cancellation for async UI work

เมื่อ user เปลี่ยน note, ปิด modal หรือ unload view ขณะ request ยังทำงานอยู่ ต้องป้องกัน stale response เขียนทับ UI ที่ใหม่กว่า

```ts
class RequestController {
  private currentRequestId = 0;

  async runLatest<T>(
    operation: () => Promise<T>
  ): Promise<T | null> {
    const requestId = ++this.currentRequestId;

    const result = await operation();

    if (requestId !== this.currentRequestId) {
      return null;
    }

    return result;
  }

  cancelPending(): void {
    this.currentRequestId++;
  }
}
```

```ts
class SearchViewController {
  private readonly requests = new RequestController();

  async search(query: string): Promise<void> {
    const result = await this.requests.runLatest(async () => {
      return this.performSearch(query);
    });

    if (!result) {
      return;
    }

    this.renderResults(result);
  }

  onunload(): void {
    this.requests.cancelPending();
  }

  private async performSearch(query: string): Promise<string[]> {
    return [query];
  }

  private renderResults(results: string[]): void {
    console.log(results);
  }
}
```

## Custom views

ใช้ `ItemView` สำหรับ sidebar, dashboard, inspector, review queue, graph panel หรือ agent activity panel ที่ต้องแสดงอยู่ต่อเนื่อง. `ItemView` ผูกกับ `WorkspaceLeaf` และ inherits lifecycle cleanup capabilities จาก `Component`.[3][6][7]

```ts
import {
  ItemView,
  WorkspaceLeaf
} from 'obsidian';

export const REVIEW_QUEUE_VIEW =
  'advanced-review-queue';

export class ReviewQueueView extends ItemView {
  constructor(
    leaf: WorkspaceLeaf,
    private readonly plugin: AdvancedPlugin
  ) {
    super(leaf);
  }

  getViewType(): string {
    return REVIEW_QUEUE_VIEW;
  }

  getDisplayText(): string {
    return 'Review Queue';
  }

  getIcon(): string {
    return 'list-checks';
  }

  async onOpen(): Promise<void> {
    this.registerEvent(
      this.app.metadataCache.on('changed', () => {
        void this.render();
      })
    );

    await this.render();
  }

  async onClose(): Promise<void> {
    this.contentEl.empty();
  }

  async render(): Promise<void> {
    const { contentEl } = this;

    contentEl.empty();
    contentEl.addClass('advanced-review-queue');

    contentEl.createEl('h2', {
      text: 'Notes Needing Review'
    });

    const notes = this.app.vault
      .getMarkdownFiles()
      .filter((file) => {
        const frontmatter = this.app.metadataCache
          .getFileCache(file)
          ?.frontmatter;

        return (
          frontmatter?.status === 'in-review' &&
          frontmatter?.reviewed === false
        );
      })
      .slice(0, 50);

    if (notes.length === 0) {
      contentEl.createEl('p', {
        text: 'No notes need review.',
        cls: 'advanced-muted'
      });

      return;
    }

    const listEl = contentEl.createEl('ul', {
      cls: 'advanced-note-list'
    });

    for (const file of notes) {
      const itemEl = listEl.createEl('li');

      const buttonEl = itemEl.createEl('button', {
        text: file.basename,
        cls: 'advanced-note-button'
      });

      this.registerDomEvent(
        buttonEl,
        'click',
        async () => {
          const leaf = this.app.workspace.getLeaf(false);

          await leaf.openFile(file);
        }
      );

      itemEl.createEl('small', {
        text: file.path,
        cls: 'advanced-muted'
      });
    }
  }
}
```

### Register and activate a view

```ts
async onload(): Promise<void> {
  this.registerView(
    REVIEW_QUEUE_VIEW,
    (leaf) => new ReviewQueueView(leaf, this)
  );

  this.addCommand({
    id: 'open-review-queue',
    name: 'Open review queue',
    callback: async () => {
      await this.activateReviewQueue();
    }
  });
}

async activateReviewQueue(): Promise<void> {
  const existingLeaf = this.app.workspace
    .getLeavesOfType(REVIEW_QUEUE_VIEW)[0];

  const leaf =
    existingLeaf ??
    this.app.workspace.getRightLeaf(false);

  if (!leaf) {
    return;
  }

  await leaf.setViewState({
    type: REVIEW_QUEUE_VIEW,
    active: true
  });

  this.app.workspace.revealLeaf(leaf);
}
```

Avoid relying on `workspace.activeLeaf` without a null check; Obsidian’s API reference explicitly cautions against using it directly.[8]

## Vault indexes

การ scan vault ทุกครั้งที่ user พิมพ์หรือเปิด panel ไม่ scale สำหรับ vault ใหญ่ ให้สร้าง index ใน memory แล้ว update เฉพาะ file ที่เปลี่ยน

```ts
import {
  App,
  TFile
} from 'obsidian';

export interface NoteIndexEntry {
  path: string;
  title: string;
  tags: string[];
  status?: string;
  noteType?: string;
  updated?: string;
}

export class NoteIndex {
  private readonly records = new Map<
    string,
    NoteIndexEntry
  >();

  constructor(private readonly app: App) {}

  rebuild(): void {
    this.records.clear();

    for (const file of this.app.vault.getMarkdownFiles()) {
      this.update(file);
    }
  }

  update(file: TFile): void {
    const frontmatter = this.app.metadataCache
      .getFileCache(file)
      ?.frontmatter ?? {};

    const tags = normalizeStringArray(frontmatter.tags);

    this.records.set(file.path, {
      path: file.path,
      title:
        typeof frontmatter.title === 'string'
          ? frontmatter.title
          : file.basename,
      tags,
      status:
        typeof frontmatter.status === 'string'
          ? frontmatter.status
          : undefined,
      noteType:
        typeof frontmatter.note_type === 'string'
          ? frontmatter.note_type
          : undefined,
      updated:
        typeof frontmatter.updated === 'string'
          ? frontmatter.updated
          : undefined
    });
  }

  remove(path: string): void {
    this.records.delete(path);
  }

  findByTag(tag: string): NoteIndexEntry[] {
    const normalized = tag.replace(/^#/, '')
      .trim()
      .toLowerCase();

    return [...this.records.values()]
      .filter((record) =>
        record.tags.some(
          (item) => item.toLowerCase() === normalized
        )
      );
  }

  findByStatus(status: string): NoteIndexEntry[] {
    return [...this.records.values()]
      .filter(
        (record) => record.status === status
      );
  }
}

function normalizeStringArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .filter((item): item is string =>
        typeof item === 'string'
      )
      .map((item) =>
        item.replace(/^#/, '').trim()
      )
      .filter(Boolean);
  }

  if (typeof value === 'string') {
    return [value.replace(/^#/, '').trim()]
      .filter(Boolean);
  }

  return [];
}
```

### Lifecycle-aware index updates

```ts
private readonly noteIndex = new NoteIndex(this.app);

async onload(): Promise<void> {
  this.app.workspace.onLayoutReady(() => {
    this.noteIndex.rebuild();
  });

  this.registerEvent(
    this.app.metadataCache.on('changed', (file) => {
      if (file.extension === 'md') {
        this.noteIndex.update(file);
      }
    })
  );

  this.registerEvent(
    this.app.vault.on('delete', (file) => {
      this.noteIndex.remove(file.path);
    })
  );

  this.registerEvent(
    this.app.vault.on('rename', (file, oldPath) => {
      this.noteIndex.remove(oldPath);

      if (file instanceof TFile && file.extension === 'md') {
        this.noteIndex.update(file);
      }
    })
  );
}
```

> [!tip]
> Rebuild index only after metadata becomes available; thereafter use incremental updates. `MetadataCache` is ideal for summaries, while full Markdown reads should happen only on demand.

## Editor extensions

ใช้ `Editor` API สำหรับ action ทั่วไป เช่น read selection, insert text และ replace range. ใช้ CodeMirror 6 เมื่อ feature ต้อง interact กับ editor viewport, decorations, widgets, transactions หรือ custom state. Obsidian documents view plugins as CodeMirror editor extensions that run after the viewport has been recomputed.[9][10][11]

### Editor command

```ts
this.addCommand({
  id: 'convert-selection-to-callout',
  name: 'Convert selection to info callout',
  editorCallback: (editor) => {
    const selected = editor.getSelection().trim();

    if (!selected) {
      return;
    }

    editor.replaceSelection(
      `> [!info]\n> ${selected.replace(/\n/g, '\n> ')}`
    );
  }
});
```

### CodeMirror view plugin lifecycle

```ts
import {
  ViewPlugin,
  ViewUpdate,
  EditorView
} from '@codemirror/view';

class SelectionTracker {
  constructor(
    private readonly view: EditorView
  ) {
    this.reportSelection();
  }

  update(update: ViewUpdate): void {
    if (
      update.selectionSet ||
      update.docChanged
    ) {
      this.reportSelection();
    }
  }

  destroy(): void {
    // Remove external subscriptions or cleanup local state here.
  }

  private reportSelection(): void {
    const selection = this.view.state.selection.main;

    console.debug({
      from: selection.from,
      to: selection.to
    });
  }
}

export const selectionTrackerExtension =
  ViewPlugin.fromClass(SelectionTracker);
```

```ts
this.registerEditorExtension(
  selectionTrackerExtension
);
```

A CodeMirror view plugin typically has `constructor()`, `update()`, and `destroy()` lifecycle methods. It can access the recomputed editor viewport, but should not make changes that affect that viewport from inside the view plugin lifecycle.[10]

### State fields and transactions

ใช้ `StateField` เมื่อ state ต้องอยู่ใน history model ของ editor และควร update ผ่าน transaction

```ts
import {
  StateEffect,
  StateField
} from '@codemirror/state';

interface ReviewState {
  enabled: boolean;
}

const setReviewMode = StateEffect.define<boolean>();

export const reviewModeField =
  StateField.define<ReviewState>({
    create(): ReviewState {
      return {
        enabled: false
      };
    },

    update(value, transaction): ReviewState {
      for (const effect of transaction.effects) {
        if (effect.is(setReviewMode)) {
          return {
            enabled: effect.value
          };
        }
      }

      return value;
    }
  });
```

CodeMirror state is transaction-based so undo/redo and editor changes can be managed consistently; update state through effects and transactions instead of ad hoc mutable global variables.[11]

## Safe concurrent writes

สำหรับ agent workflows หรือ plugin ที่มี async operation นาน ให้ป้องกัน lost updates ด้วย compare-and-write pattern

```ts
import { TFile } from 'obsidian';

async function applyProposal(
  app: App,
  file: TFile,
  expectedContent: string,
  proposedContent: string
): Promise<void> {
  await app.vault.process(file, (current) => {
    if (current !== expectedContent) {
      throw new Error(
        'File changed after the proposal was generated.'
      );
    }

    return proposedContent;
  });
}
```

### Frontmatter updates

```ts
async function updateReviewStatus(
  app: App,
  file: TFile
): Promise<void> {
  await app.fileManager.processFrontMatter(
    file,
    (frontmatter) => {
      frontmatter.status = 'in-review';
      frontmatter.reviewed = false;
      frontmatter.updated = new Date()
        .toISOString()
        .slice(0, 10);
    }
  );
}
```

Recommended write policy:

```text
Read metadata/content
→ Calculate proposal
→ Render diff
→ User confirms
→ Verify target still valid
→ Use Vault.process() / processFrontMatter()
→ Refresh UI/index
→ Record metadata-only audit event
```

## Error handling

ใช้ typed result object สำหรับ domain/service layer เพื่อไม่ให้ UI ต้อง parse arbitrary exception ทุกจุด

```ts
export type Result<T> =
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      code:
        | 'NOT_FOUND'
        | 'NOT_ALLOWED'
        | 'CONFLICT'
        | 'INVALID_INPUT'
        | 'UNKNOWN';
      message: string;
    };

export function success<T>(value: T): Result<T> {
  return {
    ok: true,
    value
  };
}

export function failure(
  code: Extract<Result<never>, { ok: false }>['code'],
  message: string
): Result<never> {
  return {
    ok: false,
    code,
    message
  };
}
```

```ts
async function getMarkdownFile(
  app: App,
  path: string
): Promise<Result<TFile>> {
  const abstractFile = app.vault.getAbstractFileByPath(path);

  if (!(abstractFile instanceof TFile)) {
    return failure(
      'NOT_FOUND',
      `Markdown file not found: ${path}`
    );
  }

  if (abstractFile.extension !== 'md') {
    return failure(
      'INVALID_INPUT',
      'Target must be a Markdown file.'
    );
  }

  return success(abstractFile);
}
```

UI code:

```ts
const result = await getMarkdownFile(
  this.app,
  requestedPath
);

if (!result.ok) {
  new Notice(result.message);
  return;
}

const file = result.value;
```

## Advanced review checklist

```text
Architecture
[ ] UI code does not directly own complex vault logic
[ ] main.ts registers features but remains thin
[ ] Services have focused responsibilities
[ ] Shared types and validation live outside views

Lifecycle
[ ] Every Obsidian event uses registerEvent()
[ ] Every DOM listener uses registerDomEvent() where applicable
[ ] Timers use registerInterval()
[ ] Async work is cancelable or stale-result safe
[ ] Views clear UI on onClose()

Performance
[ ] No full-vault scan per keystroke
[ ] MetadataCache is used for note summaries
[ ] Expensive scans are scoped, debounced and capped
[ ] Indexes update incrementally
[ ] Editor extensions do not call network or scan vault in update()

Views
[ ] ItemView uses a unique view type
[ ] View refreshes only when relevant data changes
[ ] Rendering uses createEl()/setText(), not innerHTML
[ ] Long lists have limits, pagination or virtualization
[ ] UI works in narrow sidebars and both themes

Writes
[ ] All destructive changes require confirmation
[ ] Proposed changes show a preview/diff
[ ] Content writes use Vault.process()
[ ] Frontmatter writes use processFrontMatter()
[ ] Agent-generated changes default to draft-first
[ ] Conflicts do not overwrite user edits

Security
[ ] No API key or secret in plugin bundle/settings
[ ] Note and AI content are treated as untrusted
[ ] External requests are explicit and disclosed
[ ] Metadata-only logs avoid note bodies and secrets
[ ] Path and scope validation occur before every write
```

## Related notes

- [[Obsidian & Frontend Development]]
- [[Best Practices]]
- [[innerHTML ใน Obsidian Plugins]]
- [[ตัวอย่างโค้ด TypeScript สำหรับเชื่อมต่อ AI Agent กับ Obsidian Plugin API]]
- [[การดึงรายการไฟล์ทั้งหมดที่มีแท็กหรือ Metadata เฉพาะใน Obsidian Vault]]
- [[การดึง Metadata และ Frontmatter ผ่าน Obsidian MetadataCache API]]

การอ้างอิง:
[1] Plugin - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/Plugin
[2] EditableFileView - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/EditableFileView
[3] ItemView - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/ItemView
[4] Component - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Component
[5] registerEvent - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Component/registerEvent
[6] WorkspaceLeaf - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/WorkspaceLeaf
[7] (constructor) - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/ItemView/(constructor)
[8] Workspace - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/Workspace
[9] Editor https://docs.obsidian.md/Plugins/Editor/Editor
[10] View plugins - Developer Documentation https://docs.obsidian.md/Plugins/Editor/View+plugins
[11] State management - Developer Documentation https://docs.obsidian.md/Plugins/Editor/State+management
[12] sitemap.xml https://docs.obsidian.md/sitemap.xml
[13] Plugin guidelines - Developer Documentation https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
[14] index - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/index
[15] Communicating with editor extensions https://docs.obsidian.md/Plugins/Editor/Communicating+with+editor+extensions
