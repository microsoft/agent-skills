# Patterns

Page layouts, navigation patterns, and application templates for dark-themed React applications.

## App Shell

The main application layout with sidebar navigation:

```tsx
import { motion } from 'framer-motion';
import { type ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-neutral-bg1">
      <Sidebar />
      <main className="flex-1 ml-64">
        {children}
      </main>
    </div>
  );
}
```

---

## Responsive App Shell

Mobile-responsive layout: desktop shows fixed sidebar, mobile shows hamburger menu with slide-in drawer.

**Breakpoint:** `lg` (1024px) — sidebar visible on desktop, hidden on mobile.

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { type ReactNode, useState } from 'react';
import { Sidebar } from './Sidebar';
import { MobileHeader } from './MobileHeader';
import { MobileDrawer } from './MobileDrawer';

interface ResponsiveAppShellProps {
  children: ReactNode;
}

export function ResponsiveAppShell({ children }: ResponsiveAppShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-neutral-bg1">
      {/* Desktop sidebar - hidden on mobile */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile header - visible only on mobile */}
      <MobileHeader onMenuClick={() => setDrawerOpen(true)} />

      {/* Mobile drawer */}
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />

      {/* Main content - adjusted margins for desktop sidebar and mobile header */}
      <main className="flex-1 lg:ml-64 pt-14 lg:pt-0 pb-safe-bottom">
        {children}
      </main>
    </div>
  );
}
```

---

## Mobile Header

Fixed top header for mobile with hamburger menu toggle. Uses 44px minimum touch target.

```tsx
import { Bars3Icon } from '@heroicons/react/24/outline';

interface MobileHeaderProps {
  onMenuClick: () => void;
}

export function MobileHeader({ onMenuClick }: MobileHeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-14 glass-panel flex items-center justify-between px-4 lg:hidden z-40">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <img src="/logo.svg" alt="Logo" className="w-6 h-6" />
        <span className="text-base font-semibold text-text-primary">AppName</span>
      </div>

      {/* Hamburger menu - 44px touch target */}
      <button
        onClick={onMenuClick}
        className="min-w-touch min-h-touch flex items-center justify-center rounded-lg hover:bg-white/5 active:bg-white/10 transition-colors"
        aria-label="Open menu"
      >
        <Bars3Icon className="w-6 h-6 text-text-primary" />
      </button>
    </header>
  );
}
```

---

## Mobile Drawer

Animated slide-in navigation drawer for mobile. Includes backdrop and close button.

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  HomeIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UsersIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';

const navItems = [
  { path: '/', label: 'Dashboard', icon: HomeIcon },
  { path: '/analytics', label: 'Analytics', icon: ChartBarIcon },
  { path: '/projects', label: 'Projects', icon: FolderIcon },
  { path: '/team', label: 'Team', icon: UsersIcon },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon },
];

interface MobileDrawerProps {
  open: boolean;
  onClose: () => void;
}

export function MobileDrawer({ open, onClose }: MobileDrawerProps) {
  const location = useLocation();

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 lg:hidden"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className="fixed left-0 top-0 bottom-0 w-72 glass-panel p-4 flex flex-col z-50 lg:hidden pl-safe-left"
          >
            {/* Header with close button */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <img src="/logo.svg" alt="Logo" className="w-8 h-8" />
                <span className="text-lg font-semibold text-text-primary">AppName</span>
              </div>
              <button
                onClick={onClose}
                className="min-w-touch min-h-touch flex items-center justify-center rounded-lg hover:bg-white/5 active:bg-white/10 transition-colors"
                aria-label="Close menu"
              >
                <XMarkIcon className="w-6 h-6 text-text-primary" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                const Icon = item.icon;

                return (
                  <NavLink key={item.path} to={item.path} onClick={onClose}>
                    <motion.div
                      className={clsx(
                        'relative flex items-center gap-3 px-3 py-3 rounded-lg',
                        'text-base font-medium transition-colors duration-150',
                        'min-h-touch', // 44px touch target
                        isActive
                          ? 'text-text-primary bg-brand/20 border border-brand/30'
                          : 'text-text-muted hover:text-text-secondary hover:bg-white/5 active:bg-white/10'
                      )}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className={clsx('w-5 h-5', isActive && 'text-brand')} />
                      <span>{item.label}</span>
                    </motion.div>
                  </NavLink>
                );
              })}
            </nav>

            {/* User profile at bottom */}
            <div className="mt-auto pt-4 border-t border-white/10 pb-safe-bottom">
              <div className="flex items-center gap-3 px-3 py-2">
                <div className="w-10 h-10 rounded-full bg-brand-subtle flex items-center justify-center">
                  <span className="text-sm font-medium text-brand">JD</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">John Doe</p>
                  <p className="text-xs text-text-muted truncate">john@example.com</p>
                </div>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
```

