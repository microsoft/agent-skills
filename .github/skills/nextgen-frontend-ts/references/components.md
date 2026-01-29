# Foundry NextGen Components

All components use **Framer Motion** for animations and follow **strict spacing rules**.

## Animation Variants (Required)

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Reusable variants - put in a shared file
export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3, ease: 'easeOut' } }
};

export const fadeInUp = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } }
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 }
  }
};

export const scaleOnHover = {
  whileHover: { scale: 1.01 },
  whileTap: { scale: 0.99 },
  transition: { duration: 0.15 }
};
```

## Card

**Cards have NO visible borders.** They blend into the background.

```jsx
import { motion } from 'framer-motion';

function Card({ title, description, status, tags, meta, href }) {
  return (
    <motion.div 
      className="card"
      variants={fadeInUp}
      whileHover={{ 
        scale: 1.01,
        backgroundColor: 'rgba(255, 255, 255, 0.02)'
      }}
      transition={{ duration: 0.15 }}
    >
      <div className="card-header">
        <h3 className="card-title">{title}</h3>
        {status && <Badge variant={status.variant}>{status.label}</Badge>}
      </div>
      
      <p className="card-description">{description}</p>
      
      {tags && (
        <div className="card-tags">
          {tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
        </div>
      )}
      
      {meta && <div className="card-meta">{meta}</div>}
    </motion.div>
  );
}
```

```css
.card {
  background: var(--bg-card);  /* #141414 */
  border-radius: var(--radius-lg);  /* 8px */
  padding: 20px;  /* var(--space-5) */
  border: 1px solid transparent;  /* NO visible border */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.card:hover {
  border-color: rgba(255, 255, 255, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;  /* var(--space-3) */
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.card-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px;  /* var(--space-4) bottom */
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;  /* var(--space-2) */
  margin-bottom: 16px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
```

## Card Grid

```jsx
<motion.div
  className="card-grid"
  variants={staggerContainer}
  initial="hidden"
  animate="visible"
>
  {items.map(item => (
    <motion.div key={item.id} variants={fadeInUp}>
      <Card {...item} />
    </motion.div>
  ))}
</motion.div>
```

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;  /* var(--space-4) */
}

/* Fixed column variants */
.card-grid-4 { grid-template-columns: repeat(4, 1fr); }
.card-grid-3 { grid-template-columns: repeat(3, 1fr); }
.card-grid-2 { grid-template-columns: repeat(2, 1fr); }
```

## Buttons

```jsx
<motion.button
  className="btn btn-primary"
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.1 }}
>
  Create
</motion.button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;  /* Consistent padding */
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;  /* var(--radius-md) */
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary {
  background: var(--brand-primary);  /* #8251EE */
  color: white;
  border: none;
}
.btn-primary:hover { background: var(--brand-hover); }

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.12);
}
.btn-secondary:hover { background: rgba(255, 255, 255, 0.05); }

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: none;
}
.btn-ghost:hover { 
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  border: none;
}
.btn-icon:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}
```

## Tags

**Tags are subtle, not colorful. Grey background.**

```css
.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  border-radius: 4px;
  background: var(--bg-surface);  /* #1C1C1C */
  color: var(--text-secondary);  /* #A1A1A1 */
}

/* Special tag variants for services */
.tag-github { background: rgba(255, 255, 255, 0.08); }
.tag-sdk { background: rgba(255, 255, 255, 0.06); }
```

## Badges (Status)

**Badges use semantic colors with low opacity backgrounds.**

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  border-radius: 4px;
  flex-shrink: 0;
}

.badge-success {
  background: rgba(16, 185, 129, 0.12);
  color: #10B981;
}

.badge-info {
  background: rgba(59, 130, 246, 0.12);
  color: #3B82F6;
}

.badge-warning {
  background: rgba(245, 158, 11, 0.12);
  color: #F59E0B;
}

.badge-error {
  background: rgba(239, 68, 68, 0.12);
  color: #EF4444;
}
```

## Tabs

```jsx
<nav className="tabs">
  {tabs.map(tab => (
    <motion.button
      key={tab.id}
      className={`tab ${activeTab === tab.id ? 'active' : ''}`}
      onClick={() => setActiveTab(tab.id)}
      whileHover={{ color: '#FFFFFF' }}
    >
      {tab.label}
      {activeTab === tab.id && (
        <motion.div 
          className="tab-indicator"
          layoutId="activeTab"
          transition={{ duration: 0.2 }}
        />
      )}
    </motion.button>
  ))}
</nav>
```

```css
.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 24px;
}

.tab {
  position: relative;
  padding: 12px 0;
  font-size: 14px;
  color: var(--text-muted);  /* #6B6B6B */
  background: none;
  border: none;
  cursor: pointer;
}

.tab:hover { color: var(--text-primary); }

.tab.active {
  color: var(--text-primary);
  font-weight: 500;
}

.tab-indicator {
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--brand-primary);  /* Purple only here */
}
```

## Form Inputs

```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-label .required { color: var(--error); }

.input {
  padding: 10px 12px;  /* Consistent */
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-surface);  /* #1C1C1C */
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input::placeholder { color: var(--text-muted); }
.input:hover { border-color: rgba(255, 255, 255, 0.12); }
.input:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px rgba(130, 81, 238, 0.2);
}

.form-hint {
  font-size: 12px;
  color: var(--text-muted);
}
```

## Modal

```jsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="modal"
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="btn-icon" onClick={onClose}>
            <X size={16} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
        <div className="modal-footer">
          <motion.button className="btn btn-primary" whileTap={{ scale: 0.98 }}>
            Create
          </motion.button>
          <motion.button className="btn btn-secondary" onClick={onClose} whileTap={{ scale: 0.98 }}>
            Cancel
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--bg-card);  /* #141414 */
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  max-width: 540px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
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
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
```

## Sidebar

```css
.sidebar {
  width: 56px;
  background: var(--bg-sidebar);  /* #0D0D0D */
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  padding: 12px 0;
  flex-shrink: 0;
}

.sidebar-item {
  width: 40px;
  height: 40px;
  margin: 4px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--text-muted);  /* #6B6B6B - grey */
  cursor: pointer;
  transition: all 0.15s ease;
}

.sidebar-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.sidebar-item.active {
  background: rgba(255, 255, 255, 0.08);
  color: var(--brand-light);  /* #A37EF5 - purple for active */
}
```

## Data Table

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: transparent;
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.data-table tbody tr {
  transition: background 0.15s ease;
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.data-table tbody tr.selected {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: inset 3px 0 0 var(--brand-primary);  /* Purple bar */
}
```

## Spacing Reference

| Element | Padding/Gap |
|---------|-------------|
| Page content | 32px |
| Card | 20px |
| Card header margin-bottom | 12px |
| Card description margin-bottom | 16px |
| Card tags gap | 8px |
| Card grid gap | 16px |
| Button | 8px 16px |
| Tag/Badge | 4px 10px |
| Input | 10px 12px |
| Modal body | 24px |
| Tabs gap | 24px |
| Form fields gap | 20px |
