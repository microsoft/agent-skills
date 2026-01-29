#!/usr/bin/env python3
"""Script to write the updated skill files."""
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# SKILL.md content
skill_md = '''# Microsoft Foundry NextGen Frontend Skill

Build elegant frontend UIs following Microsoft Foundry's NextGen Design System.

## Stack

- **Build**: Vite + React + pnpm
- **Styling**: CSS variables following Foundry design tokens
- **Icons**: Lucide React icons
- **Charts**: Recharts with Foundry theming

## Quick Start

```bash
pnpm create vite@latest my-foundry-app --template react-ts
cd my-foundry-app
pnpm add lucide-react recharts
```

## Critical Design Principles

### Color Usage - IMPORTANT

**Foundry uses a NEUTRAL dark theme. Purple is used SPARINGLY.**

#### Where Purple (#8251EE / #A37EF5) IS Used:
- ✅ Primary action buttons (filled background)
- ✅ Active tab underlines (2px accent line)
- ✅ Row selection indicator (left border bar)
- ✅ Active sidebar icon highlights
- ✅ Links and interactive text
- ✅ Progress indicators and sliders (track fill)
- ✅ Focus rings on inputs

#### Where Purple is NOT Used:
- ❌ Card backgrounds (use #141414)
- ❌ Surface backgrounds (use #1C1C1C)
- ❌ Text colors (use #FFFFFF, #A1A1A1, #6B6B6B)
- ❌ Table row backgrounds (use transparent or #1C1C1C on hover)
- ❌ Panel backgrounds (use #0D0D0D or #141414)
- ❌ Secondary buttons (use grey outline with white text)
- ❌ Borders (use #2A2A2A or #333333)

### Core Color Palette

```css
:root {
  /* Backgrounds - Neutral Darks (NOT purple) */
  --bg-page: #0A0A0A;
  --bg-sidebar: #0D0D0D;
  --bg-card: #141414;
  --bg-surface: #1C1C1C;
  --bg-elevated: #242424;
  --bg-hover: #2A2A2A;
  
  /* Text - White and Greys (NOT lavender) */
  --text-primary: #FFFFFF;
  --text-secondary: #A1A1A1;
  --text-muted: #6B6B6B;
  --text-disabled: #4A4A4A;
  
  /* Borders - Subtle Greys */
  --border-default: #2A2A2A;
  --border-subtle: #1F1F1F;
  --border-strong: #333333;
  
  /* Brand Purple - USE SPARINGLY */
  --brand-primary: #8251EE;
  --brand-hover: #9366F5;
  --brand-light: #A37EF5;
  
  /* Semantic */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

## Component Patterns

### Buttons

```jsx
// Primary - Purple filled (use for main actions)
<button className="btn-primary">Create</button>

// Secondary - Grey outline (NOT purple)
<button className="btn-secondary">Cancel</button>

// Ghost - Transparent with subtle hover
<button className="btn-ghost">Options</button>
```

```css
.btn-primary {
  background: var(--brand-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
}
.btn-primary:hover { background: var(--brand-hover); }

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
  padding: 8px 16px;
  border-radius: 6px;
}
.btn-secondary:hover { background: var(--bg-hover); }

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: none;
  padding: 8px 12px;
}
.btn-ghost:hover { 
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

### Cards

```css
/* Cards are NEUTRAL GREY, not purple */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 16px;
}

.card-elevated {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
```

### Data Tables

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 13px;
  border-bottom: 1px solid var(--border-default);
}

.data-table td {
  padding: 12px 16px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
}

.data-table tr:hover td {
  background: var(--bg-surface);
}

/* Selected row - purple LEFT BORDER only, not bg */
.data-table tr.selected td {
  background: var(--bg-surface);
}
.data-table tr.selected td:first-child {
  box-shadow: inset 3px 0 0 var(--brand-primary);
}
```

### Tabs

```css
.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--border-default);
}

.tab {
  padding: 12px 0;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
}

.tab:hover { color: var(--text-primary); }

/* Active tab - purple underline only */
.tab.active {
  color: var(--text-primary);
}
.tab.active::after {
  content: \\'\\';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--brand-primary);
}
```

### Sidebar Navigation

```css
.sidebar {
  width: 56px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  padding: 12px 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin: 4px auto;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
}

.sidebar-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Active - purple icon, subtle bg */
.sidebar-item.active {
  background: var(--bg-surface);
  color: var(--brand-light);
}
```

### Form Inputs

```css
.input {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 14px;
}

.input::placeholder { color: var(--text-muted); }
.input:hover { border-color: var(--border-strong); }
.input:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px rgba(130, 81, 238, 0.2);
}
```

### Modals/Dialogs

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 100%;
}

.modal-header {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
```

## Layout Structure

```jsx
function FoundryLayout({ children }) {
  return (
    <div className="app-layout">
      <header className="top-bar">
        <Logo />
        <nav className="breadcrumb">{/* ... */}</nav>
        <div className="top-actions">
          <SearchBar />
          <UserMenu />
        </div>
      </header>
      
      <div className="main-container">
        <aside className="sidebar">
          <SidebarNav />
        </aside>
        
        <main className="content">
          {children}
        </main>
      </div>
    </div>
  );
}
```

```css
.app-layout {
  min-height: 100vh;
  background: var(--bg-page);
  color: var(--text-primary);
}

.top-bar {
  height: 48px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  padding: 0 16px;
}

.main-container {
  display: flex;
  height: calc(100vh - 48px);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
```

## Typography

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, \\'Segoe UI\\', sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
}

.heading-xl { font-size: 24px; font-weight: 600; }
.heading-lg { font-size: 20px; font-weight: 600; }
.heading-md { font-size: 16px; font-weight: 600; }
.text-sm { font-size: 13px; }
.text-xs { font-size: 12px; }
.text-muted { color: var(--text-muted); }
.text-secondary { color: var(--text-secondary); }
```

## Reference Files

For detailed specifications, see:
- [Design Tokens](references/design-tokens.md) - Complete color and spacing system
- [Components](references/components.md) - Full component library
- [Patterns](references/patterns.md) - Layout and interaction patterns
'''