---

## Sidebar Navigation

Glass-effect sidebar with animated navigation items:

```tsx
import { motion } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  HomeIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UsersIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';

const navItems = [
  { path: '/', label: 'Dashboard', icon: HomeIcon },
  { path: '/analytics', label: 'Analytics', icon: ChartBarIcon },
  { path: '/projects', label: 'Projects', icon: FolderIcon },
  { path: '/team', label: 'Team', icon: UsersIcon },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass-panel p-4 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 py-4 mb-6">
        <img src="/logo.svg" alt="Logo" className="w-8 h-8" />
        <span className="text-lg font-semibold text-text-primary">AppName</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <NavLink key={item.path} to={item.path}>
              <motion.div
                className={clsx(
                  'relative flex items-center gap-3 px-3 py-2.5 rounded-lg',
                  'text-sm font-medium transition-colors duration-150',
                  isActive
                    ? 'text-text-primary'
                    : 'text-text-muted hover:text-text-secondary hover:bg-white/5'
                )}
                whileHover={{ x: 4 }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavItem"
                    className="absolute inset-0 bg-brand/20 border border-brand/30 rounded-lg"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
                <Icon className={clsx('w-5 h-5 relative z-10', isActive && 'text-brand')} />
                <span className="relative z-10">{item.label}</span>
              </motion.div>
            </NavLink>
          );
        })}
      </nav>

      {/* User profile at bottom */}
      <div className="mt-auto pt-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-brand-subtle flex items-center justify-center">
            <span className="text-sm font-medium text-brand">JD</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary truncate">John Doe</p>
            <p className="text-xs text-text-muted truncate">john@example.com</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
```

---

## Page Header

Reusable header component for pages:

```tsx
import { motion } from 'framer-motion';
import { type ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex items-center justify-between mb-8"
    >
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
        {description && (
          <p className="text-sm text-text-secondary mt-1">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </motion.header>
  );
}
```

---

## Page Transition Wrapper

Animate page transitions with route changes:

```tsx
import { motion } from 'framer-motion';
import { type ReactNode } from 'react';

interface PageTransitionProps {
  children: ReactNode;
}

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}
```

### Usage with React Router

```tsx
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

function App() {
  const location = useLocation();

  return (
    <AppShell>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AnimatePresence>
    </AppShell>
  );
}
```

---

## Basic Page Template

Standard page layout with header and content area:

```tsx
import { PageTransition } from '../components/layout/PageTransition';
import { PageHeader } from '../components/layout/PageHeader';
import { Button } from '../components/ui';

export function BasicPage() {
  return (
    <PageTransition>
      <div className="p-8">
        <PageHeader
          title="Page Title"
          description="A brief description of this page"
          actions={
            <Button>Primary Action</Button>
          }
        />

        <div className="space-y-6">
          {/* Page content */}
        </div>
      </div>
    </PageTransition>
  );
}
```

---

## List Page Template

Page with search, filters, and data table:

```tsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { PageTransition } from '../components/layout/PageTransition';
import { PageHeader } from '../components/layout/PageHeader';
import { Button, SearchInput, Card, Badge } from '../components/ui';
import { PlusIcon } from '@heroicons/react/20/solid';

interface Item {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: string;
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
};

export function ListPage() {
  const [search, setSearch] = useState('');
  const [items] = useState<Item[]>([
    { id: '1', name: 'Project Alpha', status: 'active', createdAt: '2024-01-15' },
    { id: '2', name: 'Project Beta', status: 'pending', createdAt: '2024-01-14' },
    { id: '3', name: 'Project Gamma', status: 'inactive', createdAt: '2024-01-13' },
  ]);

  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <PageTransition>
      <div className="p-8">
        <PageHeader
          title="Projects"
          description="Manage your projects and their settings"
          actions={
            <Button leftIcon={<PlusIcon className="w-4 h-4" />}>
              New Project
            </Button>
          }
        />

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-72">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search projects..."
            />
          </div>
        </div>

        {/* Table */}
        <Card padding="none">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wide px-4 py-3">
                  Name
                </th>
                <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wide px-4 py-3">
                  Status
                </th>
                <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wide px-4 py-3">
                  Created
                </th>
              </tr>
            </thead>
            <motion.tbody
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {filteredItems.map((item) => (
                <motion.tr
                  key={item.id}
                  variants={staggerItem}
                  className="border-b border-border last:border-0 hover:bg-neutral-bg3 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-text-primary">
                      {item.name}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge
                      variant={
                        item.status === 'active' ? 'success' :
                        item.status === 'pending' ? 'warning' : 'default'
                      }
                    >
                      {item.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-text-secondary">
                      {item.createdAt}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </motion.tbody>
          </table>
        </Card>
      </div>
    </PageTransition>
  );
}
```

