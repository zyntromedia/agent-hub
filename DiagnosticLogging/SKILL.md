การสร้าง diagnostic collector และ structured logging สำหรับ Obsidian

# การสร้าง Diagnostic Collector และ Structured Logging สำหรับ Obsidian

Diagnostic collector ที่ดีสำหรับ Obsidian plugin ควรเก็บเฉพาะเหตุการณ์ที่จำเป็นต่อการวิเคราะห์ปัญหา เช่น operation, duration, error code และ stack trace ที่ sanitize แล้ว โดยไม่เก็บ note body, prompt, API key หรือ frontmatter ที่อาจเป็นข้อมูลอ่อนไหว. สำหรับ lifecycle ให้ผูก event listeners และ timers ผ่าน `registerEvent()`, `registerDomEvent()` และ `registerInterval()` เพื่อให้ Obsidian cleanup เมื่อ plugin unload.[1][2][3][4]

## Architecture

```text
Plugin / View / Command
        │
        ▼
Structured Logger
        │
        ├── Console output
        ├── In-memory diagnostic buffer
        ├── Error serialization
        └── Redaction / sanitization
        │
        ▼
Diagnostic Collector
        │
        ├── Timings
        ├── Write conflicts
        ├── Vault operation failures
        ├── Metadata index events
        └── UI render failures
        │
        ▼
Diagnostics UI / Export
        │
        ├── User-safe status
        ├── Developer console details
        └── Explicit-confirmation export
```

### What to collect

```text
Safe by default
- Timestamp
- Log level
- Operation name
- Error code
- Sanitized error name/message
- Sanitized stack trace
- Duration in milliseconds
- Plugin version
- Obsidian version, if available
- Platform category
- File extension
- Redacted or allowlisted file path
- Number of affected files/results

Do not collect by default
- Full note content
- Frontmatter values
- AI prompt or response
- API keys, OAuth tokens, JWTs
- Authorization headers
- Passwords
- Cookie/session data
- Clipboard content
- Exact private vault paths
```

***

## Core types

สร้างไฟล์ `src/diagnostics/types.ts`

```ts
export type DiagnosticLevel =
  | 'debug'
  | 'info'
  | 'warn'
  | 'error';

export type DiagnosticErrorCode =
  | 'UNKNOWN'
  | 'INVALID_INPUT'
  | 'NOT_FOUND'
  | 'PATH_DENIED'
  | 'NOT_MARKDOWN'
  | 'METADATA_NOT_READY'
  | 'WRITE_FAILED'
  | 'WRITE_CONFLICT'
  | 'NETWORK_FAILED'
  | 'NETWORK_TIMEOUT'
  | 'RENDER_FAILED'
  | 'INDEX_FAILED'
  | 'SETTINGS_FAILED';

export interface DiagnosticContext {
  operation: string;
  durationMs?: number;
  errorCode?: DiagnosticErrorCode;
  filePath?: string;
  fileExtension?: string;
  affectedCount?: number;
  details?: Record<string, unknown>;
}

export interface DiagnosticEvent {
  id: string;
  timestamp: string;
  level: DiagnosticLevel;
  message: string;
  operation: string;
  durationMs?: number;
  errorCode?: DiagnosticErrorCode;
  filePath?: string;
  fileExtension?: string;
  affectedCount?: number;
  details?: Record<string, unknown>;
  error?: SerializedError;
}

export interface SerializedError {
  name: string;
  message: string;
  stack?: string;
}
```

> [!important]
> `operation` ควรเป็น stable identifier ที่ query ได้ง่าย เช่น:
>
> ```text
> plugin.onload
> metadata.index.rebuild
> metadata.search
> vault.content.update
> vault.frontmatter.update
> view.review-queue.render
> agent.proposal.generate
> agent.proposal.apply
> ```

***

## Redaction layer

สร้างไฟล์ `src/diagnostics/redaction.ts`