# design-tokens.md content
design_tokens_md = '''# Foundry NextGen Design Tokens

## Color System

### Background Colors (Neutral Darks)

**IMPORTANT: Backgrounds are neutral grey, NOT purple-tinted.**

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-page` | #0A0A0A | Main page background |
| `--bg-sidebar` | #0D0D0D | Sidebar and top bar |
| `--bg-card` | #141414 | Cards, panels, dialogs |
| `--bg-surface` | #1C1C1C | Table rows, nested surfaces |
| `--bg-elevated` | #242424 | Dropdowns, popovers |
| `--bg-hover` | #2A2A2A | Hover states |
| `--bg-active` | #333333 | Pressed/active backgrounds |

### Text Colors (White and Greys)

**IMPORTANT: Text is white/grey, NOT lavender/purple-tinted.**

| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | #FFFFFF | Main body text, headings |
| `--text-secondary` | #A1A1A1 | Secondary text, labels |
| `--text-muted` | #6B6B6B | Placeholder, disabled hints |
| `--text-disabled` | #4A4A4A | Disabled text |
| `--text-link` | #A37EF5 | Links and interactive text |

### Border Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--border-subtle` | #1F1F1F | Subtle dividers |
| `--border-default` | #2A2A2A | Standard borders |
| `--border-strong` | #333333 | Emphasized borders |
| `--border-focus` | #8251EE | Focus rings |

### Brand Colors (Use Sparingly)

**Purple is ONLY for primary actions and active indicators.**

| Token | Value | Usage |
|-------|-------|-------|
| `--brand-primary` | #8251EE | Primary buttons, active indicators |
| `--brand-hover` | #9366F5 | Primary button hover |
| `--brand-light` | #A37EF5 | Links, active sidebar icons |
| `--brand-muted` | rgba(130,81,238,0.2) | Focus shadows, selection hints |

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--success` | #10B981 | Success states |
| `--success-muted` | rgba(16,185,129,0.15) | Success backgrounds |
| `--warning` | #F59E0B | Warning states |
| `--warning-muted` | rgba(245,158,11,0.15) | Warning backgrounds |
| `--error` | #EF4444 | Error states |
| `--error-muted` | rgba(239,68,68,0.15) | Error backgrounds |
| `--info` | #3B82F6 | Info states |

## Spacing Scale

| Token | Value |
|-------|-------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 4px | Small elements, tags |
| `--radius-md` | 6px | Buttons, inputs |
| `--radius-lg` | 8px | Cards, panels |
| `--radius-xl` | 12px | Modals, large cards |
| `--radius-full` | 9999px | Pills, avatars |

## Typography Scale

| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `--text-xs` | 12px | 400 | Captions, timestamps |
| `--text-sm` | 13px | 400 | Table headers, labels |
| `--text-base` | 14px | 400 | Body text |
| `--text-lg` | 16px | 500 | Subheadings |
| `--text-xl` | 20px | 600 | Section headings |
| `--text-2xl` | 24px | 600 | Page titles |

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | 0 1px 2px rgba(0,0,0,0.3) | Subtle elevation |
| `--shadow-md` | 0 4px 12px rgba(0,0,0,0.4) | Cards, dropdowns |
| `--shadow-lg` | 0 8px 24px rgba(0,0,0,0.5) | Modals, popovers |
| `--shadow-focus` | 0 0 0 2px rgba(130,81,238,0.25) | Focus rings |

## Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--z-base` | 0 | Default |
| `--z-dropdown` | 100 | Dropdowns |
| `--z-sticky` | 200 | Sticky headers |
| `--z-modal` | 300 | Modals |
| `--z-toast` | 400 | Toasts, notifications |
| `--z-tooltip` | 500 | Tooltips |

## Complete CSS Variables

```css
:root {
  /* Backgrounds - Neutral Darks */
  --bg-page: #0A0A0A;
  --bg-sidebar: #0D0D0D;
  --bg-card: #141414;
  --bg-surface: #1C1C1C;
  --bg-elevated: #242424;
  --bg-hover: #2A2A2A;
  --bg-active: #333333;
  
  /* Text - White and Greys */
  --text-primary: #FFFFFF;
  --text-secondary: #A1A1A1;
  --text-muted: #6B6B6B;
  --text-disabled: #4A4A4A;
  --text-link: #A37EF5;
  
  /* Borders */
  --border-subtle: #1F1F1F;
  --border-default: #2A2A2A;
  --border-strong: #333333;
  --border-focus: #8251EE;
  
  /* Brand - Use Sparingly */
  --brand-primary: #8251EE;
  --brand-hover: #9366F5;
  --brand-light: #A37EF5;
  --brand-muted: rgba(130, 81, 238, 0.2);
  
  /* Semantic */
  --success: #10B981;
  --success-muted: rgba(16, 185, 129, 0.15);
  --warning: #F59E0B;
  --warning-muted: rgba(245, 158, 11, 0.15);
  --error: #EF4444;
  --error-muted: rgba(239, 68, 68, 0.15);
  --info: #3B82F6;
  
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  
  /* Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, \\'Segoe UI\\', Roboto, sans-serif;
  --text-xs: 12px;
  --text-sm: 13px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 20px;
  --text-2xl: 24px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-focus: 0 0 0 2px rgba(130, 81, 238, 0.25);
  
  /* Z-Index */
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 300;
  --z-toast: 400;
  --z-tooltip: 500;
}
```
'''