---

## Tabs Page Template

Page with tab navigation:

```tsx
import { PageTransition } from '../components/layout/PageTransition';
import { PageHeader } from '../components/layout/PageHeader';
import { Tabs, TabsList, TabsTrigger, TabsContent, Card } from '../components/ui';

export function TabsPage() {
  return (
    <PageTransition>
      <div className="p-8">
        <PageHeader
          title="Settings"
          description="Manage your account and preferences"
        />

        <Tabs defaultValue="general">
          <TabsList>
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
          </TabsList>

          <TabsContent value="general">
            <Card>
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                General Settings
              </h3>
              {/* General settings form */}
            </Card>
          </TabsContent>

          <TabsContent value="security">
            <Card>
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Security Settings
              </h3>
              {/* Security settings form */}
            </Card>
          </TabsContent>

          <TabsContent value="notifications">
            <Card>
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Notification Preferences
              </h3>
              {/* Notification settings */}
            </Card>
          </TabsContent>

          <TabsContent value="integrations">
            <Card>
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Connected Integrations
              </h3>
              {/* Integrations list */}
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </PageTransition>
  );
}
```

---

## Dashboard Template

Dashboard with stat cards and data visualization:

```tsx
import { motion } from 'framer-motion';
import { PageTransition } from '../components/layout/PageTransition';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '../components/ui';
import {
  ArrowUpIcon,
  ArrowDownIcon,
  UsersIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const stats = [
  { label: 'Total Revenue', value: '$45,231', change: '+12.5%', trend: 'up', icon: CurrencyDollarIcon },
  { label: 'Active Users', value: '2,345', change: '+8.2%', trend: 'up', icon: UsersIcon },
  { label: 'Conversion Rate', value: '3.2%', change: '-2.1%', trend: 'down', icon: ChartBarIcon },
  { label: 'Avg. Session', value: '4m 32s', change: '+18.7%', trend: 'up', icon: ClockIcon },
];

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function Dashboard() {
  return (
    <PageTransition>
      <div className="p-8">
        <PageHeader
          title="Dashboard"
          description="Welcome back! Here's what's happening."
        />

        {/* Stat Cards */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          {stats.map((stat) => {
            const Icon = stat.icon;
            const TrendIcon = stat.trend === 'up' ? ArrowUpIcon : ArrowDownIcon;

            return (
              <motion.div key={stat.label} variants={staggerItem}>
                <Card variant="glass" className="relative overflow-hidden">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-text-muted">{stat.label}</p>
                      <p className="text-2xl font-semibold text-text-primary mt-1">
                        {stat.value}
                      </p>
                      <div className="flex items-center gap-1 mt-2">
                        <TrendIcon
                          className={`w-4 h-4 ${
                            stat.trend === 'up' ? 'text-status-success' : 'text-status-error'
                          }`}
                        />
                        <span
                          className={`text-sm ${
                            stat.trend === 'up' ? 'text-status-success' : 'text-status-error'
                          }`}
                        >
                          {stat.change}
                        </span>
                        <span className="text-xs text-text-muted">vs last month</span>
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-brand-subtle">
                      <Icon className="w-5 h-5 text-brand" />
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart Card */}
          <Card variant="glass" className="lg:col-span-2">
            <CardTitle>Revenue Overview</CardTitle>
            <CardContent className="h-80">
              {/* Chart component would go here */}
              <div className="w-full h-full flex items-center justify-center text-text-muted">
                Chart placeholder
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card variant="glass">
            <CardTitle>Recent Activity</CardTitle>
            <CardContent>
              <ul className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-brand-subtle flex items-center justify-center flex-shrink-0">
                      <UsersIcon className="w-4 h-4 text-brand" />
                    </div>
                    <div>
                      <p className="text-sm text-text-primary">New user signed up</p>
                      <p className="text-xs text-text-muted">2 minutes ago</p>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTransition>
  );
}
```

