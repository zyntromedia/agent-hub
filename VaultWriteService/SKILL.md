การเขียน Vault Write Service ให้ปลอดภัยจาก Race Condition

# การเขียน Vault Write Service ให้ปลอดภัยจาก Race Condition

ใช้ `Vault.process()` สำหรับการแก้ Markdown body และ `FileManager.processFrontMatter()` สำหรับการแก้ YAML frontmatter เพราะทั้งสอง API ทำ atomic read-modify-write ภายใน Obsidian. หลีกเลี่ยง pattern `read() → await งานนาน → modify()` เพราะ user หรือ plugin อื่นอาจแก้ไฟล์ระหว่างนั้นและทำให้ข้อมูลหายได้.[1][2][3]

## ปัญหา Race Condition

Race condition เกิดเมื่อหลาย operation อ่านและเขียนไฟล์เดียวกันในช่วงเวลาใกล้กัน โดยแต่ละ operation คิดว่าข้อมูลที่อ่านมาเป็นข้อมูลล่าสุด

```text
Initial file content:

# Project
Status: Draft
```

```text
Operation A                     Operation B
───────────                     ───────────
read file
→ "Status: Draft"

                                read file
                                → "Status: Draft"

wait for AI response

                                modify file
                                → "Status: In Review"

modify file
→ "Status: Active"

Final result:
"Status: Active"

Problem:
Operation B's change is lost.
```

### Unsafe pattern

```ts
import {
  App,
  TFile
} from 'obsidian';

async function appendUnsafe(
  app: App,
  file: TFile,
  section: string
): Promise<void> {
  const currentContent = await app.vault.read(file);

  // ระหว่าง await นี้ user หรือ plugin อื่นอาจแก้ file ได้
  await new Promise((resolve) => {
    window.setTimeout(resolve, 1_000);
  });

  const nextContent = [
    currentContent.trimEnd(),
    '',
    section
  ].join('\n');

  await app.vault.modify(file, nextContent);
}
```

`Vault.modify()` เขียน content ที่ส่งเข้าไปโดยตรง จึงไม่เหมาะกับกรณีที่ new content คำนวณจาก content เก่าซึ่งอาจเปลี่ยนไปแล้ว. Obsidian ระบุให้ใช้ `Vault.process()` แทน `read()`/`modify()` เมื่อแก้ไฟล์ตามเนื้อหาปัจจุบัน เพื่อหลีกเลี่ยง unintended data loss.[1][3]

***

## หลักการออกแบบ

```text
Read-only operation
→ cachedRead() / read()

Synchronous content transformation
→ vault.process()

Synchronous frontmatter mutation
→ fileManager.processFrontMatter()

Async computation, AI request, network call
→ read snapshot
→ perform async work
→ process() at write time
→ compare snapshot / apply safe merge / abort on conflict

Multiple writes in same plugin
→ per-file queue or mutex
→ process() inside queue

Create / rename / move / delete
→ resolve target first
→ validate path
→ explicit confirmation
→ operation-specific policy
```

> [!important]
> `Vault.process()` callback ต้องเป็น synchronous function: รับ `current` แล้วคืน content ใหม่ทันที  
> ห้าม `await` network request, AI request หรือ database call ภายใน callback. สำหรับ async workflow ให้ทำงาน async ก่อน แล้วใช้ `process()` ในขั้น write สุดท้าย.[1][3]

***

## Vault Write Service

โครงสร้าง service ที่เหมาะสม:

```text
src/
├── services/
│   ├── vault-write-service.ts
│   ├── write-queue.ts
│   └── path-policy.ts
├── modals/
│   └── diff-preview-modal.ts
└── core/
    ├── result.ts
    └── types.ts
```

```text
UI / Command / Agent
        │
        ▼
Validate request
        │
        ▼
Resolve TFile
        │
        ▼
Generate proposal
        │
        ├── AI / network / long-running logic
        │
        ▼
Show preview and ask confirmation
        │
        ▼
VaultWriteService
        │
        ├── Per-file queue
        ├── Vault.process()
        ├── processFrontMatter()
        └── Conflict detection
        │
        ▼
Refresh UI / metadata index / audit event
```

