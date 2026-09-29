Best Practices

# Best Practices: Obsidian & Frontend Development

แนวปฏิบัติที่ดีสำหรับ Obsidian plugin คือออกแบบให้ **ปลอดภัย, ใช้ทรัพยากรต่ำ, เคารพข้อมูลใน vault, และกลมกลืนกับ UI ของ Obsidian** โดยใช้ API ที่ Obsidian รองรับอย่างเป็นทางการแทนการพึ่ง global objects หรือการแก้ DOM แบบเปราะบาง. แนวทางเหล่านี้สอดคล้องกับ Plugin Guidelines และ Developer Policies ของ Obsidian ซึ่งเน้นเรื่อง `innerHTML`, lifecycle cleanup, disclosure, telemetry และ dependency hygiene.[1][2][3]

## Architecture

แยก logic ของ plugin ออกจาก UI ตั้งแต่แรก เพื่อให้ test, review และขยาย feature ได้ง่าย

```text
src/
├── core/
│   ├── note-service.ts
│   ├── metadata-service.ts
│   ├── validation.ts
│   └── permissions.ts
├── commands/
│   └── commands.ts
├── views/
│   └── dashboard-view.ts
├── modals/
│   └── confirm-modal.ts
├── settings/
│   └── settings-tab.ts
├── editor/
│   └── extensions.ts
└── utils/
    ├── path.ts
    └── dates.ts
```

### Keep `main.ts` thin

```ts
import { Plugin } from 'obsidian';
import { DashboardView, DASHBOARD_VIEW } from './src/views/dashboard-view';
import { PluginSettingsTab } from './src/settings/settings-tab';

export default class VaultDashboardPlugin extends Plugin {
  async onload(): Promise<void> {
    this.registerView(
      DASHBOARD_VIEW,
      (leaf) => new DashboardView(leaf, this)
    );

    this.addSettingTab(
      new PluginSettingsTab(this.app, this)
    );

    this.addCommand({
      id: 'open-dashboard',
      name: 'Open dashboard',
      callback: async () => {
        await this.openDashboard();
      }
    });
  }

  async openDashboard(): Promise<void> {
    const existingLeaf = this.app.workspace
      .getLeavesOfType(DASHBOARD_VIEW)[0];

    const leaf =
      existingLeaf ??
      this.app.workspace.getRightLeaf(false);

    if (!leaf) {
      return;
    }

    await leaf.setViewState({
      type: DASHBOARD_VIEW,
      active: true
    });

    this.app.workspace.revealLeaf(leaf);
  }
}
```

### Prefer `this.app`, not `window.app`

```ts
// Good
const activeFile = this.app.workspace.getActiveFile();

// Avoid
const activeFile = window.app.workspace.getActiveFile();
```

`window.app` is intended primarily for debugging and should not be relied on by plugins; use the plugin instance’s `this.app` reference instead.[1][4][5]

### Use Obsidian registration APIs

```ts
this.registerEvent(
  this.app.vault.on('modify', (file) => {
    console.log('Modified:', file.path);
  })
);

this.registerView(
  'my-custom-view',
  (leaf) => new MyCustomView(leaf)
);

this.registerEditorExtension(myEditorExtension);
```

Registration methods allow Obsidian to clean up resources automatically when the plugin unloads. Prefer `registerEvent()`, `registerView()`, `registerEditorExtension()`, `addCommand()` and `addSettingTab()` rather than manually retaining listeners and view references.[3][5][6]

***

## UI and UX

ใช้ Obsidian-native components ก่อนสร้าง custom UI เอง เพราะผู้ใช้คุ้นเคยกับ conventions ของ Obsidian อยู่แล้ว

| Need | Recommended UI surface |
|---|---|
| Quick action | Command palette command |
| Frequently used action | Ribbon icon |
| Confirmation or short form | Modal |
| Persistent dashboard | `ItemView` sidebar/pane |
| User configuration | `PluginSettingTab` |
| Inline editor behavior | `Editor` API or CodeMirror 6 |
| Dynamic note data view | Bases view, where applicable |

