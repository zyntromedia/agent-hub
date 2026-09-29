innerHTML Obsidian Plugins.md

```md
---
title: innerHTML ใน Obsidian Plugins
aliases:
  - innerHTML Obsidian Plugins
  - Avoid innerHTML in Obsidian Plugin
  - Obsidian Plugin XSS Prevention
  - Safe DOM Rendering Obsidian
  - Obsidian createEl Best Practices
  - Obsidian Plugin UI Security
tags:
  - obsidian
  - obsidian/api
  - obsidian/plugins
  - frontend
  - typescript
  - dom
  - security
  - xss
  - best-practices
status: active
note_type: security-guide
topic: Avoiding innerHTML in Obsidian plugin development
language: th
created: 2026-09-29
updated: 2026-09-29
reviewed: false
security_level: internal
audience:
  - plugin-developer
  - frontend-developer
  - typescript-developer
  - agent-developer
risk_level: high
related:
  - "[[Obsidian & Frontend Development]]"
  - "[[Best Practices]]"
  - "[[ตัวอย่างโค้ด TypeScript สำหรับเชื่อมต่อ AI Agent กับ Obsidian Plugin API]]"
  - "[[การดึง Metadata และ Frontmatter ผ่าน Obsidian MetadataCache API]]"
  - "[[Obsidian AGENTS API Knowledge Documents]]"
daily_note: "[[2026-09-29]]"
created_daily_note: "[[2026-09-29]]"
updated_daily_note: "[[2026-09-29]]"
cssclasses:
  - technical-note
  - security-note
  - frontend-note
---

# innerHTML ใน Obsidian Plugins

> [!abstract]
> หลีกเลี่ยง `innerHTML`, `outerHTML` และ `insertAdjacentHTML()` ใน Obsidian plugins โดยเฉพาะเมื่อ content มาจาก user input, file names, YAML frontmatter, Markdown notes, clipboard, external API หรือ AI output
>
> ให้ใช้ Obsidian DOM helpers:
>
> ```ts
> createEl()
> createDiv()
> createSpan()
> setText()
> empty()
> ```
>
> แทนการประกอบ HTML ด้วย string

> [!danger]
> การใส่ข้อมูลที่ไม่ trusted ลงใน `innerHTML` อาจทำให้เกิด:
>
> - Cross-site scripting (XSS)
> - UI manipulation
> - Unexpected DOM behavior
> - Event handler injection
> - Unsafe link/embed rendering
> - Plugin state corruption
> - Data exposure ผ่าน malicious HTML content

Obsidian Plugin Guidelines แนะนำให้หลีกเลี่ยง `innerHTML`, `outerHTML` และ `insertAdjacentHTML` และให้ใช้ DOM API helpers เช่น `createEl()` และ `createDiv()` แทน [475]

---

## สารบัญ

- [[#ทำไม innerHTML จึงเสี่ยง]]
- [[#Unsafe Patterns]]
- [[#Safe DOM Rendering]]
- [[#ล้าง DOM อย่างปลอดภัย]]
- [[#Render Note Metadata]]
- [[#Render User Input]]
- [[#Render Markdown]]
- [[#Forms และ Event Listeners]]
- [[#Styling Best Practices]]
- [[#AI Output และ Prompt Injection]]
- [[#Migration Guide]]
- [[#Checklist]]
- [[#Quick Reference]]

---

## ทำไม innerHTML จึงเสี่ยง

### Unsafe Data Sources ใน Obsidian

ข้อมูลต่อไปนี้ควรถือว่า untrusted โดย default:

```text
- Note title
- File name
- Vault path
- YAML frontmatter
- Aliases
- Tags
- Markdown body
- Block content
- User input
- Clipboard text
- URI parameters
- External API response
- Webhook payload
- AI-generated content
- Synced content
- Content from shared vault
```

### Example Vulnerability

```ts
function renderWelcome(
  containerEl: HTMLElement,
  userName: string
): void {
  containerEl.innerHTML = `
    <p>Welcome, ${userName}</p>
  `;
}
```

Input:

```html
<img src="x" onerror="alert('Injected content')">
```

ผลลัพธ์คือ browser อาจตีความ input เป็น HTML node แทนที่จะเป็น text:

```html
<p>
  Welcome,
  <img src="x" onerror="alert('Injected content')">
