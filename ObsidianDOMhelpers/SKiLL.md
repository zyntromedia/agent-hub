Research Obsidian DOM helpers

# Research: Obsidian DOM Helpers

Obsidian extends `HTMLElement` with convenience methods for building plugin UI safely and idiomatically. The central helper is `createEl()`, which creates and appends a child element; related helpers such as `createDiv()`, `createSpan()`, `setText()`, `empty()`, `setAttr()`, and `toggleClass()` make it possible to build plugin interfaces without `innerHTML`.[1]

## Core helpers

### `createEl()`

`createEl()` creates an HTML element as a child of the current element and returns that child, so it can be further configured or used as a parent.

```ts
const headingEl = containerEl.createEl('h2', {
  text: 'Review Queue'
});

headingEl.addClass('my-plugin-heading');
```

```ts
const cardEl = containerEl.createEl('article', {
  cls: 'my-plugin-card'
});

cardEl.createEl('h3', {
  text: 'GitHub Actions Security'
});

cardEl.createEl('p', {
  text: 'This note needs review.'
});
```

The official Obsidian UI documentation describes `createEl()` as available on every `HTMLElement`, including UI container elements supplied by settings tabs, modals and custom views.[1][2]

### Common options

```ts
const linkEl = containerEl.createEl('a', {
  text: 'Open documentation',
  href: 'https://docs.obsidian.md',
  cls: 'my-plugin-link',
  attr: {
    target: '_blank',
    rel: 'noopener noreferrer'
  }
});
```

Useful options:

| Option | Purpose | Example |
|---|---|---|
| `text` | Safe text content | `{ text: 'Save' }` |
| `cls` | One or more CSS classes | `{ cls: 'my-plugin-card' }` |
| `attr` | HTML attributes | `{ attr: { 'aria-label': 'Refresh' } }` |
| `href` | Link destination | `{ href: 'https://...' }` |
| `type` | Input/button type | `{ type: 'button' }` |
| `placeholder` | Input hint text | `{ placeholder: 'Search notes' }` |

> [!important]
> Use `text` for values that originate from note content, file names, frontmatter, user input or AI output. It renders content as text rather than interpreting it as markup.

***

## Container elements

Obsidian gives plugins a context-appropriate `HTMLElement` in most UI surfaces.

| UI surface | Container element | Typical use |
|---|---|---|
| `PluginSettingTab` | `this.containerEl` | Settings UI |
| `Modal` | `this.contentEl` | Dialog content |
| `ItemView` | `this.contentEl` | Sidebar/pane/dashboard |
| `MarkdownRenderChild` | `this.containerEl` | Markdown post-processing |
| Status bar item | Returned `HTMLElement` | Compact status UI |
| Command/ribbon callback | Create modal/view first | Trigger actions |

### Settings tab

```ts
import {
  App,
  PluginSettingTab,
  Setting
} from 'obsidian';

export class ExampleSettingsTab extends PluginSettingTab {
  display(): void {
    const { containerEl } = this;

    containerEl.empty();

    containerEl.createEl('h2', {
      text: 'Plugin Settings'
    });

    new Setting(containerEl)
      .setName('Enable dashboard')
      .setDesc(
        'Show the dashboard in the right sidebar.'
      )
      .addToggle((toggle) =>
        toggle.setValue(true)
      );
  }
}
```

The official Settings guide uses `new Setting(containerEl)` to append native settings controls, with `setName()`, `setDesc()` and control-specific `add…()` methods.[3][4]

### Modal

```ts
import {
  App,
  Modal
} from 'obsidian';

export class ExampleModal extends Modal {
  constructor(app: App) {
    super(app);
  }

  onOpen(): void {
    const { contentEl } = this;

    contentEl.empty();

    contentEl.createEl('h2', {
      text: 'Confirm operation'
    });

    contentEl.createEl('p', {
      text: 'This action updates note metadata.'
    });

    const actionsEl = contentEl.createDiv({
      cls: 'my-plugin-modal-actions'
    });

    const cancelButton = actionsEl.createEl('button', {
      text: 'Cancel'
    });

    cancelButton.addEventListener('click', () => {
      this.close();
    });

    const confirmButton = actionsEl.createEl('button', {
      text: 'Confirm',
      cls: 'mod-warning'
    });

    confirmButton.addEventListener('click', async () => {
      this.close();
    });
  }

  onClose(): void {
    this.contentEl.empty();
  }
}
```

A modal’s `contentEl` is the intended container for plugin content; clearing it in `onClose()` is a common lifecycle pattern.[5]

### Custom view

```ts
import {
  ItemView,
  WorkspaceLeaf
} from 'obsidian';

export const DASHBOARD_VIEW_TYPE =
  'my-plugin-dashboard';

export class DashboardView extends ItemView {
  constructor(leaf: WorkspaceLeaf) {
    super(leaf);
  }

  getViewType(): string {
    return DASHBOARD_VIEW_TYPE;
  }

  getDisplayText(): string {
    return 'Dashboard';
  }

  getIcon(): string {
    return 'layout-dashboard';
  }

  async onOpen(): Promise<void> {
    this.contentEl.empty();

    this.contentEl.createEl('h2', {
      text: 'Vault Dashboard'
    });

    this.contentEl.createEl('p', {
      text: 'No pending review items.'
    });
  }

  async onClose(): Promise<void> {
    this.contentEl.empty();
  }
}
```

`ItemView` is the standard foundation for custom views, and Obsidian’s guide shows `onOpen()` as the place to build view content using `contentEl`, `empty()`, and `createEl()`.[2][6]

***

## Text and cleanup helpers

### `setText()`

Use `setText()` to replace the text content of an existing element.

```ts
const statusEl = containerEl.createEl('p', {
  cls: 'my-plugin-status'
});

statusEl.setText('Loading notes…');

try {
  const count = await getReviewCount();

  statusEl.setText(`${count} notes need review.`);
} catch {
  statusEl.setText('Could not load review status.');
}
```

### `empty()`

Use `empty()` to remove all child nodes before re-rendering.

```ts
function renderResults(
  containerEl: HTMLElement,
  results: string[]
): void {
  containerEl.empty();

  if (results.length === 0) {
    containerEl.createEl('p', {
      text: 'No results found.'
    });

    return;
  }

  const listEl = containerEl.createEl('ul');

  for (const result of results) {
    listEl.createEl('li', {
      text: result
    });
  }
}
```

Avoid:

```ts
containerEl.innerHTML = '';
```

### `createDiv()` and `createSpan()`

These are shorthand helpers for common layout structures.

```ts
const rowEl = containerEl.createDiv({
  cls: 'my-plugin-row'
});

rowEl.createSpan({
  text: 'Status: '
});

rowEl.createSpan({
  text: 'In review',
  cls: 'my-plugin-status-value'
});
```

### `setAttr()` and `setAttrs()`

Use attributes for semantics and accessibility.

```ts
const inputEl = containerEl.createEl('input', {
  type: 'search',
  placeholder: 'Search notes'
});

inputEl.setAttr('aria-label', 'Search notes');

inputEl.setAttrs({
  id: 'my-plugin-search',
  autocomplete: 'off'
});
```

### `toggleClass()`

Use `toggleClass()` for state-based styles.

```ts
const statusEl = containerEl.createDiv({
  cls: 'my-plugin-status'
});

const hasError = true;

statusEl.toggleClass('is-error', hasError);
statusEl.toggleClass('is-success', !hasError);
```

Obsidian’s HTML elements guide documents `cls` for CSS classes and `toggleClass()` for toggling styles based on application state.[1]

***

## Event helpers

### `addEventListener()`

For simple, short-lived elements:

```ts
const refreshButton = containerEl.createEl('button', {
  text: 'Refresh'
});

refreshButton.addEventListener('click', async () => {
  await refreshDashboard();
});
```

### `registerDomEvent()`

For listeners owned by a `Plugin`, `ItemView`, `Modal` or other `Component`, prefer `registerDomEvent()` when available so that the listener is detached automatically during unload.

```ts
const refreshButton = this.contentEl.createEl('button', {
  text: 'Refresh'
});

this.registerDomEvent(
  refreshButton,
  'click',
  async () => {
    await this.render();
  }
);
```

```ts
this.registerDomEvent(
  window,
  'resize',
  () => {
    this.updateLayout();
  }
);
```

Use `registerEvent()` for Obsidian event emitters and `registerDomEvent()` for browser DOM events. `Component.registerEvent()` registers an event reference to be detached during unloading.[7][8]

***

## Safe rendering patterns

### Note card

```ts
interface NoteSummary {
  title: string;
  path: string;
  tags: string[];
  status?: string;
}

function renderNoteCard(
  containerEl: HTMLElement,
  note: NoteSummary,
  onOpen: () => Promise<void>
): void {
  const cardEl = containerEl.createEl('article', {
    cls: 'my-plugin-note-card'
  });

  const titleButton = cardEl.createEl('button', {
    text: note.title,
    cls: 'my-plugin-note-title'
  });

  titleButton.addEventListener('click', async () => {
    await onOpen();
  });

  cardEl.createEl('small', {
    text: note.path,
    cls: 'my-plugin-note-path'
  });

  if (note.status) {
    cardEl.createEl('span', {
      text: note.status,
      cls: 'my-plugin-status-badge'
    });
  }

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

### Empty/loading/error states

```ts
type ViewState =
  | {
      kind: 'loading';
    }
  | {
      kind: 'empty';
      message: string;
    }
  | {
      kind: 'error';
      message: string;
    }
  | {
      kind: 'ready';
      count: number;
    };

function renderState(
  containerEl: HTMLElement,
  state: ViewState
): void {
  containerEl.empty();

  switch (state.kind) {
    case 'loading':
      containerEl.createEl('p', {
        text: 'Loading…',
        cls: 'my-plugin-muted'
      });
      return;

    case 'empty':
      containerEl.createEl('p', {
        text: state.message,
        cls: 'my-plugin-muted'
      });
      return;

    case 'error':
      containerEl.createEl('p', {
        text: state.message,
        cls: 'my-plugin-error'
      });
      return;

    case 'ready':
      containerEl.createEl('p', {
        text: `Found ${state.count} notes.`
      });
      return;
  }
}
```

### Accessible form

```ts
function renderTagSearch(
  containerEl: HTMLElement,
  onSearch: (tag: string) => Promise<void>
): void {
  containerEl.empty();

  const formEl = containerEl.createEl('form', {
    cls: 'my-plugin-search-form'
  });

  const labelEl = formEl.createEl('label', {
    text: 'Search notes by tag'
  });

  const inputEl = formEl.createEl('input', {
    type: 'search',
    placeholder: 'security'
  });

  inputEl.id = 'my-plugin-tag-search';
  labelEl.setAttr('for', inputEl.id);

  const searchButton = formEl.createEl('button', {
    text: 'Search',
    type: 'submit'
  });

  formEl.addEventListener('submit', async (event) => {
    event.preventDefault();

    const tag = inputEl.value
      .replace(/^#/, '')
      .trim();

    if (!tag) {
      return;
    }

    searchButton.disabled = true;

    try {
      await onSearch(tag);
    } finally {
      searchButton.disabled = false;
    }
  });
}
```

***

## Icons

Use `setIcon()` rather than embedding SVG strings manually.

```ts
import { setIcon } from 'obsidian';

const refreshButton = containerEl.createEl('button', {
  cls: 'clickable-icon'
});

refreshButton.setAttr('aria-label', 'Refresh');

setIcon(refreshButton, 'refresh-cw');
```

```ts
const statusEl = containerEl.createDiv({
  cls: 'my-plugin-status'
});

setIcon(statusEl, 'circle-check');
statusEl.createSpan({
  text: 'Vault index is ready.'
});
```

This avoids raw SVG injection and aligns icon rendering with Obsidian’s icon set. UI helper references identify `setIcon()` as the utility for adding an icon to an HTML element.[9]

***

## Markdown rendering

Use `MarkdownRenderer` when you want Obsidian to render Markdown; do not convert Markdown to HTML yourself and inject it via `innerHTML`.

```ts
import {
  App,
  Component,
  MarkdownRenderer
} from 'obsidian';

export async function renderMarkdownPreview(
  app: App,
  parent: Component,
  containerEl: HTMLElement,
  markdown: string,
  sourcePath: string
): Promise<void> {
  containerEl.empty();

  const renderer = new Component();

  parent.addChild(renderer);

  await MarkdownRenderer.render(
    app,
    markdown,
    containerEl,
    sourcePath,
    renderer
  );
}
```

`MarkdownRenderer` is part of the Obsidian TypeScript API and operates with a container `HTMLElement`; it is the appropriate renderer for Markdown preview content.[10]

> [!warning]
> Rendering Markdown is not the same as trusting it. Treat externally sourced Markdown and AI output as untrusted data, validate what is shown or acted on, and require explicit confirmation for vault writes.

***

## CSS integration

Assign semantic class names in TypeScript, then style them in `styles.css`.

```ts
const cardEl = containerEl.createDiv({
  cls: 'my-plugin-note-card'
});
```

```css
.my-plugin-note-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border: 1px solid var(--background-modifier-border);
  border-radius: var(--radius-s);
  background: var(--background-secondary);
}

.my-plugin-muted {
  color: var(--text-muted);
}

.my-plugin-error {
  color: var(--text-error);
}