Bases can display dynamic note-based tables, cards, lists, and related views; use it when your experience is fundamentally a structured note-data view rather than a bespoke application screen.[7]

### Use semantic DOM helpers

```ts
const button = contentEl.createEl('button', {
  text: 'Refresh results'
});

button.addEventListener('click', async () => {
  await this.render();
});
```

Avoid manually constructing HTML strings:

```ts
// Avoid
contentEl.innerHTML = `
  <button onclick="refresh()">Refresh</button>
`;
```

Obsidian’s guidelines specifically advise against `innerHTML`, `outerHTML`, and `insertAdjacentHTML`; use DOM creation helpers such as `createEl()`, `createDiv()`, and `setText()` instead.[1]

### Do not render untrusted text as HTML

```ts
// Good: safe text rendering
contentEl.createEl('pre', {
  text: userOrNoteContent
});
```

```ts
// Unsafe when source is untrusted
contentEl.innerHTML = userOrNoteContent;
```

This matters especially when content originates from notes, external APIs, clipboard text, synced sources, or AI output.

### Support themes

```css
.my-plugin-card {
  padding: 12px;
  border: 1px solid var(--background-modifier-border);
  border-radius: var(--radius-s);
  background: var(--background-secondary);
  color: var(--text-normal);
}

.my-plugin-muted {
  color: var(--text-muted);
}

.my-plugin-button {
  color: var(--text-accent);
}
```

Use Obsidian CSS variables instead of fixed colors:

```css
/* Avoid unless needed for a strong product reason */
background: #ffffff;
color: #000000;
```

Test every view in:

- Light theme
- Dark theme
- At least one popular custom theme
- Narrow sidebar width
- Long note/file names
- Large result lists
- Mobile, if `isDesktopOnly` is `false`

### UI setup timing

For UI that depends on workspace layout, use:

```ts
this.app.workspace.onLayoutReady(() => {
  // Initialize workspace-dependent UI here.
});
```

Obsidian’s plugin checklist recommends performing initial UI setup after `workspace.onLayoutReady()` rather than in constructors or immediately in `onload()`.[3]

***

## Data and performance

### Read metadata before reading full note bodies

```ts
const files = this.app.vault.getMarkdownFiles();

const reviewNotes = files.filter((file) => {
  const frontmatter = this.app.metadataCache
    .getFileCache(file)
    ?.frontmatter;

  return frontmatter?.status === 'in-review';
});
```

Use `MetadataCache` for frontmatter, headings, tags, links, embeds and blocks. Only call `vault.read()` or `vault.cachedRead()` when the actual Markdown content is required.

```ts
const content = await this.app.vault.cachedRead(file);
```

### Scope queries early

```ts
const files = this.app.vault
  .getMarkdownFiles()
  .filter((file) =>
    file.path.startsWith('03 Areas/Security/')
  )
  .filter((file) => {
    const fm = this.app.metadataCache
      .getFileCache(file)
      ?.frontmatter;

    return fm?.status === 'in-review';
  })
  .slice(0, 50);
```

Recommended order:

```text
Folder/path scope
→ File type filter
→ Metadata filter
→ Tag filter
→ Sort
→ Result limit
→ Render
```

### Avoid repeated full-vault scans

```ts
// Avoid calling this on every keystroke.
const allFiles = this.app.vault.getMarkdownFiles();
```

Instead:

- Debounce search input.
- Limit results.
- Cache summaries.
- Update only changed notes.
- Use `metadataCache.on('changed')` to refresh an index.
- Rebuild a full index only after metadata resolution or on explicit refresh.
- Avoid reading every file body just to build a list.

```ts
this.registerEvent(
  this.app.metadataCache.on('changed', (file) => {
    if (file.extension === 'md') {
      this.noteIndex.update(file);
    }
  })
);
```

### Do not iterate all files to find one path

```ts
// Avoid
const target = this.app.vault
  .getFiles()
  .find((file) => file.path === path);
```

```ts
// Prefer
const target = this.app.vault.getAbstractFileByPath(path);
```