</p>
```

### Safer Rendering

```ts
function renderWelcome(
  containerEl: HTMLElement,
  userName: string
): void {
  containerEl.empty();

  containerEl.createEl('p', {
    text: `Welcome, ${userName}`
  });
}
```

ผลลัพธ์จะ render input เป็น plain text:

```text
Welcome, <img src="x" onerror="alert('Injected content')">
```

---

## Unsafe Patterns

### 1. Template String + `innerHTML`

```ts
// Avoid
containerEl.innerHTML = `
  <section class="plugin-card">
    <h2>${title}</h2>
    <p>${description}</p>
  </section>
`;
```

### 2. Append ด้วย `+=`

```ts
// Avoid
containerEl.innerHTML += `
  <li>${item}</li>
`;
```

ปัญหา:

```text
- Reparse content เดิมทั้งหมด
- Event listeners ของ children เดิมอาจหาย
- Slow เมื่อ list มีขนาดใหญ่
- XSS risk
- Debug ยาก
```

### 3. `insertAdjacentHTML()`

```ts
// Avoid
containerEl.insertAdjacentHTML(
  'beforeend',
  `<div>${message}</div>`
);
```

### 4. Inline Event Handlers

```ts
// Avoid
containerEl.innerHTML = `
  <button onclick="archiveNote('${path}')">
    Archive
  </button>
`;
```

ปัญหา:

```text
- String interpolation เสี่ยง injection
- TypeScript ตรวจ type ไม่ได้
- Function scope ไม่ชัดเจน
- Test ยาก
- CSP และ plugin review อาจมีปัญหา
```

### 5. Inline Styles ที่ Hardcode

```ts
// Avoid
containerEl.innerHTML = `
  <div style="color:#fff;background:#e11d48;padding:12px">
    Error
  </div>
`;
```

ปัญหา:

```text
- ไม่รองรับ dark/light theme
- User CSS override ยาก
- Styling กระจัดกระจาย
- Accessibility อาจไม่ผ่าน contrast
```

---

## Safe DOM Rendering

### Basic Element

```ts
const messageEl = containerEl.createEl('p', {
  text: 'Plugin loaded successfully.'
});
```

### Element with Class

```ts
const cardEl = containerEl.createEl('article', {
  cls: 'my-plugin-card'
});

cardEl.createEl('h3', {
  text: 'Security Review'
});

cardEl.createEl('p', {
  text: 'No pending items.'
});
```

### Nested Elements

```ts
function renderCard(
  containerEl: HTMLElement,
  title: string,
  description: string
): void {
  const cardEl = containerEl.createDiv({
    cls: 'my-plugin-card'
  });

  cardEl.createEl('h3', {
    text: title
  });

  cardEl.createEl('p', {
    text: description
  });
}
```

### Dynamic Text

```ts
const statusEl = containerEl.createEl('p', {
  cls: 'my-plugin-status'
});

statusEl.setText('Loading…');

try {
  const result = await loadData();

  statusEl.setText(
    `Loaded ${result.length} items.`
  );
} catch (error) {
  statusEl.setText(
    'Could not load data.'
  );
}
```

### Attributes

```ts
const linkEl = containerEl.createEl('a', {
  text: 'Open documentation',
  href: '[https://docs.obsidian.md](https://docs.obsidian.md)'
});