# components.md content
components_md = '''# Foundry NextGen Components

## Buttons

### Primary Button
Purple background - use for main actions only.

```jsx
<button className="btn btn-primary">
  Create Agent
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary {
  background: var(--brand-primary);
  color: white;
  border: none;
}
.btn-primary:hover { background: var(--brand-hover); }
.btn-primary:active { background: #7344D8; }
```

### Secondary Button
Grey outline - NOT purple. Use for secondary actions.

```jsx
<button className="btn btn-secondary">
  Cancel
</button>
```

```css
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
}
.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--text-secondary);
}
```

### Ghost Button
Minimal style for tertiary actions.

```css
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: none;
}
.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

### Icon Button

```jsx
<button className="btn-icon" aria-label="More options">
  <MoreVertical size={16} />
</button>
```

```css
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-secondary);
  border: none;
  cursor: pointer;
}
.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

## Data Table

```jsx
<table className="data-table">
  <thead>
    <tr>
      <th></th>
      <th>Name</th>
      <th>Description</th>
      <th>Created on</th>
    </tr>
  </thead>
  <tbody>
    {items.map(item => (
      <tr key={item.id} className={selected === item.id ? \\' selected\\' : \\'\\'}>
        <td>
          <input type="radio" checked={selected === item.id} />
        </td>
        <td><a href="#" className="link">{item.name}</a></td>
        <td className="text-secondary">{item.description}</td>
        <td className="text-secondary">{item.createdAt}</td>
      </tr>
    ))}
  </tbody>
</table>
```

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-default);
  background: transparent;
}

.data-table td {
  padding: 12px 16px;
  font-size: var(--text-base);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
  background: transparent;
}

.data-table tbody tr:hover td {
  background: var(--bg-surface);
}

/* Selected row - purple indicator on left edge only */
.data-table tbody tr.selected td {
  background: var(--bg-surface);
}
.data-table tbody tr.selected td:first-child {
  box-shadow: inset 3px 0 0 var(--brand-primary);
}

.link {
  color: var(--text-link);
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}
```

## Tabs

```jsx
<div className="tabs">
  {tabs.map(tab => (
    <button
      key={tab.id}
      className={`tab ${activeTab === tab.id ? \\'active\\' : \\'\\'}`}
      onClick={() => setActiveTab(tab.id)}
    >
      {tab.label}
    </button>
  ))}
</div>
```

```css
.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--border-default);
  padding: 0 24px;
}

.tab {
  padding: 12px 0;
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
}

.tab:hover {
  color: var(--text-primary);
}

.tab.active {
  color: var(--text-primary);
  font-weight: 500;
}

/* Purple underline for active tab */
.tab.active::after {
  content: \\'\\';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--brand-primary);
  border-radius: 1px 1px 0 0;
}
```

## Cards

Cards use neutral grey backgrounds, NOT purple.

```jsx
<div className="card">
  <div className="card-header">
    <h3 className="card-title">Deployment info</h3>
  </div>
  <div className="card-content">
    {/* Content */}
  </div>
</div>
```

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.card-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-content {
  padding: 16px 20px;
}
```

## Form Inputs

```jsx
<div className="form-field">
  <label className="form-label">
    Name <span className="required">*</span>
  </label>
  <input
    type="text"
    className="input"
    placeholder="Enter name"
  />
  <p className="form-hint">A unique identifier for this resource.</p>
</div>
```

```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--error);
}

.input {
  padding: 10px 12px;
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input::placeholder {
  color: var(--text-muted);
}

.input:hover {
  border-color: var(--border-strong);
}

.input:focus {
  border-color: var(--brand-primary);
  box-shadow: var(--shadow-focus);
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin: 0;
}
```

## Select / Dropdown

```css
.select {
  appearance: none;
  padding: 10px 36px 10px 12px;
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-surface) url(\\'data:image/svg+xml,...\\') no-repeat right 12px center;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.select:hover {
  border-color: var(--border-strong);
}

.select:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: var(--shadow-focus);
}
```

## Modal / Dialog

```jsx
<div className="modal-overlay">
  <div className="modal">
    <div className="modal-header">
      <h2 className="modal-title">Create a knowledge source</h2>
      <button className="btn-icon modal-close">
        <X size={20} />
      </button>
    </div>
    <div className="modal-body">
      {/* Form content */}
    </div>
    <div className="modal-footer">
      <button className="btn btn-secondary">Cancel</button>
      <button className="btn btn-primary">Create</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 540px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  color: var(--text-muted);
}
.modal-close:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}
```

## Sidebar Navigation

```jsx
<aside className="sidebar">
  <div className="sidebar-brand">
    <FoundryLogo />
  </div>
  <nav className="sidebar-nav">
    {navItems.map(item => (
      <a
        key={item.id}
        href={item.href}
        className={`sidebar-item ${active === item.id ? \\'active\\' : \\'\\'}`}
        title={item.label}
      >
        <item.icon size={20} />
      </a>
    ))}
  </nav>
</aside>
```

```css
.sidebar {
  width: 56px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  padding: 12px 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  margin-bottom: 8px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 8px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.15s ease;
}

.sidebar-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Active item - purple icon only, subtle background */
.sidebar-item.active {
  background: var(--bg-surface);
  color: var(--brand-light);
}
```

## Search Input

```jsx
<div className="search-input">
  <Search size={16} className="search-icon" />
  <input
    type="text"
    placeholder="Search"
    className="search-field"
  />
</div>
```

```css
.search-input {
  position: relative;
  width: 240px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-field {
  width: 100%;
  padding: 8px 12px 8px 36px;
  font-size: var(--text-sm);
  color: var(--text-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
}

.search-field::placeholder {
  color: var(--text-muted);
}

.search-field:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: var(--shadow-focus);
}
```

## Pagination

```jsx
<div className="pagination">
  <span className="pagination-info">1-10 of 100</span>
  <div className="pagination-controls">
    <button className="btn-icon" disabled><ChevronLeft size={16} /></button>
    <button className="pagination-page active">1</button>
    <button className="pagination-page">2</button>
    <button className="pagination-page">3</button>
    <button className="btn-icon"><ChevronRight size={16} /></button>
  </div>
</div>
```

```css
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-page {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.pagination-page:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.pagination-page.active {
  background: var(--bg-surface);
  color: var(--text-primary);
  font-weight: 500;
}
```

## Badge / Tag

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius-sm);
}

.badge-default {
  background: var(--bg-surface);
  color: var(--text-secondary);
}

.badge-success {
  background: var(--success-muted);
  color: var(--success);
}

.badge-warning {
  background: var(--warning-muted);
  color: var(--warning);
}

.badge-error {
  background: var(--error-muted);
  color: var(--error);
}

/* Purple badge - use sparingly */
.badge-brand {
  background: var(--brand-muted);
  color: var(--brand-light);
}
```

## Checkbox and Radio

```css
.checkbox,
.radio {
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  cursor: pointer;
}

.checkbox {
  border-radius: var(--radius-sm);
}

.radio {
  border-radius: 50%;
}

.checkbox:checked,
.radio:checked {
  background: var(--brand-primary);
  border-color: var(--brand-primary);
}

.checkbox:checked::after {
  content: \\'✓\\';
  display: block;
  text-align: center;
  color: white;
  font-size: 12px;
  line-height: 14px;
}

.radio:checked::after {
  content: \\'\\';
  display: block;
  width: 6px;
  height: 6px;
  margin: 4px;
  background: white;
  border-radius: 50%;
}
```
'''