```ts
const SENSITIVE_KEY_PATTERN =
  /api[-_]?key|token|secret|password|authorization|cookie|session|prompt|content|body|markdown/i;

const SENSITIVE_PATH_PATTERN =
  /(^|\/)(\.obsidian|\.git|secrets?|credentials?|private)(\/|$)|\.env(\.|$)/i;

const MAX_STRING_LENGTH = 500;
const MAX_STACK_LENGTH = 3_000;

export function redactPath(
  path: string | undefined
): string | undefined {
  if (!path) {
    return undefined;
  }

  if (SENSITIVE_PATH_PATTERN.test(path)) {
    return '[redacted-path]';
  }

  return path;
}

export function redactValue(value: unknown): unknown {
  if (typeof value === 'string') {
    return value.length > MAX_STRING_LENGTH
      ? `${value.slice(0, MAX_STRING_LENGTH)}…[truncated]`
      : value;
  }

  if (Array.isArray(value)) {
    return value
      .slice(0, 20)
      .map((item) => redactValue(item));
  }

  if (
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  ) {
    return redactDetails(value as Record<string, unknown>);
  }

  return value;
}

export function redactDetails(
  details: Record<string, unknown> | undefined
): Record<string, unknown> | undefined {
  if (!details) {
    return undefined;
  }

  return Object.fromEntries(
    Object.entries(details).map(([key, value]) => {
      if (SENSITIVE_KEY_PATTERN.test(key)) {
        return [key, '[redacted]'];
      }

      return [key, redactValue(value)];
    })
  );
}

export function serializeError(
  error: unknown
): {
  name: string;
  message: string;
  stack?: string;
} {
  if (error instanceof Error) {
    return {
      name: error.name || 'Error',
      message: redactErrorMessage(error.message),
      stack: error.stack
        ? error.stack.slice(0, MAX_STACK_LENGTH)
        : undefined
    };
  }

  return {
    name: 'UnknownError',
    message: redactErrorMessage(String(error))
  };
}

function redactErrorMessage(message: string): string {
  return message
    .replace(
      /(?:api[-_]?key|token|secret|password)=\S+/gi,
      '$1=[redacted]'
    )
    .slice(0, MAX_STRING_LENGTH);
}
```

### Why redact by key and path?

```ts
logger.error('Request failed', error, {
  operation: 'agent.request',
  details: {
    endpoint: 'https://api.example.com',
    apiKey: 'sk-secret-value',
    prompt: 'private note content',
    retryCount: 1
  }
});
```

Expected safe output:

```ts
{
  endpoint: 'https://api.example.com',
  apiKey: '[redacted]',
  prompt: '[redacted]',
  retryCount: 1
}
```

> [!warning]
> Redaction เป็น defense-in-depth—not a reason to log arbitrary objects. ออกแบบ context ให้มีข้อมูลน้อยที่สุดตั้งแต่แรก

***

## Structured logger

สร้างไฟล์ `src/diagnostics/logger.ts`

```ts
import {
  DiagnosticContext,
  DiagnosticEvent,
  DiagnosticLevel
} from './types';

import {
  redactDetails,
  redactPath,
  serializeError
} from './redaction';

import { DiagnosticCollector } from './collector';

export interface LoggerOptions {
  namespace: string;
  isDebugEnabled: () => boolean;
  getPluginVersion: () => string;
}

export class StructuredLogger {
  constructor(
    private readonly collector: DiagnosticCollector,
    private readonly options: LoggerOptions
  ) {}

  debug(
    message: string,
    context: DiagnosticContext
  ): void {
    if (!this.options.isDebugEnabled()) {
      return;
    }

    this.log('debug', message, context);
  }

  info(
    message: string,
    context: DiagnosticContext
  ): void {
    this.log('info', message, context);
  }

  warn(
    message: string,
    context: DiagnosticContext
  ): void {
    this.log('warn', message, context);
  }

  error(
    message: string,
    error: unknown,
    context: DiagnosticContext
  ): void {
    this.log('error', message, context, error);
  }

  private log(
    level: DiagnosticLevel,
    message: string,
    context: DiagnosticContext,
    error?: unknown
  ): void {
    const event: DiagnosticEvent = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      level,
      message,
      operation: context.operation,
      durationMs: context.durationMs,
      errorCode: context.errorCode,
      filePath: redactPath(context.filePath),
      fileExtension: context.fileExtension,
      affectedCount: context.affectedCount,
      details: redactDetails(context.details),
      error: error
        ? serializeError(error)
        : undefined
    };

    this.collector.add(event);

    const prefix = `[${this.options.namespace}]`;

    switch (level) {
      case 'debug':
        console.debug(prefix, event);
        break;

      case 'info':
        console.info(prefix, event);
        break;

      case 'warn':
        console.warn(prefix, event);
        break;

      case 'error':
        console.error(prefix, event);
        break;
    }
  }
}
```

Example:

```ts
this.logger.info(
  'Metadata index rebuilt',
  {
    operation: 'metadata.index.rebuild',
    durationMs: 47,
    affectedCount: 172,
    details: {
      source: 'workspace.layout-ready'
    }
  }
);
```

Console output:

```text
[MyPlugin] {
  level: "info",
  operation: "metadata.index.rebuild",
  durationMs: 47,
  affectedCount: 172
}
```

Obsidian’s plugin anatomy guide identifies the Developer Tools console as a primary tool for monitoring plugin lifecycle and runtime behavior; open it with `Ctrl+Shift+I` on Windows/Linux or `Cmd+Option+I` on macOS.[3]

***

## Bounded diagnostic collector

อย่าเก็บ events แบบไม่จำกัด เพราะ plugin อาจทำงานหลายชั่วโมงหรือหลายวัน

สร้างไฟล์ `src/diagnostics/collector.ts`

```ts
import {
  DiagnosticEvent,
  DiagnosticLevel
} from './types';

export class DiagnosticCollector {
  private readonly events: DiagnosticEvent[] = [];

  constructor(
    private readonly maxEvents: number = 200
  ) {}

  add(event: DiagnosticEvent): void {
    this.events.push(event);

    const excess =
      this.events.length - this.maxEvents;

    if (excess > 0) {
      this.events.splice(0, excess);
    }
  }

  getAll(): readonly DiagnosticEvent[] {
    return [...this.events];
  }

  getRecent(
    limit: number = 50
  ): readonly DiagnosticEvent[] {
    return this.events.slice(-limit);
  }

  getByLevel(
    level: DiagnosticLevel
  ): readonly DiagnosticEvent[] {
    return this.events.filter(
      (event) => event.level === level
    );
  }

  getByOperation(
    operation: string
  ): readonly DiagnosticEvent[] {
    return this.events.filter(
      (event) => event.operation === operation
    );
  }

  clear(): void {
    this.events.length = 0;
  }

  getSummary(): {
    total: number;
    errors: number;
    warnings: number;
    latestTimestamp?: string;
  } {
    const errors = this.events.filter(
      (event) => event.level === 'error'
    ).length;

    const warnings = this.events.filter(
      (event) => event.level === 'warn'
    ).length;

    return {
      total: this.events.length,
      errors,
      warnings,
      latestTimestamp: this.events.at(-1)?.timestamp
    };
  }
}
```

### Example usage

```ts
const collector = new DiagnosticCollector(250);

const logger = new StructuredLogger(
  collector,
  {
    namespace: 'ReviewDashboard',
    isDebugEnabled: () => this.settings.debugMode,
    getPluginVersion: () => this.manifest.version
  }
);
```

> [!tip]
> ใช้ in-memory buffer เป็น default เพราะลดโอกาสเขียน sensitive diagnostic data ลง vault โดยไม่จำเป็น

***

## Operation timing

สร้างไฟล์ `src/diagnostics/measure.ts`

```ts
import { StructuredLogger } from './logger';

export async function measureAsync<T>(
  logger: StructuredLogger,
  operation: string,
  action: () => Promise<T>,
  context: Record<string, unknown> = {}
): Promise<T> {
  const startedAt = performance.now();

  try {
    const result = await action();

    logger.debug('Operation completed', {
      operation,
      durationMs: Math.round(
        performance.now() - startedAt
      ),
      details: context
    });

    return result;
  } catch (error) {
    logger.error(
      'Operation failed',
      error,
      {
        operation,
        durationMs: Math.round(
          performance.now() - startedAt
        ),
        errorCode: 'UNKNOWN',
        details: context
      }
    );

    throw error;
  }
}
```

