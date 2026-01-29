---
name: nextgen-frontend-ts
description: Build elegant frontend UIs following Microsoft Foundry's NextGen Design System using Vite + React + pnpm + Framer Motion. Use when creating dashboards, agent builders, data grids, entity management interfaces, or any application matching Foundry's refined dark-themed aesthetic.
---

# Microsoft Foundry NextGen Frontend Skill

Build elegant, production-ready interfaces following Microsoft Foundry's NextGen Design System - a refined **neutral dark-themed** design language with **minimal purple accents** and **subtle animations**.

## ⚠️ CRITICAL: Color Usage Rules

**Purple (#8251EE / #A37EF5) is ONLY for:**
- Primary action buttons (filled background)
- Active tab indicators (2px underline)
- Row selection indicators (left border bar)
- Active sidebar navigation icons
- Links and interactive text
- Progress indicators and sliders

**Everything else uses NEUTRAL DARK GREYS:**
- Backgrounds: Near-black (#0A0A0A, #0D0D0D)
- Cards/Surfaces: Dark grey (#141414, #1C1C1C) with **NO visible borders** or very subtle ones
- Text: White (#FFFFFF), grey (#A1A1A1), muted (#6B6B6B)
- Borders: **Mostly invisible** or very subtle (#1F1F1F)

## Preferred Stack

```bash
pnpm create vite@latest my-foundry-app --template react-ts
cd my-foundry-app
pnpm install
pnpm add framer-motion lucide-react
```

**Required packages:**
- `framer-motion` - for subtle, elegant animations
- `lucide-react` - for icons

## ⚠️ CRITICAL: Spacing & Padding Rules

**Consistent spacing is non-negotiable. Use the spacing scale:**

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

**Standard padding patterns:**
| Element | Padding |
|---------|---------|
| Page content | 32px (--space-8) |
| Card | 20px (--space-5) |
| Card header | 16px 20px |
| Button | 8px 16px |
| Input | 10px 12px |
| Table cell | 12px 16px |
| Modal body | 24px |
| Badge/Tag | 4px 10px |

**Grid gaps:**
| Layout | Gap |
|--------|-----|
| Card grid | 16px (--space-4) |
| Form fields | 20px (--space-5) |
| Button group | 12px (--space-3) |
| Tag group | 8px (--space-2) |

## Core Design Tokens

```css
:root {
  /* BACKGROUNDS - Neutral Darks */
  --bg-page: #0A0A0A;
  --bg-sidebar: #0D0D0D;
  --bg-card: #141414;
  --bg-surface: #1C1C1C;
  --bg-elevated: #242424;
  --bg-hover: rgba(255, 255, 255, 0.05);
  --bg-active: rgba(255, 255, 255, 0.08);

  /* TEXT */
  --text-primary: #FFFFFF;
  --text-secondary: #A1A1A1;
  --text-muted: #6B6B6B;
  --text-disabled: #4A4A4A;
  --text-link: #A37EF5;

  /* BRAND - Use Sparingly! */
  --brand-primary: #8251EE;
  --brand-hover: #9366F5;
  --brand-light: #A37EF5;

  /* BORDERS - Keep Subtle! */
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.12);

  /* STATUS */
  --success: #10B981;
  --success-bg: rgba(16, 185, 129, 0.12);
  --warning: #F59E0B;
  --warning-bg: rgba(245, 158, 11, 0.12);
  --error: #EF4444;
  --error-bg: rgba(239, 68, 68, 0.12);
  --info: #3B82F6;
  --info-bg: rgba(59, 130, 246, 0.12);

  /* RADIUS */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
}
```

## ⚠️ CRITICAL: Animation with Framer Motion

**Always add subtle animations. Never skip animations.**

```jsx
import { motion } from 'framer-motion';

// Page/container fade in
const pageVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' }
  }
};

// Stagger children (for lists, grids)
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
};

// Individual item animation
const itemVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut' }
  }
};

// Hover scale for cards/buttons
const hoverScale = {
  whileHover: { scale: 1.01 },
  whileTap: { scale: 0.99 },
  transition: { duration: 0.15 }
};
```

**Standard animation patterns:**

```jsx
// Page wrapper - always animate page entry
<motion.div
  initial="hidden"
  animate="visible"
  variants={pageVariants}
  className="page"
>
  {children}
</motion.div>

// Card grid with stagger
<motion.div
  variants={containerVariants}
  initial="hidden"
  animate="visible"
  className="card-grid"
>
  {items.map(item => (
    <motion.div key={item.id} variants={itemVariants}>
      <Card {...item} />
    </motion.div>
  ))}
</motion.div>

// Interactive card with hover
<motion.div
  className="card"
  whileHover={{ scale: 1.01, backgroundColor: 'rgba(255,255,255,0.02)' }}
  whileTap={{ scale: 0.99 }}
  transition={{ duration: 0.15 }}
>
  {content}
</motion.div>

// Button with press feedback
<motion.button
  className="btn btn-primary"
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.1 }}
>
  Create
</motion.button>

// Modal with backdrop
<motion.div
  className="modal-overlay"
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>
  <motion.div
    className="modal"
    initial={{ opacity: 0, scale: 0.95, y: 10 }}
    animate={{ opacity: 1, scale: 1, y: 0 }}
    exit={{ opacity: 0, scale: 0.95, y: 10 }}
    transition={{ duration: 0.2, ease: 'easeOut' }}
  >
    {content}
  </motion.div>
</motion.div>
```

## Components Quick Reference

For full component implementations with JSX and CSS, see [references/components.md](references/components.md).

| Component | Key Rule |
|-----------|----------|
| Card | NO visible borders, subtle shadow, hover scale 1.01 |
| Button | Primary = purple, Secondary = transparent with border |
| Badge | Status colors only (success, warning, error, info) |
| Tag | Neutral grey background, uppercase, 11px |
| Grid | 16px gap, 32px page padding |

## Layout Structure

```jsx
// Standard app layout
<div className="app-layout">
  <Sidebar />           {/* 56px width, bg-sidebar */}
  <main className="main-content">
    <TopBar />          {/* 48px height */}
    <motion.div className="page-content" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {children}
    </motion.div>
  </main>
</div>
```

For detailed layout patterns, see [references/patterns.md](references/patterns.md).

## Critical Rules

**Don'ts ❌**
- Visible card borders (blend into background)
- Inconsistent padding (use spacing scale)
- Skip animations (every list, modal, page needs motion)
- Purple for cards/backgrounds (neutral greys only)
- Skip hover states (everything interactive needs feedback)

**Do's ✅**
- Use Framer Motion for all animations
- Use spacing scale: 4, 8, 12, 16, 20, 24, 32px
- 32px page padding, 16px card grid gap
- Transparent or very subtle borders
- Stagger list/grid item animations

## References

| File | Contents |
|------|----------|
| [references/design-tokens.md](references/design-tokens.md) | Full CSS variables, colors, spacing |
| [references/components.md](references/components.md) | Card, Button, Badge, Tag, Input implementations |
| [references/patterns.md](references/patterns.md) | Layout, Grid, Modal, Table patterns |