# patterns.md content  
patterns_md = '''# Foundry NextGen Patterns

## Page Layouts

### List Page (Entity Browser)

The standard layout for browsing entities with search, tabs, and data table.

```jsx
function EntityListPage() {
  const [activeTab, setActiveTab] = useState(\\'all\\');
  const [searchQuery, setSearchQuery] = useState(\\'\\');
  const [selected, setSelected] = useState(null);

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Entity list <span className="count">(100)</span></h1>
      </header>

      <div className="tabs">
        <button className={`tab ${activeTab === \\'all\\' ? \\'active\\' : \\'\\'}`}>
          All
        </button>
        <button className={`tab ${activeTab === \\'recent\\' ? \\'active\\' : \\'\\'}`}>
          Recent
        </button>
      </div>

      <div className="toolbar">
        <SearchInput value={searchQuery} onChange={setSearchQuery} />
        <button className="btn btn-primary">Create</button>
      </div>

      <DataTable
        data={filteredData}
        selected={selected}
        onSelect={setSelected}
      />

      <Pagination
        page={1}
        pageSize={10}
        total={100}
      />
    </div>
  );
}
```

```css
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-header {
  padding: 24px 24px 16px;
}

.page-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.page-title .count {
  font-weight: 400;
  color: var(--text-secondary);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
}
```

### Detail Page

Split layout with main content and detail panel.

```jsx
function DetailPage() {
  return (
    <div className="detail-layout">
      <div className="detail-main">
        <header className="detail-header">
          <h1 className="detail-title">Resource Name</h1>
          <div className="detail-actions">
            <button className="btn btn-primary">Button</button>
            <button className="btn btn-secondary">Button</button>
          </div>
        </header>

        <div className="tabs">
          <button className="tab active">First tab</button>
          <button className="tab">Second tab</button>
        </div>

        <div className="detail-content">
          <Card title="Deployment info">
            <InfoGrid>
              <InfoItem label="Name" value="GPT-5" />
              <InfoItem label="Status" value="Succeeded" />
            </InfoGrid>
          </Card>
        </div>
      </div>

      <aside className="detail-sidebar">
        <h2 className="sidebar-title">Target URI</h2>
        <CopyField value="endpoint-aip-2i93..." />
        
        <h2 className="sidebar-title">Key</h2>
        <SecretField value="••••••••••••••" />
        
        <CodeSnippet language="python" />
      </aside>
    </div>
  );
}
```

```css
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  height: 100%;
}

.detail-main {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  overflow: hidden;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
}

.detail-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.detail-sidebar {
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-page);
}

.sidebar-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}
```

## App Shell

Complete application layout with top bar and sidebar.

```jsx
function AppShell({ children }) {
  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-left">
          <FoundryLogo />
          <span className="topbar-divider">/</span>
          <ProjectSelector />
        </div>
        <div className="topbar-right">
          <GlobalSearch />
          <NotificationBell />
          <UserAvatar />
        </div>
      </header>

      <div className="app-body">
        <Sidebar />
        <main className="app-main">
          {children}
        </main>
      </div>
    </div>
  );
}
```

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  color: var(--text-primary);
}

.topbar {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border-subtle);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-divider {
  color: var(--text-muted);
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow-y: auto;
}
```

## Empty States

```jsx
function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Icon size={48} />
      </div>
      <h3 className="empty-title">{title}</h3>
      <p className="empty-description">{description}</p>
      {action && (
        <button className="btn btn-primary">{action}</button>
      )}
    </div>
  );
}
```

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
}

.empty-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  max-width: 360px;
}
```

## Loading States

```jsx
function LoadingState() {
  return (
    <div className="loading-state">
      <div className="spinner" />
      <span className="loading-text">Loading...</span>
    </div>
  );
}

function SkeletonRow() {
  return (
    <tr className="skeleton-row">
      <td><div className="skeleton skeleton-radio" /></td>
      <td><div className="skeleton skeleton-text" /></td>
      <td><div className="skeleton skeleton-text-long" /></td>
      <td><div className="skeleton skeleton-text" /></td>
    </tr>
  );
}
```

```css
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-default);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.skeleton {
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton-radio {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.skeleton-text {
  width: 80px;
  height: 14px;
}

.skeleton-text-long {
  width: 160px;
  height: 14px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

## Info Grid

Key-value display pattern used in detail panels.

```jsx
function InfoGrid({ children }) {
  return <dl className="info-grid">{children}</dl>;
}

function InfoItem({ label, value }) {
  return (
    <>
      <dt className="info-label">{label}</dt>
      <dd className="info-value">{value}</dd>
    </>
  );
}
```

```css
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 24px;
  margin: 0;
}

.info-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.info-value {
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0;
}
```

## Code Snippet

```jsx
function CodeSnippet({ language, code, showCopy = true }) {
  return (
    <div className="code-snippet">
      <div className="code-header">
        <span className="code-language">{language}</span>
        {showCopy && (
          <button className="btn-icon" title="Copy">
            <Copy size={14} />
          </button>
        )}
      </div>
      <pre className="code-content">
        <code>{code}</code>
      </pre>
    </div>
  );
}
```

```css
.code-snippet {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
}

.code-language {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.code-content {
  margin: 0;
  padding: 16px;
  font-family: \\'SF Mono\\', \\'Fira Code\\', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  overflow-x: auto;
}
```

## Copy Field

Field with copy-to-clipboard functionality.

```jsx
function CopyField({ value, masked = false }) {
  const [copied, setCopied] = useState(false);
  const [revealed, setRevealed] = useState(!masked);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="copy-field">
      <input
        type={revealed ? \\'text\\' : \\'password\\'}
        value={value}
        readOnly
        className="copy-field-input"
      />
      {masked && (
        <button
          className="btn-icon"
          onClick={() => setRevealed(!revealed)}
        >
          {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
        </button>
      )}
      <button className="btn-icon" onClick={handleCopy}>
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
    </div>
  );
}
```

```css
.copy-field {
  display: flex;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.copy-field-input {
  flex: 1;
  padding: 10px 12px;
  font-size: var(--text-sm);
  font-family: \\'SF Mono\\', monospace;
  color: var(--text-primary);
  background: transparent;
  border: none;
  outline: none;
}

.copy-field .btn-icon {
  border-radius: 0;
}
```

## Chart Theming (Recharts)

```jsx
const chartColors = {
  primary: \\'#8251EE\\',
  secondary: \\'#A37EF5\\',
  grid: \\'#2A2A2A\\',
  text: \\'#A1A1A1\\',
  tooltip: {
    bg: \\'#242424\\',
    border: \\'#333333\\',
  }
};

function FoundryAreaChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={chartColors.primary} stopOpacity={0.3} />
            <stop offset="100%" stopColor={chartColors.primary} stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="name"
          axisLine={false}
          tickLine={false}
          tick={{ fill: chartColors.text, fontSize: 12 }}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: chartColors.text, fontSize: 12 }}
        />
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={chartColors.grid}
          vertical={false}
        />
        <Tooltip
          contentStyle={{
            background: chartColors.tooltip.bg,
            border: `1px solid ${chartColors.tooltip.border}`,
            borderRadius: 6,
            color: \\'#fff\\',
          }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={chartColors.primary}
          fill="url(#colorValue)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
```

## Collapsible Section

```jsx
function CollapsibleSection({ title, defaultExpanded = false, children }) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className="collapsible">
      <button
        className="collapsible-trigger"
        onClick={() => setExpanded(!expanded)}
      >
        <ChevronRight
          size={16}
          className={`collapsible-icon ${expanded ? \\'expanded\\' : \\'\\'}`}
        />
        <span>{title}</span>
      </button>
      {expanded && (
        <div className="collapsible-content">
          {children}
        </div>
      )}
    </div>
  );
}
```

```css
.collapsible-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.collapsible-trigger:hover {
  color: var(--text-link);
}

.collapsible-icon {
  color: var(--text-muted);
  transition: transform 0.2s ease;
}

.collapsible-icon.expanded {
  transform: rotate(90deg);
}

.collapsible-content {
  padding-left: 24px;
}
```
'''

# Write files
with open(os.path.join(base_dir, 'SKILL.md'), 'w') as f:
    f.write(skill_md)

os.makedirs(os.path.join(base_dir, 'references'), exist_ok=True)

with open(os.path.join(base_dir, 'references', 'design-tokens.md'), 'w') as f:
    f.write(design_tokens_md)

with open(os.path.join(base_dir, 'references', 'components.md'), 'w') as f:
    f.write(components_md)

with open(os.path.join(base_dir, 'references', 'patterns.md'), 'w') as f:
    f.write(patterns_md)

print("All skill files updated successfully!")
print(f"- {os.path.join(base_dir, 'SKILL.md')}")
print(f"- {os.path.join(base_dir, 'references', 'design-tokens.md')}")  
print(f"- {os.path.join(base_dir, 'references', 'components.md')}")
print(f"- {os.path.join(base_dir, 'references', 'patterns.md')}")
