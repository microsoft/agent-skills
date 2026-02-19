# Design Tokens

Complete design token reference for the frontend-ui-dark-ts theme system.

## CSS Custom Properties

Define these in your `globals.css` or a dedicated `tokens.css` file:

```css
:root {
  /* ========================================
   * BRAND COLORS
   * ======================================== */
  --color-brand: #8251EE;
  --color-brand-hover: #9366F5;
  --color-brand-light: #A37EF5;
  --color-brand-subtle: rgba(130, 81, 238, 0.15);
  --color-brand-muted: rgba(130, 81, 238, 0.4);

  /* ========================================
   * NEUTRAL BACKGROUNDS (HSL-based)
   * ======================================== */
  --color-bg-1: hsl(240, 6%, 10%);   /* #18181B - Base/page background */
  --color-bg-2: hsl(240, 5%, 12%);   /* #1F1F23 - Card background */
  --color-bg-3: hsl(240, 5%, 14%);   /* #242428 - Elevated surface */
  --color-bg-4: hsl(240, 4%, 18%);   /* #2D2D32 - Higher elevation */
  --color-bg-5: hsl(240, 4%, 22%);   /* #38383E - Hover states */
  --color-bg-6: hsl(240, 4%, 26%);   /* #43434A - Active states */

  /* ========================================
   * TEXT COLORS
   * ======================================== */
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #A1A1AA;
  --color-text-muted: #71717A;
  --color-text-disabled: #52525B;
  --color-text-inverse: #18181B;

  /* ========================================
   * BORDER COLORS
   * ======================================== */
  --color-border-subtle: hsla(0, 0%, 100%, 0.08);
  --color-border-default: hsla(0, 0%, 100%, 0.12);
  --color-border-strong: hsla(0, 0%, 100%, 0.20);
  --color-border-focus: var(--color-brand);

  /* ========================================
   * STATUS COLORS
   * ======================================== */
  --color-success: #10B981;
  --color-success-subtle: rgba(16, 185, 129, 0.15);
  --color-warning: #F59E0B;
  --color-warning-subtle: rgba(245, 158, 11, 0.15);
  --color-error: #EF4444;
  --color-error-subtle: rgba(239, 68, 68, 0.15);
  --color-info: #3B82F6;
  --color-info-subtle: rgba(59, 130, 246, 0.15);

  /* ========================================
   * DATA VISUALIZATION PALETTE
   * ======================================== */
  --color-dataviz-1: #8251EE;  /* Purple (brand) */
  --color-dataviz-2: #3B82F6;  /* Blue */
  --color-dataviz-3: #10B981;  /* Green */
  --color-dataviz-4: #F59E0B;  /* Yellow */
  --color-dataviz-5: #EF4444;  /* Red */
  --color-dataviz-6: #EC4899;  /* Pink */
  --color-dataviz-7: #06B6D4;  /* Cyan */

  /* ========================================
   * GLASS EFFECT COLORS
   * ======================================== */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-bg-hover: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.10);
  --glass-border-strong: rgba(255, 255, 255, 0.15);
  --glass-overlay: rgba(0, 0, 0, 0.60);
  --glass-panel: rgba(0, 0, 0, 0.40);

  /* ========================================
   * SHADOWS
   * ======================================== */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.3);
  --shadow-glow: 0 0 20px rgba(130, 81, 238, 0.3);
  --shadow-glow-lg: 0 0 40px rgba(130, 81, 238, 0.4);

  /* ========================================
   * SPACING SCALE
   * ======================================== */
  --spacing-0: 0;
  --spacing-px: 1px;
  --spacing-0-5: 0.125rem;  /* 2px */
  --spacing-1: 0.25rem;     /* 4px */
  --spacing-1-5: 0.375rem;  /* 6px */
  --spacing-2: 0.5rem;      /* 8px */
  --spacing-2-5: 0.625rem;  /* 10px */
  --spacing-3: 0.75rem;     /* 12px */
  --spacing-3-5: 0.875rem;  /* 14px */
  --spacing-4: 1rem;        /* 16px */
  --spacing-5: 1.25rem;     /* 20px */
  --spacing-6: 1.5rem;      /* 24px */
  --spacing-7: 1.75rem;     /* 28px */
  --spacing-8: 2rem;        /* 32px */
  --spacing-9: 2.25rem;     /* 36px */
  --spacing-10: 2.5rem;     /* 40px */
  --spacing-12: 3rem;       /* 48px */
  --spacing-14: 3.5rem;     /* 56px */
  --spacing-16: 4rem;       /* 64px */
  --spacing-20: 5rem;       /* 80px */
  --spacing-24: 6rem;       /* 96px */

  /* ========================================
   * BORDER RADIUS
   * ======================================== */
  --radius-none: 0;
  --radius-sm: 0.25rem;     /* 4px */
  --radius-default: 0.375rem; /* 6px */
  --radius-md: 0.5rem;      /* 8px */
  --radius-lg: 0.75rem;     /* 12px */
  --radius-xl: 1rem;        /* 16px */
  --radius-2xl: 1.5rem;     /* 24px */
  --radius-full: 9999px;

  /* ========================================
   * TYPOGRAPHY
   * ======================================== */
  --font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  --font-mono: 'Cascadia Code', 'Fira Code', monospace;

  /* Font sizes */
  --text-xs: 0.75rem;       /* 12px */
  --text-sm: 0.875rem;      /* 14px */
  --text-base: 1rem;        /* 16px */
  --text-lg: 1.125rem;      /* 18px */
  --text-xl: 1.25rem;       /* 20px */
  --text-2xl: 1.5rem;       /* 24px */
  --text-3xl: 1.875rem;     /* 30px */
  --text-4xl: 2.25rem;      /* 36px */

  /* Line heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Font weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* ========================================
   * TRANSITIONS
   * ======================================== */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;
  --transition-spring: 200ms cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ========================================
   * Z-INDEX SCALE
   * ======================================== */
  --z-dropdown: 50;
  --z-sticky: 100;
  --z-modal: 200;
  --z-popover: 300;
  --z-tooltip: 400;
  --z-toast: 500;
}
```