***

## Result Type

สร้าง result type เพื่อให้ UI ไม่ต้องจับ exception แบบกระจัดกระจาย

```ts
export type WriteErrorCode =
  | 'NOT_FOUND'
  | 'NOT_MARKDOWN'
  | 'PATH_DENIED'
  | 'CONFLICT'
  | 'INVALID_INPUT'
  | 'WRITE_FAILED';

export type WriteResult<T> =
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      code: WriteErrorCode;
      message: string;
    };

export function writeSuccess<T>(
  value: T
): WriteResult<T> {
  return {
    ok: true,
    value
  };
}

export function writeFailure(
  code: WriteErrorCode,
  message: string
): WriteResult<never> {
  return {
    ok: false,
    code,
    message
  };
}
```

***

## Per-file Write Queue

`Vault.process()` ป้องกัน race ระหว่างการอ่านและเขียน **ต่อหนึ่ง atomic operation** แต่ service ที่มีหลาย request พร้อมกัน—เช่น UI, command, agent, background refresh หรือ external integration—ควร serialize writes ต่อไฟล์ด้วย queue เพิ่มเติม เพื่อให้ behavior predictable และเพื่อลด conflict ใน plugin ของตนเอง. แนวคิดของ process-wide/per-file mutex ถูกใช้ใน integrations ที่มี concurrent vault writes ด้วยเช่นกัน.[4]

```ts
export class PerFileWriteQueue {
  private readonly queues = new Map<
    string,
    Promise<void>
  >();

  async run<T>(
    filePath: string,
    operation: () => Promise<T>
  ): Promise<T> {
    const previous = this.queues.get(filePath) ?? Promise.resolve();

    let releaseCurrent!: () => void;

    const current = new Promise<void>((resolve) => {
      releaseCurrent = resolve;
    });

    const chain = previous
      .catch(() => undefined)
      .then(() => current);

    this.queues.set(filePath, chain);

    await previous.catch(() => undefined);

    try {
      return await operation();
    } finally {
      releaseCurrent();

      if (this.queues.get(filePath) === chain) {
        this.queues.delete(filePath);
      }
    }
  }
}
```

### Why per-file, not global queue?

```text
Global queue
→ File A must wait while File B is written
→ Unnecessary slowdown

Per-file queue
→ Writes to the same file are serialized
→ Writes to different files can run in parallel
```

| Scenario | Per-file queue behavior |
|---|---|
| Two writes to `Project.md` | Run one after another |
| One write to `Project.md`, one to `Daily.md` | Can run concurrently |
| Ten agent proposals for same file | Serialized deterministically |
| User edits file manually | `process()` gets current file body at write time |

***

## Safe Content Update Service

```ts
import {
  App,
  TFile
} from 'obsidian';

import {
  WriteResult,
  writeFailure,
  writeSuccess
} from '../core/result';

import { PerFileWriteQueue } from './write-queue';

export interface ContentUpdateRequest {
  file: TFile;
  expectedContent?: string;
  transform: (currentContent: string) => string;
}

export class VaultWriteService {
  private readonly queue = new PerFileWriteQueue();

  constructor(private readonly app: App) {}

  async updateContent(
    request: ContentUpdateRequest
  ): Promise<WriteResult<string>> {
    const { file, expectedContent, transform } = request;

    if (file.extension !== 'md') {
      return writeFailure(
        'NOT_MARKDOWN',
        'Only Markdown files can be updated.'
      );
    }

    try {
      const writtenContent = await this.queue.run(
        file.path,
        async () => {
          return this.app.vault.process(
            file,
            (currentContent) => {
              if (
                expectedContent !== undefined &&
                currentContent !== expectedContent
              ) {
                throw new WriteConflictError(
                  'The file changed after the proposal was created.'
                );
              }

              const nextContent = transform(currentContent);

              if (typeof nextContent !== 'string') {
                throw new Error(
                  'Content transform must return a string.'
                );
              }

              return nextContent;
            }
          );
        }
      );

      return writeSuccess(writtenContent);
    } catch (error) {
      if (error instanceof WriteConflictError) {
        return writeFailure(
          'CONFLICT',
          error.message
        );
      }

      console.error('Vault write failed.', error);

      return writeFailure(
        'WRITE_FAILED',
        'Could not update the note.'
      );
    }
  }
}

export class WriteConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'WriteConflictError';
  }
}
```