Obsidian’s release checklist explicitly warns against iterating all files to find a file or folder by path.[1][3]

### Build concise view models

```ts
interface NoteSummary {
  path: string;
  title: string;
  tags: string[];
  status?: string;
  updated?: string;
}

function toNoteSummary(
  app: App,
  file: TFile
): NoteSummary {
  const frontmatter = app.metadataCache
    .getFileCache(file)
    ?.frontmatter ?? {};

  return {
    path: file.path,
    title:
      typeof frontmatter.title === 'string'
        ? frontmatter.title
        : file.basename,
    tags: Array.isArray(frontmatter.tags)
      ? frontmatter.tags.filter(
          (tag): tag is string => typeof tag === 'string'
        )
      : [],
    status:
      typeof frontmatter.status === 'string'
        ? frontmatter.status
        : undefined,
    updated:
      typeof frontmatter.updated === 'string'
        ? frontmatter.updated
        : undefined
  };
}
```

Render summaries in lists; load full notes only when users select one.

***

## Safe write operations

### Use preview and explicit confirmation

```text
Read note
→ Generate proposed change
→ Show preview/diff
→ User confirms
→ Apply change
→ Display result
```

```ts
new ConfirmActionModal(
  this.app,
  'Apply status update?',
  `Set status to "in-review" for ${file.path}`,
  async () => {
    await this.app.fileManager.processFrontMatter(
      file,
      (frontmatter) => {
        frontmatter.status = 'in-review';
      }
    );
  }
).open();
```

### Update frontmatter with `processFrontMatter()`

```ts
await this.app.fileManager.processFrontMatter(
  file,
  (frontmatter) => {
    frontmatter.status = 'active';
    frontmatter.updated = new Date()
      .toISOString()
      .slice(0, 10);
  }
);
```

This is preferable to reconstructing YAML manually because it preserves unrelated properties.

### Use `Vault.process()` for content updates

```ts
const expectedContent = await this.app.vault.read(file);

const proposedContent = [
  expectedContent.trimEnd(),
  '',
  '## Review',
  '',
  '- [ ] Confirm generated content'
].join('\n');

await this.app.vault.process(file, (current) => {
  if (current !== expectedContent) {
    throw new Error(
      'The note changed while the update was being prepared.'
    );
  }

  return proposedContent;
});
```

This helps prevent overwriting edits made by the user while a modal, agent workflow, or network request is in progress.

### Prefer draft-first for generated content

```text
Source note
→ Agent or plugin produces proposal
→ Create draft in 00 Inbox/
→ User reviews
→ User merges or accepts
```

```ts
await this.app.vault.create(
  '00 Inbox/Proposed - Review.md',
  proposedMarkdown
);
```

For AI-assisted features, draft-first should be the default for important notes, bulk operations, migrations, and content derived from external sources.

### Prefer trash over permanent deletion

```ts
await this.app.vault.trash(file, true);
```

Before delete-like actions:

- Show affected file paths.
- Tell the user whether items go to trash or are permanent.
- Require confirmation.
- Avoid bulk deletion as a default behavior.
- Offer dry-run mode where practical.

***

## Security and privacy

Community plugins run third-party code with meaningful access to a user’s environment and vault. Obsidian recommends independent review for plugins used with sensitive information, and Restricted mode exists to prevent community plugins from running by default.[8][9]

### Never store secrets in the plugin

Do not place credentials in:

```text
main.ts
settings tab values
manifest.json
styles.css
README examples
vault files
console logs
client-side requests
```

Examples of prohibited secret-like values:

```text
OpenAI API keys
Anthropic API keys
GitHub personal access tokens
Supabase service-role keys
Database passwords
JWT signing keys
OAuth client secrets
Private SSH keys
Webhook signing secrets
```

### Use a backend for external AI or API calls

```text
Obsidian plugin
→ User-approved minimal context
→ Trusted backend/proxy
→ Server-side secret storage
→ External AI/API provider
```

The backend should provide:

- Authentication
- Authorization
- Input validation
- Request-size limits
- Rate limiting
- Secret management
- Provider-specific privacy controls
- Metadata-only audit logging
- Error handling without leaking sensitive content

### Disclose network behavior

If a plugin uses remote services, clearly explain:

- Which service is contacted
- Why it is contacted
- What data is sent
- Whether an account is required
- Whether telemetry exists
- How users can disable the connection

Obsidian’s developer policies require disclosure for remote services and other sensitive capabilities; client-side telemetry is prohibited.[2][3]

### Keep dependencies minimal

```text
Fewer dependencies
→ smaller bundle
→ faster startup
→ smaller attack surface
→ easier code review
→ easier upgrades
```

- Prefer the Obsidian API before adding a library.
- Avoid packages with unnecessary analytics or tracking.
- Use a lock file.
- Review transitive dependencies.
- Remove unused packages.
- Pin and update dependencies intentionally.

The official checklist recommends dependency awareness, using a lock file, and following the “less is safer” principle.[3]

### Avoid telemetry

Obsidian Developer Policies prohibit client-side telemetry. Do not include analytics SDKs, hidden tracking pixels, fingerprinting scripts, or background usage reporting in a community plugin.[2][3]

***

## Editor and CodeMirror

### Prefer the standard `Editor` API for simple edits

```ts
this.addCommand({
  id: 'wrap-selection-as-info-callout',
  name: 'Wrap selection as info callout',
  editorCallback: (editor) => {
    const text = editor.getSelection().trim();

    if (!text) {
      return;
    }

    editor.replaceSelection(
      `> [!info]\n> ${text.replace(/\n/g, '\n> ')}`
    );
  }
});
```

Use the standard `Editor` API for:

- Current selection
- Cursor position
- Replacing selection
- Inserting text
- Editing ranges
- Basic command-driven edits

The Obsidian `Editor` class is designed for reading and manipulating active Markdown documents in edit mode.[10]

### Use CodeMirror 6 only when needed

Use editor extensions for features such as:

- Inline decorations
- Linting
- Autocomplete
- Interactive widgets
- Syntax-aware analysis
- Code actions
- Live validation

Avoid expensive work in editor update cycles:

```text
Do not:
- Scan entire vault
- Read every note body
- Call external APIs
- Render large DOM trees
- Run costly regex across huge documents
- Write notes automatically on every keystroke
```

Editor extensions should react only to relevant document changes and keep update code lightweight. Obsidian provides `registerEditorExtension()` for lifecycle-managed CodeMirror extension registration.[6][11]

***

## Release readiness

Before releasing to the Obsidian Community directory:

- [ ] Use a unique plugin ID.
- [ ] Remove placeholder names such as `MyPlugin`.
- [ ] Write clear command names in sentence case.
- [ ] Include `README.md`.
- [ ] Include `LICENSE`.
- [ ] Include valid `manifest.json`.
- [ ] Follow semantic versioning.
- [ ] Build and attach `main.js`, `manifest.json`, and `styles.css` if needed.
- [ ] Do not commit generated `main.js` to the source repository unless your release workflow requires it elsewhere.
- [ ] Commit a package-manager lock file.
- [ ] Test with a clean vault.
- [ ] Test enable/disable/reload behavior.
- [ ] Test light and dark themes.
- [ ] Test without network access if the plugin is expected to work locally.
- [ ] Document network, account, payment, telemetry, external-file and closed-source behavior.
- [ ] Remove debug logs and sensitive test data.
- [ ] Confirm that no secret is present in Git history.

Obsidian’s submission guidance requires a README, LICENSE and manifest, and uses Semantic Versioning for releases; its checklist further recommends meaningful naming, minimized release bundles, lock files, disclosure and performance optimization.[2][3][12]

***

## Practical checklist