.my-plugin-note-path {
  overflow: hidden;
  color: var(--text-muted);
  font-family: var(--font-monospace);
  font-size: var(--font-smallest);
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

Use Obsidian theme variables rather than fixed colors so your plugin works in light mode, dark mode and user-installed themes.

***

## Helper reference

| Helper | What it does | Typical use |
|---|---|---|
| `createEl(tag, options)` | Creates/appends an element | Structured UI |
| `createDiv(options)` | Creates/appends `<div>` | Layout wrappers |
| `createSpan(options)` | Creates/appends `<span>` | Inline labels/badges |
| `setText(text)` | Replaces text content | Status/message updates |
| `empty()` | Removes all children | Re-render UI |
| `setAttr(name, value)` | Sets one attribute | ARIA, IDs, URLs |
| `setAttrs(record)` | Sets multiple attributes | Form/input setup |
| `addClass(...classes)` | Adds CSS class(es) | Visual state |
| `removeClass(...classes)` | Removes CSS class(es) | Reset state |
| `toggleClass(class, value)` | Adds/removes class conditionally | Error/selected state |
| `hasClass(class)` | Tests for a class | Conditional UI logic |
| `createSvg(tag, options)` | Creates SVG element | Custom vector UI only |
| `setIcon(element, icon)` | Adds Lucide icon | Buttons/status icons |

Some helper methods are runtime extensions added by Obsidian to DOM prototypes, so they are available inside the Obsidian plugin runtime but not necessarily in a standalone browser/JSDOM environment without a compatible test setup.[11]

## Testing considerations

When testing DOM-rendering utilities outside Obsidian:

```text
Obsidian runtime:
HTMLElement.prototype.createEl()
HTMLElement.prototype.createDiv()
HTMLElement.prototype.createSpan()
HTMLElement.prototype.setText()
HTMLElement.prototype.empty()

Typical plain JSDOM:
These methods may not exist automatically.
```

Options:

- Use integration tests inside Obsidian for UI behavior.
- Abstract DOM construction behind small rendering functions.
- Mock helpers in tests.
- Use standard DOM equivalents in framework-independent core UI code.
- Use a compatible utility package only after reviewing its maintenance, license and dependency impact.

Example lightweight test helper:

```ts
export function installDomHelperMocks(): void {
  HTMLElement.prototype.empty = function (): void {
    this.replaceChildren();
  };

  HTMLElement.prototype.setText = function (
    text: string
  ): void {
    this.textContent = text;
  };
}
```

> [!tip]
> Keep domain services independent of `HTMLElement`. Test vault logic, metadata queries and write safety as plain TypeScript; reserve DOM integration tests for rendering and interaction boundaries.

## Summary

```text
Safe Obsidian UI pattern:

containerEl.empty()
→ createEl() / createDiv() / createSpan()
→ set text through { text: value } or setText()
→ add CSS classes
→ attach events with registerDomEvent()
→ use MarkdownRenderer only for Markdown
→ avoid innerHTML / outerHTML / insertAdjacentHTML
```

The official UI docs position `createEl()` as the primary mechanism for plugin DOM construction, with class support via `cls` and conditional styling via `toggleClass()`. Custom views, settings tabs and modals all expose container elements designed for this workflow.[1][2][3][5]

การอ้างอิง:
[1] HTML elements - Developer Documentation https://docs.obsidian.md/Plugins/User+interface/HTML+elements
[2] Views - Developer Documentation https://docs.obsidian.md/Plugins/User+interface/Views
[3] Settings - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Plugins/User+interface/Settings
[4] (constructor) - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Setting/(constructor)
[5] Modals | Obsidian Plugin Developer Docs https://marcusolsson.github.io/obsidian-plugin-docs/user-interface/modals
[6] ItemView - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/ItemView
[7] registerEvent - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Component/registerEvent
[8] Component - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/Component
[9] UI Elements | obsidianmd/obsidian-plugin-docs | DeepWiki https://deepwiki.com/obsidianmd/obsidian-plugin-docs/4.3-ui-elements
[10] MarkdownRenderer - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/MarkdownRenderer
[11] html-element | Obsidian Dev Utils https://mnaoumov.dev/obsidian-dev-utils/api/html-element/
[12] API & Code Quality Rules | colorsakura/obsidian-annotator-lite | DeepWiki https://deepwiki.com/colorsakura/obsidian-annotator-lite/8.1-api-and-code-quality-rules
[13] Plugin guidelines - Developer Documentation https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
[14] Workspace - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/Workspace
[15] index - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/index
[16] Home - Developer Documentation - Obsidian https://docs.obsidian.md/Home
[17] Build a Bases view - Developer Documentation https://docs.obsidian.md/plugins/guides/bases-view
[18] EditableFileView - Developer Documentation https://docs.obsidian.md/Reference/TypeScript+API/EditableFileView