## Tailwind Configuration

Extend these tokens in `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Cascadia Code', 'Fira Code', 'monospace'],
      },
      colors: {
        brand: {
          DEFAULT: '#8251EE',
          hover: '#9366F5',
          light: '#A37EF5',
          subtle: 'rgba(130, 81, 238, 0.15)',
          muted: 'rgba(130, 81, 238, 0.4)',
        },
        neutral: {
          bg1: 'hsl(240, 6%, 10%)',
          bg2: 'hsl(240, 5%, 12%)',
          bg3: 'hsl(240, 5%, 14%)',
          bg4: 'hsl(240, 4%, 18%)',
          bg5: 'hsl(240, 4%, 22%)',
          bg6: 'hsl(240, 4%, 26%)',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#A1A1AA',
          muted: '#71717A',
          disabled: '#52525B',
          inverse: '#18181B',
        },
        border: {
          subtle: 'hsla(0, 0%, 100%, 0.08)',
          DEFAULT: 'hsla(0, 0%, 100%, 0.12)',
          strong: 'hsla(0, 0%, 100%, 0.20)',
        },
        status: {
          success: '#10B981',
          'success-subtle': 'rgba(16, 185, 129, 0.15)',
          warning: '#F59E0B',
          'warning-subtle': 'rgba(245, 158, 11, 0.15)',
          error: '#EF4444',
          'error-subtle': 'rgba(239, 68, 68, 0.15)',
          info: '#3B82F6',
          'info-subtle': 'rgba(59, 130, 246, 0.15)',
        },
        dataviz: {
          purple: '#8251EE',
          blue: '#3B82F6',
          green: '#10B981',
          yellow: '#F59E0B',
          red: '#EF4444',
          pink: '#EC4899',
          cyan: '#06B6D4',
        },
        glass: {
          bg: 'rgba(255, 255, 255, 0.05)',
          'bg-hover': 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.10)',
          'border-strong': 'rgba(255, 255, 255, 0.15)',
          overlay: 'rgba(0, 0, 0, 0.60)',
          panel: 'rgba(0, 0, 0, 0.40)',
        },
      },
      borderRadius: {
        DEFAULT: '0.375rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        glow: '0 0 20px rgba(130, 81, 238, 0.3)',
        'glow-lg': '0 0 40px rgba(130, 81, 238, 0.4)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      transitionTimingFunction: {
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
};
```

## Glass Effect Utilities

Add these to your `globals.css` under `@layer components`:

```css
@layer components {
  /* Basic glass effect */
  .glass {
    @apply backdrop-blur-md bg-white/5 border border-white/10;
  }

  /* Glass card with rounded corners */
  .glass-card {
    @apply backdrop-blur-md bg-white/5 border border-white/10 rounded-xl;
  }

  /* Glass card on hover */
  .glass-card-hover {
    @apply backdrop-blur-md bg-white/5 border border-white/10 rounded-xl
           hover:bg-white/[0.08] hover:border-white/[0.15]
           transition-colors duration-200;
  }

  /* Darker glass panel (for sidebars, navigation) */
  .glass-panel {
    @apply backdrop-blur-lg bg-black/40 border border-white/5;
  }

  /* Glass overlay for modals */
  .glass-overlay {
    @apply backdrop-blur-sm bg-black/60;
  }

  /* Glass input field */
  .glass-input {
    @apply backdrop-blur-sm bg-white/5 border border-white/10 
           placeholder:text-text-muted
           focus:border-brand focus:bg-white/[0.08] focus:outline-none
           transition-colors duration-200;
  }

  /* Glass button */
  .glass-button {
    @apply backdrop-blur-sm bg-white/5 border border-white/10
           hover:bg-white/[0.08] hover:border-white/[0.15]
           active:bg-white/[0.12]
           transition-colors duration-150;
  }

  /* Elevated glass (stronger blur, more prominent) */
  .glass-elevated {
    @apply backdrop-blur-xl bg-white/[0.08] border border-white/[0.15]
           shadow-lg;
  }
}
```

