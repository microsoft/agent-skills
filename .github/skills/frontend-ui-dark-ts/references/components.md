# Components

Reusable UI components built with React, Tailwind CSS, and Framer Motion.

## Button

```tsx
import { motion, type HTMLMotionProps } from 'framer-motion';
import { clsx } from 'clsx';
import { forwardRef, type ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-brand text-white hover:bg-brand-hover active:bg-brand-light',
  secondary: 'bg-neutral-bg3 text-text-primary border border-border hover:bg-neutral-bg4 hover:border-border-strong',
  ghost: 'text-text-secondary hover:text-text-primary hover:bg-neutral-bg3',
  danger: 'bg-status-error text-white hover:bg-red-600 active:bg-red-700',
};

// Size variants - all sizes meet 44px minimum height on mobile for touch targets
const sizes: Record<ButtonSize, string> = {
  sm: 'h-8 min-h-touch px-3 text-xs gap-1.5 rounded',      // 32px desktop, 44px mobile minimum
  md: 'h-10 min-h-touch px-4 text-sm gap-2 rounded-lg',    // 40px desktop, 44px mobile minimum
  lg: 'h-12 px-6 text-base gap-2.5 rounded-lg',            // 48px already exceeds 44px
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', children, isLoading, leftIcon, rightIcon, className, disabled, ...props }, ref) => {
    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: disabled || isLoading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
        transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        className={clsx(
          'inline-flex items-center justify-center font-medium transition-colors duration-150',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-bg1',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
          </>
        )}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';
```

### Button Usage

```tsx
// Primary (default)
<Button>Save Changes</Button>

// Secondary
<Button variant="secondary">Cancel</Button>

// Ghost
<Button variant="ghost">Learn More</Button>

// Danger
<Button variant="danger">Delete</Button>

// With icons
<Button leftIcon={<PlusIcon />}>Add Item</Button>
<Button rightIcon={<ArrowRightIcon />}>Continue</Button>

// Loading state
<Button isLoading>Saving...</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

---

## Input

```tsx
import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, leftIcon, rightIcon, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
              {leftIcon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'w-full h-10 min-h-touch px-3 rounded-lg text-sm text-text-primary', // min-h-touch for 44px mobile touch target
              'bg-neutral-bg2 border border-border',
              'placeholder:text-text-muted',
              'focus:outline-none focus:border-brand focus:bg-neutral-bg3',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-colors duration-150',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-status-error focus:border-status-error',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted">
              {rightIcon}
            </span>
          )}
        </div>
        {error && <p className="text-xs text-status-error">{error}</p>}
        {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

### Search Input Variant

```tsx
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/20/solid';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchInput({ value, onChange, placeholder = 'Search...' }: SearchInputProps) {
  return (
    <Input
      type="search"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      leftIcon={<MagnifyingGlassIcon className="w-4 h-4" />}
      rightIcon={
        value && (
          <button onClick={() => onChange('')} className="hover:text-text-primary transition-colors">
            <XMarkIcon className="w-4 h-4" />
          </button>
        )
      }
    />
  );
}
```

---

## Card

```tsx
import { motion, type HTMLMotionProps } from 'framer-motion';
import { clsx } from 'clsx';
import { forwardRef, type ReactNode } from 'react';

type CardVariant = 'default' | 'glass' | 'elevated';

interface CardProps extends HTMLMotionProps<'div'> {
  variant?: CardVariant;
  children: ReactNode;
  interactive?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const variants: Record<CardVariant, string> = {
  default: 'bg-neutral-bg2 border border-border',
  glass: 'backdrop-blur-md bg-white/5 border border-white/10',
  elevated: 'bg-neutral-bg3 border border-border shadow-lg',
};

const paddings = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', children, interactive = false, padding = 'md', className, ...props }, ref) => {
    const baseClass = clsx(
      'rounded-xl',
      variants[variant],
      paddings[padding],
      interactive && 'cursor-pointer hover:border-border-strong transition-colors duration-150',
      className
    );

    if (interactive) {
      return (
        <motion.div
          ref={ref}
          className={baseClass}
          whileHover={{ scale: 1.01, y: -2 }}
          whileTap={{ scale: 0.99 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          {...props}
        >
          {children}
        </motion.div>
      );
    }

    return (
      <motion.div ref={ref} className={baseClass} {...props}>
        {children}
      </motion.div>
    );
  }
);

Card.displayName = 'Card';

// Subcomponents
export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx('mb-4', className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={clsx('text-lg font-semibold text-text-primary', className)}>{children}</h3>;
}

export function CardDescription({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={clsx('text-sm text-text-secondary mt-1', className)}>{children}</p>;
}

export function CardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={className}>{children}</div>;
}

export function CardFooter({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx('mt-4 flex items-center gap-2', className)}>{children}</div>;
}
```

### Card Usage

```tsx
// Default card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
</Card>

// Glass card
<Card variant="glass">
  <p>Glass card with blur effect</p>
</Card>

// Interactive card
<Card interactive onClick={() => console.log('clicked')}>
  <p>Click me!</p>
</Card>
```

---

## Badge

```tsx
import { clsx } from 'clsx';
import { type ReactNode } from 'react';

type BadgeVariant = 'default' | 'brand' | 'success' | 'warning' | 'error' | 'info';
type BadgeSize = 'sm' | 'md';

interface BadgeProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  children: ReactNode;
  className?: string;
}

const variants: Record<BadgeVariant, string> = {
  default: 'bg-neutral-bg4 text-text-secondary',
  brand: 'bg-brand-subtle text-brand-light',
  success: 'bg-status-success-subtle text-status-success',
  warning: 'bg-status-warning-subtle text-status-warning',
  error: 'bg-status-error-subtle text-status-error',
  info: 'bg-status-info-subtle text-status-info',
};

const sizes: Record<BadgeSize, string> = {
  sm: 'text-xs px-1.5 py-0.5',
  md: 'text-xs px-2 py-1',
};

export function Badge({ variant = 'default', size = 'md', children, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-md',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}
```

### Badge Usage

```tsx
<Badge>Default</Badge>
<Badge variant="brand">Brand</Badge>
<Badge variant="success">Success</Badge>
<Badge variant="warning">Warning</Badge>
<Badge variant="error">Error</Badge>
<Badge variant="info">Info</Badge>

// With dot indicator
<Badge variant="success">
  <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
  Active
</Badge>
```

---

## Dialog

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { type ReactNode, useEffect, useRef } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface DialogProps {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizes = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
};

export function Dialog({ open, onClose, children, title, description, size = 'md' }: DialogProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (open) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            ref={overlayRef}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 glass-overlay"
            onClick={(e) => e.target === overlayRef.current && onClose()}
          />

          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
            className={clsx(
              'relative w-full mx-4 glass-card p-6',
              sizes[size]
            )}
          >
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-text-muted hover:text-text-primary transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>

            {/* Header */}
            {(title || description) && (
              <div className="mb-4 pr-8">
                {title && <h2 className="text-lg font-semibold text-text-primary">{title}</h2>}
                {description && <p className="text-sm text-text-secondary mt-1">{description}</p>}
              </div>
            )}

            {/* Content */}
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

// Subcomponents
export function DialogFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={clsx('mt-6 flex items-center justify-end gap-3', className)}>
      {children}
    </div>
  );
}
```

### Dialog Usage

```tsx
const [open, setOpen] = useState(false);