```text
Architecture
[ ] Keep main.ts thin
[ ] Separate UI, domain logic, settings and utility code
[ ] Use this.app rather than window.app
[ ] Use registration APIs for lifecycle cleanup

UI
[ ] Prefer native Obsidian UI components
[ ] Do not use innerHTML for untrusted content
[ ] Use semantic HTML elements
[ ] Use Obsidian CSS variables
[ ] Test light/dark/narrow layouts

Performance
[ ] Use MetadataCache before reading note bodies
[ ] Scope folders before scanning metadata
[ ] Debounce search
[ ] Limit results
[ ] Cache indexes for repeated queries
[ ] Avoid full-vault scans on keystrokes
[ ] Avoid expensive editor extension updates

Writes
[ ] Preview changes
[ ] Require explicit confirmation
[ ] Use processFrontMatter for properties
[ ] Use Vault.process for body modifications
[ ] Prefer draft-first workflows
[ ] Prefer trash over permanent delete

Security
[ ] Never store client-side secrets
[ ] Avoid client-side telemetry
[ ] Disclose remote services and data use
[ ] Keep dependencies minimal
[ ] Validate paths and inputs
[ ] Treat note content as untrusted data
[ ] Do not log note bodies or sensitive metadata

Release
[ ] README and LICENSE included
[ ] Semantic version updated
[ ] Manifest valid
[ ] Lock file committed
[ ] Build artifacts attached to release
[ ] Clean-vault test completed
```

## Related notes

- [[Obsidian & Frontend Development]]
- [[ตัวอย่างโค้ด TypeScript สำหรับเชื่อมต่อ AI Agent กับ Obsidian Plugin API]]
- [[การดึง Metadata และ Frontmatter ผ่าน Obsidian MetadataCache API]]
- [[การดึงรายการไฟล์ทั้งหมดที่มีแท็กหรือ Metadata เฉพาะใน Obsidian Vault]]
- [[Obsidian AGENTS API Knowledge Documents]]
- [[Obsidian Database Migration]]

การอ้างอิง:
[1] Plugin guidelines - Developer Documentation https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
[2] Developer policies - Developer Documentation https://docs.obsidian.md/Developer+policies
[3] Obsidian October plugin self-critique checklist https://docs.obsidian.md/oo/plugin
[4] Plugin guidelines https://obsidian-developer-docs.pages.dev/Plugins/Releasing/Plugin-guidelines
[5] Plugin Guidelines and Best Practices | obsidianmd/obsidian ... https://deepwiki.com/obsidianmd/obsidian-developer-docs/2.2-plugin-guidelines-and-best-practices
[6] Plugin - Developer Documentation - Obsidian Developer Docs https://docs.obsidian.md/Reference/TypeScript+API/Plugin
[7] Build a Bases view - Developer Documentation https://docs.obsidian.md/plugins/guides/bases-view
[8] Plugin security - Obsidian Help https://obsidian.md/help/plugin-security
[9] Community plugins - Obsidian Help https://obsidian.md/help/community-plugins
[10] Editor https://docs.obsidian.md/Plugins/Editor/Editor
[11] Communicating with editor extensions https://docs.obsidian.md/Plugins/Editor/Communicating+with+editor+extensions
[12] Submit your plugin - Developer Documentation https://docs.obsidian.md/plugins/releasing/submit-plugin
[13] The future of Obsidian plugins https://obsidian.md/blog/future-of-plugins/
[14] أمان المكوّن الإضافي - مساعدة Obsidian - Obsidian Publish https://publish.obsidian.md/help-ar/extending-obsidian/plugin-security
[15] for Plugin Developers - Obsidian Hub https://publish.obsidian.md/hub/04+-+Guides,+Workflows,+&+Courses/for+Plugin+Developers
[16] deepwiki.com · obsidianmd · obsidian-developer-docsReleasing Your Plugin | obsidianmd/obsidian-developer-docs ... https://deepwiki.com/obsidianmd/obsidian-developer-docs/2.8-releasing-your-plugin
[17] deepwiki.com · obsidianmd · obsidian-developer-docsobsidianmd/obsidian-developer-docs | DeepWiki https://deepwiki.com/obsidianmd/obsidian-developer-docs
[18] Home - Developer Documentation - Obsidian https://docs.obsidian.md/Home
[19] Build a plugin https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin
