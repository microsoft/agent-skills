# Frontend UI Dark Theme Acceptance Criteria (TypeScript)

**Stack**: React, Tailwind CSS, Framer Motion, Vite
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Core React Imports

#### ✅ CORRECT: React Imports
```typescript
import React from 'react';
import { useState, useEffect, useCallback, memo } from 'react';
import ReactDOM from 'react-dom/client';
```

### 1.2 Router Imports

#### ✅ CORRECT: React Router Imports
```typescript
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
```

### 1.3 Animation Imports

#### ✅ CORRECT: Framer Motion Imports
```typescript
import { motion, AnimatePresence } from 'framer-motion';
```

### 1.4 Utility Imports

#### ✅ CORRECT: Class Merging
```typescript
import clsx from 'clsx';
```

### 1.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using outdated imports
```typescript
// WRONG - outdated createRoot API
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// WRONG - using require
const React = require('react');
```

---

## 2. Color System Patterns

### 2.1 ✅ CORRECT: Brand Colors
```typescript
// Brand purple palette
const brandColors = {
  brand: '#8251EE',
  brandHover: '#9366F5',
  brandLight: '#A37EF5',
  brandSubtle: 'rgba(130, 81, 238, 0.15)',
};
```

### 2.2 ✅ CORRECT: Neutral Background Colors
```typescript
// Dark theme neutral backgrounds (bg1 darkest to bg6 lightest)
<div className="bg-neutral-bg1">Page background</div>
<div className="bg-neutral-bg2">Card background</div>
<div className="bg-neutral-bg3">Elevated surface</div>
<div className="bg-neutral-bg4">Hover state</div>
```

### 2.3 ✅ CORRECT: Text Colors
```typescript
<h1 className="text-text-primary">Primary text (white)</h1>
<p className="text-text-secondary">Secondary text (gray)</p>
<span className="text-text-muted">Muted text (dark gray)</span>
```

### 2.4 ✅ CORRECT: Border Colors
```typescript
<div className="border border-border-subtle">Subtle border</div>
<div className="border border-border">Default border</div>
<div className="border border-border-strong">Strong border</div>
```

### 2.5 ✅ CORRECT: Status Colors
```typescript
<span className="text-status-success">Success</span>
<span className="text-status-warning">Warning</span>
<span className="text-status-error">Error</span>
<span className="text-status-info">Info</span>
```

### 2.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using light theme colors
```typescript
// WRONG - light theme background
<div className="bg-white">...</div>

// WRONG - light theme text
<p className="text-gray-900">...</p>
```

---

## 3. Glass Effect Patterns

### 3.1 ✅ CORRECT: Glass Card
```typescript
<div className="glass-card p-6">
  <h2 className="text-lg font-semibold text-text-primary">Card Title</h2>
  <p className="text-text-secondary mt-2">Card content goes here.</p>
</div>
```

### 3.2 ✅ CORRECT: Glass Panel
```typescript
<aside className="glass-panel w-64 h-screen p-4">
  <nav className="space-y-2">
    {/* Navigation items */}
  </nav>
</aside>
```

### 3.3 ✅ CORRECT: Glass Overlay (Modal)
```typescript
<div className="fixed inset-0 glass-overlay flex items-center justify-center z-50">
  <div className="glass-card p-6 max-w-md w-full mx-4">
    {/* Modal content */}
  </div>
</div>
```

### 3.4 ✅ CORRECT: Glass Input
```typescript
<input className="glass-input px-4 py-2 rounded-lg w-full" />
```

---

## 4. Animation Patterns

### 4.1 ✅ CORRECT: Fade In Variant
```typescript
const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.2 },
};

<motion.div {...fadeIn}>Content</motion.div>
```

### 4.2 ✅ CORRECT: Slide Up Variant
```typescript
const slideUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
  transition: { duration: 0.3, ease: 'easeOut' },
};
```