<Button onClick={() => setOpen(true)}>Open Dialog</Button>

<Dialog
  open={open}
  onClose={() => setOpen(false)}
  title="Confirm Action"
  description="Are you sure you want to continue?"
>
  <p className="text-sm text-text-secondary">
    This action cannot be undone.
  </p>
  <DialogFooter>
    <Button variant="secondary" onClick={() => setOpen(false)}>
      Cancel
    </Button>
    <Button variant="danger" onClick={handleConfirm}>
      Delete
    </Button>
  </DialogFooter>
</Dialog>
```

---

## Tabs

```tsx
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { createContext, useContext, useState, type ReactNode } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

interface TabsProps {
  defaultValue: string;
  children: ReactNode;
  className?: string;
}

export function Tabs({ defaultValue, children, className }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={clsx(
        'flex items-center gap-1 p-1 bg-neutral-bg2 rounded-lg',
        className
      )}
    >
      {children}
    </div>
  );
}

interface TabsTriggerProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function TabsTrigger({ value, children, className }: TabsTriggerProps) {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabsTrigger must be used within Tabs');

  const { activeTab, setActiveTab } = context;
  const isActive = activeTab === value;

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={clsx(
        'relative px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-150',
        isActive ? 'text-text-primary' : 'text-text-muted hover:text-text-secondary',
        className
      )}
    >
      {isActive && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-neutral-bg4 rounded-md"
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  );
}

interface TabsContentProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function TabsContent({ value, children, className }: TabsContentProps) {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabsContent must be used within Tabs');

  if (context.activeTab !== value) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={clsx('mt-4', className)}
    >
      {children}
    </motion.div>
  );
}
```

### Tabs Usage

```tsx
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="analytics">Analytics</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">
    <p>Overview content</p>
  </TabsContent>
  <TabsContent value="analytics">
    <p>Analytics content</p>
  </TabsContent>
  <TabsContent value="settings">
    <p>Settings content</p>
  </TabsContent>