---

## Stagger Animation Patterns

Reusable animation variants for list items:

```tsx
// variants.ts
export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

export const fadeInScale = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

export const slideInFromRight = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

export const slideInFromLeft = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};
```

### Using Stagger Animations

```tsx
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from './variants';

function ItemList({ items }) {
  return (
    <motion.ul
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      {items.map((item) => (
        <motion.li key={item.id} variants={staggerItem}>
          {item.name}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

---

## Glass Panel Layouts

### Two-Column Layout with Glass Panels

```tsx
export function TwoColumnLayout() {
  return (
    <div className="flex gap-6 p-8">
      {/* Main content */}
      <div className="flex-1">
        <Card variant="glass">
          <h2 className="text-lg font-semibold text-text-primary mb-4">
            Main Content
          </h2>
          {/* Content */}
        </Card>
      </div>

      {/* Sidebar */}
      <aside className="w-80">
        <Card variant="glass" className="sticky top-8">
          <h3 className="text-sm font-medium text-text-muted uppercase tracking-wide mb-4">
            Quick Actions
          </h3>
          {/* Sidebar content */}
        </Card>
      </aside>
    </div>
  );
}
```

### Grid of Glass Cards

```tsx
export function CardGrid({ items }) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      {items.map((item) => (
        <motion.div key={item.id} variants={staggerItem}>
          <Card variant="glass" interactive>
            <h3 className="text-base font-medium text-text-primary">
              {item.title}
            </h3>
            <p className="text-sm text-text-secondary mt-2">
              {item.description}
            </p>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
```

---

## Form Patterns

### Settings Form

```tsx
import { Button, Input, Select, Checkbox, Card } from '../components/ui';

export function SettingsForm() {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-text-primary mb-6">
        Account Settings
      </h2>

      <form className="space-y-6">
        {/* Two-column grid for larger screens */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="First Name"
            placeholder="Enter your first name"
          />
          <Input
            label="Last Name"
            placeholder="Enter your last name"
          />
        </div>

        <Input
          label="Email Address"
          type="email"
          placeholder="you@example.com"
        />

        <Select
          label="Timezone"
          placeholder="Select timezone"
          options={[
            { value: 'utc', label: 'UTC' },
            { value: 'pst', label: 'Pacific Time (PST)' },
            { value: 'est', label: 'Eastern Time (EST)' },
          ]}
        />

        <div className="border-t border-border pt-6">
          <h3 className="text-sm font-medium text-text-primary mb-4">
            Notification Preferences
          </h3>
          <div className="space-y-3">
            <Checkbox label="Email notifications" defaultChecked />
            <Checkbox label="Push notifications" />
            <Checkbox label="Weekly digest" defaultChecked />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary">Cancel</Button>
          <Button>Save Changes</Button>
        </div>
      </form>
    </Card>
  );
}
```

---

## Empty States

```tsx
import { motion } from 'framer-motion';
import { FolderIcon } from '@heroicons/react/24/outline';
import { Button } from '../components/ui';

interface EmptyStateProps {
  icon?: typeof FolderIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon: Icon = FolderIcon, title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-4"
    >
      <div className="w-16 h-16 rounded-full bg-neutral-bg3 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-text-muted" />
      </div>
      <h3 className="text-lg font-medium text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-secondary text-center max-w-sm mb-6">
        {description}
      </p>
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
    </motion.div>
  );
}
```

### Usage

```tsx
<EmptyState
  title="No projects yet"
  description="Get started by creating your first project."
  action={{
    label: 'Create Project',
    onClick: () => setShowCreateModal(true),
  }}
/>
```

---

## Loading States

### Skeleton Loader

```tsx
import { clsx } from 'clsx';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={clsx(
        'animate-pulse bg-neutral-bg4 rounded',
        className
      )}
    />
  );
}

// Usage
<Skeleton className="h-4 w-32" />
<Skeleton className="h-10 w-full" />
<Skeleton className="h-40 w-full rounded-xl" />
```

### Card Skeleton

```tsx
export function CardSkeleton() {
  return (
    <Card>
      <div className="space-y-4">
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </Card>
  );
}
```

### Table Skeleton

```tsx
export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <Card padding="none">
      <div className="divide-y divide-border">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4">
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-4 flex-1" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>
    </Card>
  );
}
```