### Append a Section Safely

```ts
async function appendReviewSection(
  writeService: VaultWriteService,
  file: TFile
): Promise<void> {
  const result = await writeService.updateContent({
    file,
    transform: (currentContent) => {
      if (currentContent.includes('## Review')) {
        return currentContent;
      }

      return [
        currentContent.trimEnd(),
        '',
        '## Review',
        '',
        '- [ ] Review this note.',
        ''
      ].join('\n');
    }
  });

  if (!result.ok) {
    throw new Error(result.message);
  }
}
```

ผลลัพธ์:

```text
Current latest content
→ re-read atomically by Vault.process()
→ transform current value
→ write result atomically
```

จึงไม่ใช้ snapshot เก่ามาเขียนทับ user edits โดยไม่ตั้งใจ

***

## Optimistic Concurrency Control

สำหรับ workflow ที่มี async gap เช่น AI สร้าง proposal, user เปิด preview modal นาน หรือ user ใช้ editor แก้ note ระหว่างนั้น ให้เก็บ `expectedContent` ตอนสร้าง proposal แล้วตรวจอีกครั้งตอน write

```text
1. Read snapshot
2. Generate proposal asynchronously
3. User reviews preview
4. process() receives latest content
5. Compare latest content with snapshot
6. If different:
   - abort
   - show conflict
   - regenerate proposal
```

### Proposal Type

```ts
import { TFile } from 'obsidian';

export interface WriteProposal {
  file: TFile;
  originalContent: string;
  proposedContent: string;
  createdAt: number;
}
```

### Create Proposal

```ts
async function createProposal(
  app: App,
  file: TFile
): Promise<WriteProposal> {
  const originalContent = await app.vault.cachedRead(file);

  const proposedContent = [
    originalContent.trimEnd(),
    '',
    '## Agent Review',
    '',
    '> [!info]',
    '> Review generated after explicit approval.',
    '',
    '- [ ] Validate this section.'
  ].join('\n');

  return {
    file,
    originalContent,
    proposedContent,
    createdAt: Date.now()
  };
}
```

### Apply Proposal Only If Unchanged

```ts
async function applyProposal(
  writeService: VaultWriteService,
  proposal: WriteProposal
): Promise<WriteResult<string>> {
  return writeService.updateContent({
    file: proposal.file,
    expectedContent: proposal.originalContent,
    transform: () => proposal.proposedContent
  });
}
```

If the file changed after the proposal was made:

```text
Expected:
# Project
Status: Draft

Current:
# Project
Status: Draft
Owner: Alice

Result:
CONFLICT
```

แนะนำ UI response:

```text
This note changed while the proposal was open.

Options:
- Regenerate proposal from the latest note
- View current note
- Cancel
```

> [!warning]
> อย่าแก้ conflict ด้วยการเขียน `proposedContent` ทับ current content ทันที เพราะ proposal ถูกสร้างจาก document version เก่าและอาจลบ user edits

***

## Async Agent Workflow

### Incorrect

```ts
await app.vault.process(file, async (current) => {
  const aiResponse = await callAi(current);

  return aiResponse;
});
```

ปัญหา:

- `process()` callback ต้อง synchronous
- AI call อาจใช้เวลาหลายวินาที
- Lock/transaction ไม่ควรถูกถือไว้ระหว่าง network request
- TypeScript/API contract ไม่รองรับ callback ที่ return `Promise<string>`

### Correct

```ts
async function generateAndApplyAgentProposal(
  app: App,
  writeService: VaultWriteService,
  file: TFile,
  callAi: (content: string) => Promise<string>
): Promise<WriteResult<string>> {
  const snapshot = await app.vault.cachedRead(file);

  const proposal = await callAi(snapshot);

  return writeService.updateContent({
    file,
    expectedContent: snapshot,
    transform: () => proposal
  });
}
```