### 4.3 ✅ CORRECT: Scale on Hover
```typescript
const scaleOnHover = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: { type: 'spring', stiffness: 400, damping: 17 },
};
```

### 4.4 ✅ CORRECT: Stagger Children
```typescript
const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};
```

### 4.5 ✅ CORRECT: Page Transition
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
>
  {children}
</motion.div>
```

### 4.6 ✅ CORRECT: AnimatePresence for Exit
```typescript
<AnimatePresence mode="wait">
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
  </Routes>
</AnimatePresence>
```

---

## 5. Component Patterns

### 5.1 ✅ CORRECT: Button Component
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

function Button({ variant = 'primary', size = 'md', children, onClick }: ButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={clsx(
        'rounded-lg font-medium transition-colors',
        variant === 'primary' && 'bg-brand hover:bg-brand-hover text-white',
        variant === 'secondary' && 'bg-neutral-bg3 hover:bg-neutral-bg4 text-text-primary',
        variant === 'ghost' && 'hover:bg-neutral-bg3 text-text-secondary',
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2 text-sm',
        size === 'lg' && 'px-6 py-3 text-base',
      )}
      onClick={onClick}
    >
      {children}
    </motion.button>
  );
}
```

### 5.2 ✅ CORRECT: Card Component
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx('glass-card p-6', className)}
    >
      {children}
    </motion.div>
  );
}
```

---

## 6. Typography Patterns

### 6.1 ✅ CORRECT: Typography Classes
```typescript
// Page title
<h1 className="text-2xl font-semibold text-text-primary">Page Title</h1>

// Section title
<h2 className="text-lg font-semibold text-text-primary">Section Title</h2>

// Card title
<h3 className="text-base font-medium text-text-primary">Card Title</h3>

// Body text
<p className="text-sm text-text-secondary">Body text content</p>

// Caption
<span className="text-xs text-text-muted">Caption text</span>

// Label
<label className="text-sm font-medium text-text-secondary">Label</label>
```

---

## 7. Layout Patterns

### 7.1 ✅ CORRECT: App Shell
```typescript
function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-neutral-bg1 flex">
      <Sidebar />
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

### 7.2 ✅ CORRECT: Page Header
```typescript
function PageHeader({ title, description }: { title: string; description?: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
      {description && (
        <p className="text-sm text-text-secondary mt-1">{description}</p>
      )}
    </div>
  );
}
```

---

## 8. Focus and Accessibility Patterns

### 8.1 ✅ CORRECT: Focus Visible
```css
*:focus-visible {
  @apply outline-none ring-2 ring-brand ring-offset-2 ring-offset-neutral-bg1;
}
```

### 8.2 ✅ CORRECT: Dark Color Scheme
```css
html {
  color-scheme: dark;
}
```

---

## 9. Tailwind Configuration Patterns

### 9.1 ✅ CORRECT: Custom Colors in Config
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#8251EE',
          hover: '#9366F5',
        },
        neutral: {
          bg1: 'hsl(240, 6%, 10%)',
          bg2: 'hsl(240, 5%, 12%)',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#A1A1AA',
        },
      },
    },
  },
};
```

---

## 10. Anti-Patterns (ERRORS)

### 10.1 ❌ INCORRECT: Light Theme Usage
```typescript
// WRONG - light backgrounds
<div className="bg-white">...</div>
<div className="bg-gray-100">...</div>
```

### 10.2 ❌ INCORRECT: Missing Motion Components
```typescript
// WRONG - static hover without motion
<button className="hover:scale-105">...</button>

// CORRECT - with motion
<motion.button whileHover={{ scale: 1.05 }}>...</motion.button>
```

### 10.3 ❌ INCORRECT: Missing AnimatePresence
```typescript
// WRONG - no exit animations
{isOpen && <Modal />}

// CORRECT - with AnimatePresence
<AnimatePresence>
  {isOpen && <Modal />}
</AnimatePresence>
```