</Tabs>
```

---

## Avatar

```tsx
import { clsx } from 'clsx';
import { useState, type ImgHTMLAttributes } from 'react';

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size'> {
  size?: AvatarSize;
  fallback?: string;
}

const sizes: Record<AvatarSize, string> = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl',
};

export function Avatar({ size = 'md', fallback, src, alt, className, ...props }: AvatarProps) {
  const [hasError, setHasError] = useState(false);

  const initials = fallback || alt?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?';

  if (!src || hasError) {
    return (
      <div
        className={clsx(
          'flex items-center justify-center rounded-full bg-brand-subtle text-brand font-medium',
          sizes[size],
          className
        )}
      >
        {initials}
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      onError={() => setHasError(true)}
      className={clsx('rounded-full object-cover', sizes[size], className)}
      {...props}
    />
  );
}
```

---

## Checkbox

```tsx
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { forwardRef, type InputHTMLAttributes } from 'react';
import { CheckIcon } from '@heroicons/react/20/solid';

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className, id, ...props }, ref) => {
    const checkboxId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <label className={clsx('flex items-center gap-2 cursor-pointer', className)}>
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            id={checkboxId}
            className="peer sr-only"
            {...props}
          />
          <div
            className={clsx(
              'w-5 h-5 rounded border-2 transition-colors duration-150',
              'border-border bg-transparent',
              'peer-checked:border-brand peer-checked:bg-brand',
              'peer-focus-visible:ring-2 peer-focus-visible:ring-brand peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-neutral-bg1',
              'peer-disabled:opacity-50 peer-disabled:cursor-not-allowed'
            )}
          />
          <motion.div
            initial={false}
            animate={{ scale: props.checked ? 1 : 0 }}
            className="absolute inset-0 flex items-center justify-center text-white pointer-events-none"
          >
            <CheckIcon className="w-3.5 h-3.5" />
          </motion.div>
        </div>
        {label && <span className="text-sm text-text-secondary">{label}</span>}
      </label>
    );
  }
);

Checkbox.displayName = 'Checkbox';
```

---

## Select

```tsx
import { clsx } from 'clsx';
import { forwardRef, type SelectHTMLAttributes } from 'react';
import { ChevronDownIcon } from '@heroicons/react/20/solid';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, error, placeholder, className, id, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={selectId} className="text-sm font-medium text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={clsx(
              'w-full h-10 px-3 pr-10 rounded-lg text-sm appearance-none',
              'bg-neutral-bg2 border border-border text-text-primary',
              'focus:outline-none focus:border-brand focus:bg-neutral-bg3',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-colors duration-150',
              error && 'border-status-error focus:border-status-error',
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDownIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
        </div>
        {error && <p className="text-xs text-status-error">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
```

---

## Toast

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';

type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...toast, id }]);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
}

const icons: Record<ToastVariant, typeof CheckCircleIcon> = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationCircleIcon,
  info: InformationCircleIcon,
};

const variants: Record<ToastVariant, string> = {
  success: 'text-status-success',
  error: 'text-status-error',
  warning: 'text-status-warning',
  info: 'text-status-info',
};

function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon = icons[toast.variant];
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="glass-card p-4 min-w-[300px] max-w-[400px] flex items-start gap-3"
            >
              <Icon className={clsx('w-5 h-5 flex-shrink-0 mt-0.5', variants[toast.variant])} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary">{toast.title}</p>
                {toast.description && (
                  <p className="text-sm text-text-secondary mt-1">{toast.description}</p>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
```

### Toast Usage

```tsx
// Wrap app with provider
<ToastProvider>
  <App />
</ToastProvider>

// Use in components
const { addToast } = useToast();

addToast({
  variant: 'success',
  title: 'Changes saved',
  description: 'Your settings have been updated.',
});

addToast({
  variant: 'error',
  title: 'Error',
  description: 'Something went wrong.',
});
```

---

## Component Index

Export all components from a central file:

```tsx
// src/components/ui/index.ts
export { Button } from './Button';
export { Input, SearchInput } from './Input';
export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './Card';
export { Badge } from './Badge';
export { Dialog, DialogFooter } from './Dialog';
export { Tabs, TabsList, TabsTrigger, TabsContent } from './Tabs';
export { Avatar } from './Avatar';
export { Checkbox } from './Checkbox';
export { Select } from './Select';
export { ToastProvider, useToast } from './Toast';
```