### Recommended AI Flow

```text
Read snapshot
        │
        ▼
Send only approved/minimized content to backend
        │
        ▼
Receive structured proposal
        │
        ▼
Validate proposal
        │
        ▼
Show diff preview
        │
        ▼
User confirms
        │
        ▼
Vault.process()
        │
        ├── File unchanged → write
        └── File changed → conflict, regenerate
```

***

## Safe Frontmatter Service

`FileManager.processFrontMatter()` atomically reads, mutates and saves a Markdown file’s frontmatter. Callback ต้อง mutate frontmatter object แบบ synchronous และต้อง handle errors เช่น YAML parse error.[2]

```ts
import {
  App,
  TFile
} from 'obsidian';

import {
  WriteResult,
  writeFailure,
  writeSuccess
} from '../core/result';

export class FrontmatterWriteService {
  private readonly queue = new PerFileWriteQueue();

  constructor(private readonly app: App) {}

  async update(
    file: TFile,
    mutate: (frontmatter: Record<string, unknown>) => void
  ): Promise<WriteResult<void>> {
    if (file.extension !== 'md') {
      return writeFailure(
        'NOT_MARKDOWN',
        'Frontmatter can only be updated in Markdown files.'
      );
    }

    try {
      await this.queue.run(file.path, async () => {
        await this.app.fileManager.processFrontMatter(
          file,
          (frontmatter) => {
            mutate(frontmatter as Record<string, unknown>);
          }
        );
      });

      return writeSuccess(undefined);
    } catch (error) {
      console.error('Frontmatter write failed.', error);

      return writeFailure(
        'WRITE_FAILED',
        'Could not update note properties.'
      );
    }
  }
}
```

### Idempotent Frontmatter Mutation

การ update ควร idempotent เพื่อให้ retry ไม่สร้าง duplicate values

```ts
function normalizeStringArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .filter((item): item is string =>
        typeof item === 'string'
      )
      .map((item) => item.trim())
      .filter(Boolean);
  }

  if (typeof value === 'string' && value.trim()) {
    return [value.trim()];
  }

  return [];
}

function addUniqueTag(
  frontmatter: Record<string, unknown>,
  tag: string
): void {
  const normalized = tag
    .replace(/^#/, '')
    .trim();

  if (!normalized) {
    return;
  }

  const currentTags = normalizeStringArray(
    frontmatter.tags
  );

  const alreadyExists = currentTags.some(
    (currentTag) =>
      currentTag.toLowerCase() === normalized.toLowerCase()
  );

  frontmatter.tags = alreadyExists
    ? currentTags
    : [...currentTags, normalized];
}
```

Usage:

```ts
const frontmatterService =
  new FrontmatterWriteService(this.app);

const result = await frontmatterService.update(
  file,
  (frontmatter) => {
    addUniqueTag(frontmatter, 'reviewed');

    frontmatter.status = 'in-review';
    frontmatter.reviewed = false;
    frontmatter.updated = new Date()
      .toISOString()
      .slice(0, 10);
  }
);
```

***

## One Queue for Content and Frontmatter

หาก plugin มีทั้ง body write และ frontmatter write ให้ **share queue instance เดียว** ระหว่าง services เพื่อ serialize writes ที่ target file เดียวกัน

```ts
export class VaultMutationService {
  private readonly queue = new PerFileWriteQueue();

  constructor(private readonly app: App) {}

  async updateContent(
    file: TFile,
    transform: (current: string) => string
  ): Promise<string> {
    return this.queue.run(file.path, async () => {
      return this.app.vault.process(file, transform);
    });
  }

  async updateFrontmatter(
    file: TFile,
    mutate: (frontmatter: Record<string, unknown>) => void
  ): Promise<void> {
    await this.queue.run(file.path, async () => {
      await this.app.fileManager.processFrontMatter(
        file,
        (frontmatter) => {
          mutate(frontmatter as Record<string, unknown>);
        }
      );
    });
  }
}
```

