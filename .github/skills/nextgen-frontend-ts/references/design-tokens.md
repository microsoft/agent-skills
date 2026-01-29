# Foundry NextGen Design Tokens

Complete CSS custom properties for the Foundry design system.

## Full Token Set

```css
:root {
  /* ===== SPACING SCALE ===== */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* ===== BACKGROUNDS - Neutral Darks ===== */
  --bg-page: #0A0A0A;
  --bg-sidebar: #0D0D0D;
  --bg-topbar: #0D0D0D;
  --bg-card: #141414;
  --bg-surface: #1C1C1C;
  --bg-elevated: #242424;
  --bg-hover: rgba(255, 255, 255, 0.05);
  --bg-active: rgba(255, 255, 255, 0.08);
  --bg-selected: rgba(255, 255, 255, 0.04);

  /* ===== TEXT ===== */
  --text-primary: #FFFFFF;
  --text-secondary: #A1A1A1;
  --text-muted: #6B6B6B;
  --text-disabled: #4A4A4A;
  --text-link: #A37EF5;

  /* ===== BRAND (Use Sparingly!) ===== */
  --brand-primary: #8251EE;
  --brand-hover: #9366F5;
  --brand-light: #A37EF5;
  --brand-muted: rgba(130, 81, 238, 0.15);

  /* ===== BORDERS - Subtle/Transparent ===== */
  --border-none: transparent;
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.12);
  --border-focus: var(--brand-primary);

  /* ===== STATUS COLORS ===== */
  --success: #10B981;
  --success-bg: rgba(16, 185, 129, 0.12);
  --warning: #F59E0B;
  --warning-bg: rgba(245, 158, 11, 0.12);
  --error: #EF4444;
  --error-bg: rgba(239, 68, 68, 0.12);
  --info: #3B82F6;
  --info-bg: rgba(59, 130, 246, 0.12);

  /* ===== BORDER RADIUS ===== */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;

  /* ===== SHADOWS ===== */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.4);
  --shadow-focus: 0 0 0 2px rgba(130, 81, 238, 0.2);

  /* ===== TYPOGRAPHY ===== */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', monospace;

  --text-xs: 11px;
  --text-sm: 12px;
  --text-base: 13px;
  --text-md: 14px;
  --text-lg: 15px;
  --text-xl: 16px;
  --text-2xl: 20px;
  --text-3xl: 24px;

  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;

  /* ===== TRANSITIONS ===== */
  --transition-fast: 0.1s ease;
  --transition-base: 0.15s ease;
  --transition-slow: 0.3s ease;

  /* ===== Z-INDEX ===== */
  --z-dropdown: 50;
  --z-sticky: 60;
  --z-modal: 100;
  --z-toast: 110;
}
```

## Base Styles

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--text-primary);
  background: var(--bg-page);
}

a {
  color: var(--text-link);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button {
  font-family: inherit;
  cursor: pointer;
}

input, textarea, select {
  font-family: inherit;
}
```

## Color Usage Guide

| Element | Background | Border | Text |
|---------|------------|--------|------|
| Page | #0A0A0A | - | #FFFFFF |
| Sidebar | #0D0D0D | rgba(255,255,255,0.06) | #6B6B6B |
| Card | #141414 | transparent → hover: rgba(255,255,255,0.06) | #FFFFFF |
| Modal | #141414 | rgba(255,255,255,0.08) | #FFFFFF |
| Input | #1C1C1C | rgba(255,255,255,0.08) | #FFFFFF |
| Tag | #1C1C1C | - | #A1A1A1 |
| Primary Button | #8251EE | - | #FFFFFF |
| Secondary Button | transparent | rgba(255,255,255,0.12) | #FFFFFF |

## Spacing Usage Guide

| Element | Value |
|---------|-------|
| Page padding | 32px (--space-8) |
| Card padding | 20px (--space-5) |
| Card grid gap | 16px (--space-4) |
| Button padding | 8px 16px |
| Input padding | 10px 12px |
| Tag padding | 4px 10px |
| Modal body padding | 24px (--space-6) |
| Form field gap | 20px (--space-5) |
| Section margin | 24px (--space-6) |