Usage:

```ts
const notes = await measureAsync(
  this.logger,
  'metadata.search',
  async () => {
    return this.findNotesByTag('security');
  },
  {
    folderScope: '03 Areas/',
    resultLimit: 50
  }
);
```

### Slow operation wrapper

```ts
export async function measureWithThreshold<T>(
  logger: StructuredLogger,
  operation: string,
  thresholdMs: number,
  action: () => Promise<T>
): Promise<T> {
  const startedAt = performance.now();

  try {
    return await action();
  } finally {
    const durationMs = Math.round(
      performance.now() - startedAt
    );

    if (durationMs >= thresholdMs) {
      logger.warn('Slow operation detected', {
        operation,
        durationMs,
        details: {
          thresholdMs
        }
      });
    }
  }
}
```

Example:

```ts
const results = await measureWithThreshold(
  this.logger,
  'metadata.index.rebuild',
  1_000,
  async () => {
    return this.noteIndex.rebuild();
  }
);
```

***

## Integrate with plugin lifecycle

```ts
import {
  Plugin,
  TFile
} from 'obsidian';

import { DiagnosticCollector } from './src/diagnostics/collector';
import { StructuredLogger } from './src/diagnostics/logger';

interface PluginSettings {
  debugMode: boolean;
}

export default class ReviewDashboardPlugin extends Plugin {
  settings: PluginSettings = {
    debugMode: false
  };

  readonly diagnostics = new DiagnosticCollector(250);

  logger = new StructuredLogger(
    this.diagnostics,
    {
      namespace: 'ReviewDashboard',
      isDebugEnabled: () => this.settings.debugMode,
      getPluginVersion: () => this.manifest.version
    }
  );

  async onload(): Promise<void> {
    this.logger.info('Plugin loading', {
      operation: 'plugin.onload',
      details: {
        version: this.manifest.version
      }
    });

    this.registerEvent(
      this.app.metadataCache.on('changed', (file) => {
        if (file.extension !== 'md') {
          return;
        }

        this.logger.debug('Metadata changed', {
          operation: 'metadata.changed',
          filePath: file.path,
          fileExtension: file.extension
        });
      })
    );

    this.registerEvent(
      this.app.vault.on('delete', (file) => {
        this.logger.info('Vault file deleted', {
          operation: 'vault.delete',
          filePath: file.path,
          fileExtension:
            file instanceof TFile
              ? file.extension
              : undefined
        });
      })
    );

    this.registerDomEvent(
      window,
      'unhandledrejection',
      (event: PromiseRejectionEvent) => {
        this.logger.error(
          'Unhandled promise rejection',
          event.reason,
          {
            operation: 'runtime.unhandled-rejection',
            errorCode: 'UNKNOWN'
          }
        );
      }
    );
  }

  onunload(): void {
    this.logger.info('Plugin unloading', {
      operation: 'plugin.onunload'
    });
  }
}
```

Obsidian’s lifecycle guidance states that `registerEvent()` automatically detaches Obsidian event listeners, `registerDomEvent()` removes DOM listeners, and `registerInterval()` clears timers when a plugin unloads.[1][2][4]

> [!warning]
> `window`-level `error` and `unhandledrejection` handlersอาจรับ errors ของ Obsidian core หรือ plugin อื่น จึงควร log เพื่อ debugging เท่านั้น และไม่ควรแสดงทุก error เป็น user-facing failure ของ plugin คุณ

***

## Capture write diagnostics

สำหรับ Vault Write Service ให้ log outcome ที่มี context เพียงพอสำหรับ debug race condition แต่ไม่เก็บ content

```ts
async updateContent(
  file: TFile,
  expectedContent: string,
  proposedContent: string
): Promise<void> {
  const startedAt = performance.now();

  try {
    await this.app.vault.process(
      file,
      (currentContent) => {
        if (currentContent !== expectedContent) {
          throw new WriteConflictError(
            'The note changed after proposal generation.'
          );
        }

        return proposedContent;
      }
    );

    this.logger.info('Content update completed', {
      operation: 'vault.content.update',
      durationMs: Math.round(
        performance.now() - startedAt
      ),
      filePath: file.path,
      fileExtension: file.extension
    });
  } catch (error) {
    const conflict =
      error instanceof WriteConflictError;

    this.logger.error(
      conflict
        ? 'Content update conflict'
        : 'Content update failed',
      error,
      {
        operation: 'vault.content.update',
        durationMs: Math.round(
          performance.now() - startedAt
        ),
        filePath: file.path,
        fileExtension: file.extension,
        errorCode: conflict
          ? 'WRITE_CONFLICT'
          : 'WRITE_FAILED'
      }
    );

    throw error;
  }
}
```

Safe diagnostic output:

```json
{
  "operation": "vault.content.update",
  "durationMs": 12,
  "filePath": "03 Areas/Security/Review.md",
  "fileExtension": "md",
  "errorCode": "WRITE_CONFLICT"
}
```

Unsafe diagnostic output:

```json
{
  "expectedContent": "# Entire private note...",
  "currentContent": "# Entire modified private note...",
  "proposedContent": "# Full AI-generated replacement..."
}
```

***

## Diagnostic rules

เริ่มจาก rule-based diagnosis ที่ deterministic ก่อนใช้ AI analysis

### Repeated write conflict rule

```ts
import {
  DiagnosticEvent
} from './types';

export interface DiagnosticFinding {
  id: string;
  severity: 'info' | 'warning' | 'error';
  title: string;
  evidence: string[];
  recommendation: string;
}

export function findWriteConflictPattern(
  events: readonly DiagnosticEvent[]
): DiagnosticFinding | null {
  const conflicts = events.filter(
    (event) =>
      event.errorCode === 'WRITE_CONFLICT'
  );

  if (conflicts.length < 3) {
    return null;
  }

  return {
    id: 'repeated-write-conflicts',
    severity: 'warning',
    title: 'Repeated write conflicts detected',
    evidence: conflicts
      .slice(-5)
      .map(
        (event) =>
          `${event.timestamp} — ${event.operation}`
      ),
    recommendation: [
      'Use a shared per-file write queue.',
      'Create proposals from a content snapshot.',
      'Compare snapshot and current content in Vault.process().',
      'Regenerate the proposal if a conflict occurs.',
      'Avoid read → await → modify workflows.'
    ].join(' ')
  };
}
```

### Slow search rule

```ts
export function findSlowSearchPattern(
  events: readonly DiagnosticEvent[]
): DiagnosticFinding | null {
  const slowSearches = events.filter(
    (event) =>
      event.operation === 'metadata.search' &&
      (event.durationMs ?? 0) >= 250
  );

  if (slowSearches.length < 3) {
    return null;
  }

  return {
    id: 'slow-metadata-search',
    severity: 'warning',
    title: 'Metadata search is repeatedly slow',
    evidence: slowSearches
      .slice(-5)
      .map(
        (event) =>
          `${event.timestamp} — ${event.durationMs} ms`
      ),
    recommendation: [
      'Restrict search to an allowed folder.',
      'Debounce user input.',
      'Apply a maximum result limit.',
      'Build an in-memory index.',
      'Avoid reading note bodies while searching metadata.'
    ].join(' ')
  };
}
```

***

## Diagnostics view

สร้าง custom `ItemView` เพื่อให้ developer/user เห็น summary แต่ไม่ต้องเปิด Console ทุกครั้ง

```ts
import {
  ItemView,
  WorkspaceLeaf
} from 'obsidian';

import {
  DiagnosticCollector
} from '../diagnostics/collector';

export const DIAGNOSTICS_VIEW_TYPE =
  'my-plugin-diagnostics';

export class DiagnosticsView extends ItemView {
  constructor(
    leaf: WorkspaceLeaf,
    private readonly collector: DiagnosticCollector
  ) {
    super(leaf);
  }

  getViewType(): string {
    return DIAGNOSTICS_VIEW_TYPE;
  }

  getDisplayText(): string {
    return 'Plugin Diagnostics';
  }

  getIcon(): string {
    return 'bug';
  }

  async onOpen(): Promise<void> {
    this.render();
  }

  render(): void {
    const { contentEl } = this;

    contentEl.empty();

    contentEl.createEl('h2', {
      text: 'Plugin Diagnostics'
    });

    const summary = this.collector.getSummary();

    contentEl.createEl('p', {
      text: [
        `Events: ${summary.total}`,
        `Warnings: ${summary.warnings}`,
        `Errors: ${summary.errors}`
      ].join(' · ')
    });

    const events = this.collector
      .getRecent(50)
      .slice()
      .reverse();

    if (events.length === 0) {
      contentEl.createEl('p', {
        text: 'No diagnostic events recorded.',
        cls: 'my-plugin-muted'
      });

      return;
    }

    const listEl = contentEl.createEl('ul', {
      cls: 'my-plugin-diagnostic-list'
    });

    for (const event of events) {
      const itemEl = listEl.createEl('li', {
        cls: `my-plugin-diagnostic-item is-${event.level}`
      });

      itemEl.createEl('strong', {
        text: `[${event.level.toUpperCase()}] `
      });

      itemEl.createSpan({
        text: event.message
      });

      itemEl.createEl('small', {
        text: [
          event.operation,
          event.durationMs
            ? `${event.durationMs} ms`
            : null,
          event.errorCode ?? null
        ]
          .filter(Boolean)
          .join(' · '),
        cls: 'my-plugin-muted'
      });
    }
  }
}
```

> [!tip]
> Diagnostics view ควรแสดง summary, sanitized messages และ aggregate counts ไม่ควรแสดง raw request payloads, note content หรือ secret-like values

***

## Export diagnostics safely

การ export diagnostic report เป็น write operation จึงควรทำหลัง user confirmation และต้องแสดง destination path ที่ resolve แล้ว

```ts
import {
  App,
  normalizePath
} from 'obsidian';

import {
  DiagnosticEvent
} from './types';

export function buildDiagnosticMarkdown(
  events: readonly DiagnosticEvent[]
): string {
  const rows = events.map((event) => {
    const escapedMessage = event.message
      .replace(/\|/g, '\\|');

    return [
      event.timestamp,
      event.level,
      event.operation,
      event.durationMs ?? '',
      event.errorCode ?? '',
      escapedMessage
    ].join(' | ');
  });

  return [
    '---',
    'title: Plugin Diagnostics',
    'note_type: diagnostic-report',
    `created: ${new Date().toISOString()}`,
    'contains_note_content: false',
    'contains_secrets: false',
    '---',
    '',
    '# Plugin Diagnostics',
    '',
    '> [!warning]',
    '> This report contains sanitized runtime metadata only.',
    '',
    '| Time | Level | Operation | Duration | Error Code | Message |',
    '|---|---|---|---:|---|---|',
    ...rows,
    ''
  ].join('\n');
}

export async function exportDiagnosticReport(
  app: App,
  events: readonly DiagnosticEvent[]
): Promise<string> {
  const folder = '09 Reports/Plugin Diagnostics';

  const timestamp = new Date()
    .toISOString()
    .replace(/[:.]/g, '-');

  const destination = normalizePath(
    `${folder}/Diagnostics ${timestamp}.md`
  );

  if (!app.vault.getAbstractFileByPath(folder)) {
    await app.vault.createFolder(folder);
  }

  await app.vault.create(
    destination,
    buildDiagnosticMarkdown(events)
  );

  return destination;
}
```

Recommended confirmation UI:

```text
Create sanitized diagnostic report?

Destination:
09 Reports/Plugin Diagnostics/Diagnostics 2026-09-29T17-19-00-000Z.md

The report includes:
- Timestamp
- Operation names
- Durations
- Error codes
- Sanitized messages

The report excludes:
- Note content
- AI prompts/responses
- Tokens and API keys
- Full frontmatter
```

***

## Recommended settings