```text
Without shared queue:

Content write ────────┐
                      ├── Same file
Frontmatter write ────┘
                      ↓
Potential ordering ambiguity

With shared queue:

Content write
        ↓
Frontmatter write
        ↓
Predictable serialized writes
```

> [!important]
> `processFrontMatter()` และ `Vault.process()` เป็น atomic ต่อ operation แต่หาก plugin ต้องรักษา invariant ข้ามหลาย operation เช่น “เพิ่ม section แล้ว update `status` พร้อมกัน” ให้รวม operation ให้มากที่สุด หรือ serialize ทั้ง sequence ผ่าน shared per-file queue

***

## Multi-step Transaction Limitation

Obsidian ไม่มี public multi-file transaction ที่สามารถ commit/rollback หลายไฟล์แบบ ACID transaction ในครั้งเดียวได้ ดังนั้น operation ข้ามหลาย notes ต้องออกแบบเป็น saga-like workflow

```text
Create report file
        │
        ▼
Update source note
        │
        ▼
Update index note
        │
        ▼
If a later step fails:
- Record failure
- Offer retry
- Offer compensating action
- Do not silently claim success
```

### Example: Multi-file Batch Result

```ts
interface BatchWriteResult {
  succeeded: string[];
  failed: Array<{
    path: string;
    message: string;
  }>;
}
```

```ts
async function addTagToFiles(
  service: VaultMutationService,
  files: TFile[],
  tag: string
): Promise<BatchWriteResult> {
  const result: BatchWriteResult = {
    succeeded: [],
    failed: []
  };

  for (const file of files) {
    try {
      await service.updateFrontmatter(
        file,
        (frontmatter) => {
          addUniqueTag(frontmatter, tag);
        }
      );

      result.succeeded.push(file.path);
    } catch (error) {
      result.failed.push({
        path: file.path,
        message:
          error instanceof Error
            ? error.message
            : 'Unknown write error.'
      });
    }
  }

  return result;
}
```

> [!warning]
> ก่อน bulk update ให้แสดง:
>
> - จำนวนไฟล์ที่กระทบ
> - paths หรือ sample paths
> - property/content ที่จะเปลี่ยน
> - dry-run result
> - confirmation
> - failure report หลังรัน

***

## Path and Target Validation

ทุก write operation ควร verify target ก่อนเขียน

```ts
import {
  App,
  TFile,
  normalizePath
} from 'obsidian';

function isAllowedPath(path: string): boolean {
  const normalized = normalizePath(path);

  const allowedRoots = [
    '00 Inbox/',
    '02 Projects/',
    '03 Areas/'
  ];

  const deniedFragments = [
    '.obsidian/',
    '.git/',
    '.env',
    'secrets/',
    'credentials/'
  ];

  return (
    allowedRoots.some((root) =>
      normalized.startsWith(root)
    ) &&
    !deniedFragments.some((fragment) =>
      normalized.includes(fragment)
    )
  );
}

function validateWritableFile(
  app: App,
  file: TFile
): WriteResult<TFile> {
  if (file.extension !== 'md') {
    return writeFailure(
      'NOT_MARKDOWN',
      'Only Markdown files are supported.'
    );
  }

  if (!isAllowedPath(file.path)) {
    return writeFailure(
      'PATH_DENIED',
      'The target path is outside the approved write scope.'
    );
  }

  const latest = app.vault.getFileByPath(file.path);

  if (!latest) {
    return writeFailure(
      'NOT_FOUND',
      'The target file no longer exists.'
    );
  }

  return writeSuccess(latest);
}
```

***

## Audit Without Sensitive Content

บันทึกเฉพาะ metadata ของ operation—not full note content, prompt, AI response หรือ secrets

```ts
interface WriteAuditEvent {
  timestamp: string;
  operation: string;
  path: string;
  result: 'success' | 'conflict' | 'failed';
  reason: string;
}
```