linkEl.setAttr('target', '_blank');
linkEl.setAttr('rel', 'noopener noreferrer');
```

> [!warning]
> Validate or allowlist URLs before assigning dynamic `href` values. Do not blindly create external links from untrusted note text, AI output or API payloads.

---

## ล้าง DOM อย่างปลอดภัย

### Do

```ts
containerEl.empty();
```

### Avoid

```ts
containerEl.innerHTML = '';
```

### Render Pattern

```ts
function renderResults(
  containerEl: HTMLElement,
  results: string[]
): void {
  containerEl.empty();

  if (results.length === 0) {
    containerEl.createEl('p', {
      text: 'No results found.',
      cls: 'my-plugin-muted'
    });

    return;
  }

  const listEl = containerEl.createEl('ul', {
    cls: 'my-plugin-result-list'
  });

  for (const result of results) {
    listEl.createEl('li', {
      text: result
    });
  }
}
```

Obsidian recommends `empty()` for clearing an element before re-rendering content rather than replacing it with an empty HTML string. [475]

---

## Render Note Metadata

### Unsafe Example

```ts
interface NoteData {
  title: string;
  path: string;
  tags: string[];
}

function renderNoteUnsafe(
  containerEl: HTMLElement,
  note: NoteData
): void {
  containerEl.innerHTML += `
    <article class="note-card">
      <h3>${note.title}</h3>
      <small>${note.path}</small>
      <div>
        ${note.tags
          .map((tag) => `<span>#${tag}</span>`)
          .join('')}
      </div>
    </article>
  `;
}
```

### Safe Example

```ts
interface NoteData {
  title: string;
  path: string;
  tags: string[];
}

function renderNote(
  containerEl: HTMLElement,
  note: NoteData
): void {
  const cardEl = containerEl.createEl('article', {
    cls: 'my-plugin-note-card'
  });

  cardEl.createEl('h3', {
    text: note.title
  });

  cardEl.createEl('small', {
    text: note.path,
    cls: 'my-plugin-note-path'
  });

  const tagsEl = cardEl.createDiv({
    cls: 'my-plugin-tags'
  });

  for (const tag of note.tags) {
    tagsEl.createSpan({
      text: `#${tag}`,
      cls: 'my-plugin-tag'
    });
  }
}
```

### Render Query Results

```ts
import {
  App,
  TFile
} from 'obsidian';

function renderNoteResults(
  app: App,
  containerEl: HTMLElement,
  files: TFile[]
): void {
  containerEl.empty();

  const listEl = containerEl.createEl('ul', {
    cls: 'my-plugin-note-list'
  });

  for (const file of files) {
    const metadata = app.metadataCache.getFileCache(file);
    const frontmatter = metadata?.frontmatter ?? {};

    const title =
      typeof frontmatter.title === 'string'
        ? frontmatter.title
        : file.basename;

    const rowEl = listEl.createEl('li', {
      cls: 'my-plugin-note-row'
    });

    const openButton = rowEl.createEl('button', {
      text: title,
      cls: 'my-plugin-note-button'
    });

    openButton.addEventListener('click', async () => {
      const leaf = app.workspace.getLeaf(false);

      await leaf.openFile(file);
    });

    rowEl.createEl('small', {
      text: file.path,
      cls: 'my-plugin-note-path'
    });
  }
}
```

---

## Render User Input

### Safe Search Form

```ts
import { Notice } from 'obsidian';

function renderSearchForm(
  containerEl: HTMLElement,
  onSearch: (query: string) => Promise<void>
): void {
  containerEl.empty();

  const formEl = containerEl.createEl('form', {
    cls: 'my-plugin-search-form'
  });

  const labelEl = formEl.createEl('label', {
    text: 'Search notes'
  });

  const inputEl = formEl.createEl('input', {
    type: 'search',
    placeholder: 'Tag, title, or status'
  });

  inputEl.id = 'my-plugin-search-input';
  labelEl.setAttr('for', inputEl.id);

  const submitButton = formEl.createEl('button', {
    text: 'Search',
    type: 'submit'
  });

  formEl.addEventListener('submit', async (event) => {
    event.preventDefault();

    const query = inputEl.value.trim();

    if (!query) {
      new Notice('Enter a search query first.');
      return;
    }

    submitButton.disabled = true;

    try {
      await onSearch(query);
    } finally {
      submitButton.disabled = false;
    }
  });
}
```

### Avoid Inline Handlers

```ts
// Avoid
containerEl.innerHTML = `
  <input id="query">
  <button onclick="search()">Search</button>
`;
```

ใช้ `addEventListener()` แทน:

```ts
buttonEl.addEventListener('click', async () => {
  await performSearch();
});
```

---

## Render Markdown

หากต้องแสดง Markdown ให้ใช้ Obsidian renderer แทนการแปลง Markdown เป็น HTML แล้วใส่ผ่าน `innerHTML`

```ts
import {
  App,
  Component,
  MarkdownRenderer
} from 'obsidian';

async function renderMarkdown(
  app: App,
  containerEl: HTMLElement,
  markdown: string,
  sourcePath: string,
  parentComponent: Component
): Promise<void> {
  containerEl.empty();

  await MarkdownRenderer.render(
    app,
    markdown,
    containerEl,
    sourcePath,
    parentComponent
  );
}
```

### Use in a Modal

```ts
import {
  App,
  Component,
  Modal,
  MarkdownRenderer
} from 'obsidian';

class MarkdownPreviewModal extends Modal {
  private readonly rendererComponent = new Component();

  constructor(
    app: App,
    private readonly markdown: string,
    private readonly sourcePath: string
  ) {
    super(app);
  }

  async onOpen(): Promise<void> {
    const { contentEl } = this;

    contentEl.empty();

    contentEl.createEl('h2', {
      text: 'Preview'
    });

    const previewEl = contentEl.createDiv({
      cls: 'markdown-rendered'
    });

    await MarkdownRenderer.render(
      this.app,
      this.markdown,
      previewEl,
      this.sourcePath,
      this.rendererComponent
    );
  }

  onClose(): void {
    this.rendererComponent.unload();
    this.contentEl.empty();
  }
}
```

> [!warning]
> MarkdownRenderer มีไว้เพื่อ render Markdown ตามระบบของ Obsidian ไม่ใช่ mechanism สำหรับ trust content  
> AI output, external content และ note content ที่มาจาก shared/untrusted source ควรถูก review และจำกัด scope ก่อน render หรือส่งต่อไปยัง write operation

---

## Forms และ Event Listeners

### Button with Async Action

```ts
function createActionButton(
  containerEl: HTMLElement,
  label: string,
  onClick: () => Promise<void>
): HTMLButtonElement {
  const buttonEl = containerEl.createEl('button', {
    text: label
  });

  buttonEl.addEventListener('click', async () => {
    buttonEl.disabled = true;

    try {
      await onClick();
    } catch (error) {
      console.error(error);
    } finally {
      buttonEl.disabled = false;
    }
  });

  return buttonEl;
}
```

### Confirmation Before Write

```ts
function renderArchiveAction(
  containerEl: HTMLElement,
  filePath: string,
  onConfirm: () => Promise<void>
): void {
  const buttonEl = containerEl.createEl('button', {
    text: 'Archive note',
    cls: 'mod-warning'
  });

  buttonEl.addEventListener('click', async () => {
    const confirmed = window.confirm(
      `Archive this note?\n\n${filePath}`
    );

    if (!confirmed) {
      return;
    }

    await onConfirm();
  });
}
```

> [!tip]
> สำหรับ production plugin ควรใช้ Obsidian `Modal` แบบ custom แทน `window.confirm()` เพื่อให้หน้าตาสอดคล้องกับ UI ของ Obsidian และแสดงรายละเอียด/diff ของการเปลี่ยนแปลงได้ครบกว่า

---

## Styling Best Practices

### TypeScript

```ts
const cardEl = containerEl.createDiv({
  cls: 'my-plugin-note-card'
});
```

### `styles.css`

```css
.my-plugin-note-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--background-modifier-border);
  border-radius: var(--radius-s);
  background: var(--background-secondary);
}

.my-plugin-note-path {
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--font-monospace);
  font-size: var(--font-smallest);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.my-plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.my-plugin-tag {
  padding: 2px 6px;
  border-radius: var(--radius-s);
  color: var(--text-accent);
  background: var(--background-modifier-hover);
  font-size: var(--font-smallest);
}
```

### Avoid

```ts
cardEl.style.backgroundColor = '#ffffff';
cardEl.style.color = '#000000';
cardEl.style.padding = '12px';
```

Use CSS classes and Obsidian variables because they better support dark mode, custom themes, user CSS snippets and accessibility. Obsidian’s plugin guidance recommends using classes and style sheets rather than inline styles. [475]

---

## AI Output และ Prompt Injection

### Treat AI Output as Untrusted

```text
AI response
≠ Trusted HTML
≠ Trusted Markdown
≠ Trusted instruction
≠ Safe action request
```

### Unsafe

```ts
containerEl.innerHTML = aiResponse;
```

### Safe Plain Text

```ts
containerEl.createEl('pre', {
  text: aiResponse
});
```

### Safe Structured Proposal

```ts
interface AgentProposal {
  title: string;
  summary: string;
  warnings: string[];
}

function renderAgentProposal(
  containerEl: HTMLElement,
  proposal: AgentProposal
): void {
  containerEl.empty();

  containerEl.createEl('h2', {
    text: proposal.title
  });

  containerEl.createEl('p', {
    text: proposal.summary
  });

  if (proposal.warnings.length > 0) {
    const warningEl = containerEl.createDiv({
      cls: 'my-plugin-warning'
    });

    warningEl.createEl('strong', {
      text: 'Warnings'
    });

    const listEl = warningEl.createEl('ul');

    for (const warning of proposal.warnings) {
      listEl.createEl('li', {
        text: warning
      });
    }
  }
}
```

### Agent UI Rules

```text
[ ] Never pass AI output to innerHTML
[ ] Never execute instructions embedded in note text
[ ] Never treat a Markdown note as plugin configuration
[ ] Never auto-click or auto-submit actions based on AI output
[ ] Require confirmation before vault writes
[ ] Display file paths affected by a proposed action
[ ] Preview a diff before modifying existing notes
[ ] Limit agent access by folder and file type
[ ] Keep secrets out of agent prompts and UI logs
```

---

## Migration Guide

### Before

```ts
function renderTask(
  containerEl: HTMLElement,
  task: string,
  complete: boolean
): void {
  containerEl.innerHTML += `
    <div class="task ${complete ? 'complete' : ''}">
      <input type="checkbox" ${complete ? 'checked' : ''}>
      <span>${task}</span>
    </div>
  `;
}
```

### After

```ts
function renderTask(
  containerEl: HTMLElement,
  task: string,
  complete: boolean
): void {
  const taskEl = containerEl.createDiv({
    cls: [
      'my-plugin-task',
      complete ? 'is-complete' : ''
    ]
      .filter(Boolean)
      .join(' ')
  });

  const checkboxEl = taskEl.createEl('input', {
    type: 'checkbox'
  });

  checkboxEl.checked = complete;

  taskEl.createSpan({
    text: task,
    cls: 'my-plugin-task-label'
  });
}
```

### Before

```ts
containerEl.innerHTML = '';
```

### After

```ts
containerEl.empty();
```

### Before

```ts
containerEl.insertAdjacentHTML(
  'beforeend',
  `<li>${result}</li>`
);
```

### After

```ts
listEl.createEl('li', {
  text: result
});
```

### Before

```ts
containerEl.innerHTML = `
  <button onclick="doSomething()">
    Run
  </button>
`;
```

### After

```ts
const buttonEl = containerEl.createEl('button', {
  text: 'Run'
});

buttonEl.addEventListener('click', async () => {
  await doSomething();
});
```

---

## Checklist

```text
DOM Security
[ ] No innerHTML
[ ] No outerHTML
[ ] No insertAdjacentHTML
[ ] No inline onclick/onchange/oninput handlers
[ ] No dynamic HTML string interpolation

Safe Rendering
[ ] Use createEl()
[ ] Use createDiv()
[ ] Use createSpan()
[ ] Use setText()
[ ] Use empty()
[ ] Use text: value for untrusted text
[ ] Use addEventListener() for interactions

Markdown
[ ] Use MarkdownRenderer when Markdown rendering is necessary
[ ] Set correct sourcePath for relative links
[ ] Attach renderer component to plugin/view lifecycle
[ ] Treat AI and external Markdown as untrusted

Styling
[ ] Use CSS classes
[ ] Keep styles in styles.css
[ ] Use Obsidian CSS variables
[ ] Test in light and dark themes
[ ] Avoid hardcoded colors unless justified

Write Safety
[ ] Show preview/diff before writes
[ ] Require explicit confirmation
[ ] Use Vault.process() for content updates
[ ] Use processFrontMatter() for metadata updates
[ ] Avoid automatic destructive actions
```

---

## Quick Reference

```ts
// Create element
const cardEl = containerEl.createEl('article', {
  cls: 'my-plugin-card'
});

// Create text safely
cardEl.createEl('p', {
  text: userProvidedText
});

// Create nested div
const rowEl = cardEl.createDiv({
  cls: 'my-plugin-row'
});

// Update existing text
statusEl.setText('Loading…');

// Clear container
containerEl.empty();

// Safe event listener
buttonEl.addEventListener('click', async () => {
  await runAction();
});

// Render Markdown through Obsidian
await MarkdownRenderer.render(
  app,
  markdown,
  containerEl,
  sourcePath,
  component
);
```

---

## Final Recommendation

> [!success]
> ใช้หลักการนี้เป็นมาตรฐาน:
>
> ```text
> HTML string construction
> → หลีกเลี่ยง
>
> Obsidian DOM helpers
> → ใช้เป็นค่าเริ่มต้น
>
> createEl() + text
> → safe text rendering
>
> empty()
> → clear UI
>
> addEventListener()
> → interaction
>
> CSS classes + Obsidian variables
> → styling
>
> MarkdownRenderer
> → render Markdown only when needed
> ```

> [!important]
> ใน Obsidian plugin, filenames, frontmatter, aliases, tags, note content และ AI output ไม่ควรถูก assume ว่าปลอดภัยสำหรับ `innerHTML`  
> ให้ render ทุก value เป็น text ผ่าน `createEl()` หรือ `setText()` เว้นแต่มีเหตุผลชัดเจนและมี sanitization/review ที่เหมาะสม

---

## Daily Notes

- Created: [[2026-09-29]]
- Updated: [[2026-09-29]]
- Related security research: [[2026-09-29]]

## Related Notes

- [[Obsidian & Frontend Development]]
- [[Best Practices]]
- [[ตัวอย่างโค้ด TypeScript สำหรับเชื่อมต่อ AI Agent กับ Obsidian Plugin API]]
- [[การดึง Metadata และ Frontmatter ผ่าน Obsidian MetadataCache API]]
- [[Obsidian AGENTS API Knowledge Documents]]

## Backlinks

> [!info]
> สร้าง backlink มายัง note นี้ด้วย:
>
> ```md
> [[innerHTML ใน Obsidian Plugins]]
> ```
>
> หรือ:
>
> ```md
> [[innerHTML ใน Obsidian Plugins|Avoid innerHTML in Obsidian Plugin]]
> ```
>
> Obsidian จะเพิ่ม incoming link ใน Backlinks panel อัตโนมัติ
```

การอ้างอิง:
[1] Plugin guidelines - Developer Documentation https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
