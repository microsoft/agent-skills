# Foundry NextGen Patterns

Layout patterns and page compositions with **Framer Motion** animations.

## Required Imports

```jsx
import { motion, AnimatePresence } from 'framer-motion';
import { Home, Layers, Box, Search, MoreVertical, X } from 'lucide-react';
```

## Animation Variants

```jsx
// Put these in a shared utils/animations.js file
export const pageVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3, ease: 'easeOut' } }
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 }
  }
};

export const fadeInUp = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } }
};

export const modalVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.2, ease: 'easeOut' } },
  exit: { opacity: 0, scale: 0.95, y: 10 }
};
```

## App Layout

```jsx
function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <TopBar />
        <motion.div 
          className="page-content"
          initial="hidden"
          animate="visible"
          variants={pageVariants}
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
```

```css
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-page);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.page-content {
  flex: 1;
  padding: 32px;  /* Always 32px page padding */
  overflow-y: auto;
}
```

## Sidebar Component

```jsx
function Sidebar() {
  const [active, setActive] = useState('home');
  
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <FoundryLogo />
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <motion.button
            key={item.id}
            className={`sidebar-item ${active === item.id ? 'active' : ''}`}
            onClick={() => setActive(item.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <item.icon size={20} />
          </motion.button>
        ))}
      </nav>
    </aside>
  );
}
```

```css
.sidebar {
  width: 56px;
  background: var(--bg-sidebar);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  padding: 12px 0;
  flex-shrink: 0;
}

.sidebar-logo {
  padding: 12px;
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 8px;
}

.sidebar-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.sidebar-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.sidebar-item.active {
  background: rgba(255, 255, 255, 0.08);
  color: var(--brand-light);  /* Purple for active only */
}
```

## Card Grid Page (List View)

```jsx
function CardGridPage({ title, items }) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={pageVariants}
    >
      {/* Page header */}
      <header className="page-header">
        <h1 className="page-title">{title}</h1>
        <motion.button 
          className="btn btn-primary"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Create
        </motion.button>
      </header>

      {/* Filter bar */}
      <div className="filter-bar">
        <nav className="tabs">
          <button className="tab active">All Demos</button>
          <button className="tab">Tier 1</button>
          <button className="tab">Tier 2</button>
        </nav>
      </div>

      {/* Card grid with stagger animation */}
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
    </motion.div>
  );
}
```

```css
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.filter-bar {
  margin-bottom: 24px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
```

## Card Component

```jsx
function Card({ title, description, status, tags, meta }) {
  return (
    <motion.div 
      className="card"
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
          {tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
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
  border-radius: 8px;
  padding: 20px;
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
  margin-bottom: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  border-radius: 4px;
  background: var(--bg-surface);
  color: var(--text-secondary);
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

## Badges

```css
.badge {
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
```

## Spacing Quick Reference

```
Page padding:     32px
Card padding:     20px
Card grid gap:    16px
Card header mb:   12px
Card desc mb:     16px
Tags gap:         8px
Tag padding:      4px 10px
Badge padding:    4px 10px
Button padding:   8px 16px
Modal body:       24px
Tabs gap:         24px
```

## Animation Quick Reference

```jsx
// Page entry
<motion.div initial="hidden" animate="visible" variants={pageVariants}>

// List with stagger
<motion.div variants={staggerContainer} initial="hidden" animate="visible">
  {items.map(item => (
    <motion.div key={item.id} variants={fadeInUp}>

// Card hover
<motion.div 
  whileHover={{ scale: 1.01, backgroundColor: 'rgba(255,255,255,0.02)' }}
  transition={{ duration: 0.15 }}
>

// Button press
<motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>

// Modal
<AnimatePresence>
  {isOpen && (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div variants={modalVariants} initial="hidden" animate="visible" exit="exit">
```