```ts
function toAuditLine(event: WriteAuditEvent): string {
  return [
    event.timestamp,
    event.operation,
    event.path,
    event.result,
    event.reason.replace(/\|/g, '\\|')
  ].join(' | ');
}
```

Good:

```text
2026-09-29T08:30:00.000Z | update_frontmatter | 03 Areas/Security/Review.md | success | user confirmed
```

Avoid:

```text
2026-09-29 | AI prompt | entire note body and provider output
```

***

## Test Scenarios

```text
Content safety
[ ] Two append operations on same file do not lose either append
[ ] A stale proposal fails with CONFLICT
[ ] Transform callback returns latest content plus intended change
[ ] Transform callback is synchronous
[ ] Empty/no-op transformations remain valid

Frontmatter safety
[ ] Two tag additions do not duplicate tags
[ ] Unrelated frontmatter properties remain unchanged
[ ] Invalid YAML produces handled error
[ ] Boolean/string/list type variations are normalized

Queue behavior
[ ] Writes to same path run in request order
[ ] Writes to different paths may run concurrently
[ ] Failed first operation does not block next operation
[ ] Queue entry is removed after completion
[ ] Content and frontmatter share one queue

Path safety
[ ] .obsidian/ is denied
[ ] .env is denied
[ ] Path traversal is denied
[ ] Deleted file produces NOT_FOUND
[ ] Non-Markdown file produces NOT_MARKDOWN

User experience
[ ] User sees diff before content update
[ ] User sees explicit confirmation before write
[ ] Conflict message offers regenerate/retry
[ ] Batch result lists succeeded and failed files
[ ] Audit log has no sensitive note content
```

## Summary

```text
Safe single-file update:
Vault.process(file, current => transform(current))

Safe frontmatter update:
FileManager.processFrontMatter(file, fm => mutate(fm))

Safe async proposal:
cachedRead snapshot
→ async work
→ preview
→ user confirmation
→ Vault.process()
→ compare current to snapshot
→ write or return conflict

Safe concurrent plugin writes:
Shared per-file queue
→ Vault.process() / processFrontMatter()
→ metadata-only audit
```

`Vault.process()` atomically reads, modifies and saves content, guaranteeing the file does not change between the read and write portion of that operation; `processFrontMatter()` offers the corresponding atomic mutation pattern for frontmatter. Use them as the core of a Vault Write Service, then add per-file serialization, optimistic conflict detection, validation, confirmation and audited outcomes around them.[1][2][3]

การอ้างอิง:
[1] Vault https://docs.obsidian.md/Plugins/Vault
[2] processFrontMatter - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/FileManager/processFrontMatter
[3] process - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Vault/process
[4] Protocol https://community.obsidian.md/plugins/mcp-tools-istefox
[5] Note Pilot - Obsidian Plugin https://community.obsidian.md/plugins/note-pilot
[6] Vault | Obsidian Plugin Developer Docs https://marcusolsson.github.io/obsidian-plugin-docs/reference/typescript/classes/Vault
[7] File Management and Vault Operations | dannymcc/Granola-to-Obsidian | DeepWiki https://deepwiki.com/dannymcc/Granola-to-Obsidian/5.6-file-management-and-vault-operations
[8] Frontmatter in Templater - seeking solutions for 3 use cases - Help https://forum.obsidian.md/t/frontmatter-in-templater-seeking-solutions-for-3-use-cases/67670
[9] Plugin guidelines - Developer Documentation https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
[10] index - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/index
[11] Obsidian October plugin self-critique checklist https://docs.obsidian.md/oo/plugin
[12] User Scripts https://quickadd.obsidian.guide/docs/next/UserScripts/
[13] quickadd.obsidian.guide https://quickadd.obsidian.guide/docs/UserScripts.md
[14] Working with Files and Editor | obsidianmd/obsidian-developer ... https://deepwiki.com/obsidianmd/obsidian-developer-docs/2.4-working-with-files-and-editor
[15] deepwiki.com · obsidianmd · obsidian-developer-docsPlugin Development | obsidianmd/obsidian-developer-docs ... https://deepwiki.com/obsidianmd/obsidian-developer-docs/2-plugin-development