```ts
export interface DiagnosticsSettings {
  debugMode: boolean;
  performanceMetrics: boolean;
  maxEvents: number;
  allowDiagnosticExport: boolean;
}

export const DEFAULT_DIAGNOSTICS_SETTINGS:
  DiagnosticsSettings = {
    debugMode: false,
    performanceMetrics: false,
    maxEvents: 200,
    allowDiagnosticExport: true
  };
```

| Setting | Default | Reason |
|---|---:|---|
| Debug mode | `false` | ลด console noise และ accidental data exposure |
| Performance metrics | `false` | เปิดเมื่อ investigate performance |
| Max events | `200` | Bounded memory usage |
| Export diagnostics | `true` | Allow user-initiated support reports |
| Auto export | `false` | ไม่เขียนข้อมูลลง vault โดยไม่ขออนุมัติ |
| Remote telemetry | `false` | ควรไม่ส่ง diagnostic data ออก network โดย default |

***

## Testing checklist

```text
Redaction
[ ] apiKey is replaced with [redacted]
[ ] token is replaced with [redacted]
[ ] prompt/content/body keys are redacted
[ ] .env and secrets paths are redacted
[ ] long strings are truncated
[ ] error stacks are length-limited

Collector
[ ] respects maxEvents
[ ] removes oldest events first
[ ] returns immutable copy to callers
[ ] clear() removes all events
[ ] summary counts warnings/errors correctly

Logger
[ ] debug events are skipped if debugMode is false
[ ] info/warn/error events are collected
[ ] error serializes Error safely
[ ] operation is always present
[ ] raw note content is never included

Lifecycle
[ ] workspace/vault listeners use registerEvent()
[ ] window/document listeners use registerDomEvent()
[ ] timers use registerInterval()
[ ] plugin disable unloads listeners
[ ] view close clears view-specific UI/state

Write diagnostics
[ ] success does not log note body
[ ] conflict returns WRITE_CONFLICT
[ ] write failure returns WRITE_FAILED
[ ] frontmatter failure is handled
[ ] export requires explicit confirmation
```

## Summary

```text
Safe diagnostic architecture:

StructuredLogger
→ sanitize context
→ serialize errors
→ console output
→ bounded DiagnosticCollector
→ rule-based findings
→ optional user-confirmed export

Lifecycle:

registerEvent()
registerDomEvent()
registerInterval()

Never log by default:

note bodies
frontmatter payloads
AI prompts/responses
tokens
API keys
authorization headers
cookies
passwords
```

Obsidian’s lifecycle model is designed for this pattern: `Plugin` inherits component cleanup helpers, so registering workspace/vault events, DOM events and intervals through the provided methods prevents stale listeners and resource leaks when the plugin is disabled or reloaded.[1][2][3][4]

การอ้างอิง:
[1] Manage plugin lifecycle - Developer Documentation https://docs.obsidian.md/plugins/guides/lifecycle-management
[2] registerDomEvent - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Component/registerDomEvent
[3] Anatomy of a plugin - Developer Documentation https://docs.obsidian.md/Plugins/Getting+started/Anatomy+of+a+plugin
[4] obsidian https://www.npmjs.com/package/obsidian
[5] aidenlx/obsidian https://www.npmjs.com/package/@aidenlx/obsidian
[6] Plugin Anatomy and Lifecycle | obsidianmd/obsidian-plugin-docs | DeepWiki https://deepwiki.com/obsidianmd/obsidian-plugin-docs/3.1-plugin-anatomy-and-lifecycle
[7] Event Handling | obsidianmd/obsidian-plugin-docs | DeepWiki https://deepwiki.com/obsidianmd/obsidian-plugin-docs/5.1-event-handling
[8] Advanced Topics | obsidianmd/obsidian-plugin-docs | DeepWiki https://deepwiki.com/obsidianmd/obsidian-plugin-docs/5-advanced-topics
[9] Memory Management & Lifecycle | gapmiss/obsidian-plugin-skill | DeepWiki https://deepwiki.com/gapmiss/obsidian-plugin-skill/4.1-memory-management-and-lifecycle