## Typography Classes

Add these utility classes for consistent typography:

```css
@layer components {
  /* Headings */
  .heading-1 {
    @apply text-3xl font-bold text-text-primary leading-tight;
  }

  .heading-2 {
    @apply text-2xl font-semibold text-text-primary leading-tight;
  }

  .heading-3 {
    @apply text-xl font-semibold text-text-primary leading-snug;
  }

  .heading-4 {
    @apply text-lg font-semibold text-text-primary leading-snug;
  }

  /* Body text */
  .body-large {
    @apply text-base text-text-secondary leading-relaxed;
  }

  .body {
    @apply text-sm text-text-secondary leading-normal;
  }

  .body-small {
    @apply text-xs text-text-muted leading-normal;
  }

  /* Labels */
  .label {
    @apply text-sm font-medium text-text-secondary;
  }

  .label-small {
    @apply text-xs font-medium text-text-muted uppercase tracking-wide;
  }

  /* Captions */
  .caption {
    @apply text-xs text-text-muted;
  }
}
```

## Framer Motion Timing

Recommended easing functions for Framer Motion:

```tsx
// Timing presets
export const timing = {
  fast: 0.15,
  normal: 0.2,
  slow: 0.3,
  verySlow: 0.5,
};

// Easing presets
export const easing = {
  // Standard ease for most animations
  default: [0.25, 0.1, 0.25, 1],
  
  // Ease out for entering elements
  easeOut: [0, 0, 0.2, 1],
  
  // Ease in for exiting elements
  easeIn: [0.4, 0, 1, 1],
  
  // Spring-like bounce
  spring: [0.34, 1.56, 0.64, 1],
  
  // Smooth deceleration
  decelerate: [0, 0.7, 0.3, 1],
};

// Transition presets
export const transitions = {
  fast: { duration: timing.fast, ease: easing.default },
  normal: { duration: timing.normal, ease: easing.default },
  slow: { duration: timing.slow, ease: easing.easeOut },
  spring: { type: 'spring', stiffness: 400, damping: 17 },
  springGentle: { type: 'spring', stiffness: 200, damping: 20 },
};
```

## Color Palette Summary

### Brand Colors
| Name | Hex | Usage |
|------|-----|-------|
| Brand | `#8251EE` | Primary actions, links, focus rings |
| Brand Hover | `#9366F5` | Hover state for brand elements |
| Brand Light | `#A37EF5` | Lighter accent, selected states |
| Brand Subtle | `rgba(130,81,238,0.15)` | Background for brand badges, tags |

### Neutral Backgrounds
| Name | HSL | Hex | Usage |
|------|-----|-----|-------|
| bg1 | `hsl(240,6%,10%)` | `#18181B` | Page background |
| bg2 | `hsl(240,5%,12%)` | `#1F1F23` | Card background |
| bg3 | `hsl(240,5%,14%)` | `#242428` | Elevated surface, input bg |
| bg4 | `hsl(240,4%,18%)` | `#2D2D32` | Higher elevation |
| bg5 | `hsl(240,4%,22%)` | `#38383E` | Hover states |
| bg6 | `hsl(240,4%,26%)` | `#43434A` | Active/pressed states |

### Text Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#FFFFFF` | Headings, important text |
| Secondary | `#A1A1AA` | Body text, descriptions |
| Muted | `#71717A` | Captions, placeholders |
| Disabled | `#52525B` | Disabled text |

### Status Colors
| Status | Color | Subtle |
|--------|-------|--------|
| Success | `#10B981` | `rgba(16,185,129,0.15)` |
| Warning | `#F59E0B` | `rgba(245,158,11,0.15)` |
| Error | `#EF4444` | `rgba(239,68,68,0.15)` |
| Info | `#3B82F6` | `rgba(59,130,246,0.15)` |

### Data Visualization
| Index | Color | Name |
|-------|-------|------|
| 1 | `#8251EE` | Purple |
| 2 | `#3B82F6` | Blue |
| 3 | `#10B981` | Green |
| 4 | `#F59E0B` | Yellow |
| 5 | `#EF4444` | Red |
| 6 | `#EC4899` | Pink |
| 7 | `#06B6D4` | Cyan |
