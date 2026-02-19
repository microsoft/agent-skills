# Zustand Store Acceptance Criteria (TypeScript)

**Library**: Zustand
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Core Imports

#### ✅ CORRECT: Zustand Imports
```typescript
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
```

#### ✅ CORRECT: Persist Middleware
```typescript
import { persist, createJSONStorage } from 'zustand/middleware';
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Old import style
```typescript
// WRONG - old import syntax
import create from 'zustand';

// CORRECT - named import
import { create } from 'zustand';
```

---

## 2. Store Creation Patterns

### 2.1 ✅ CORRECT: Basic Store with subscribeWithSelector
```typescript
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface MyStore {
  count: number;
  increment: () => void;
}

export const useMyStore = create<MyStore>()(
  subscribeWithSelector((set) => ({
    count: 0,
    increment: () => set((state) => ({ count: state.count + 1 })),
  }))
);
```

### 2.2 ✅ CORRECT: With get() Access
```typescript
export const useMyStore = create<MyStore>()(
  subscribeWithSelector((set, get) => ({
    count: 0,
    increment: () => set((state) => ({ count: state.count + 1 })),
    double: () => {
      const current = get().count;
      set({ count: current * 2 });
    },
  }))
);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing subscribeWithSelector
```typescript
// WRONG - should use subscribeWithSelector for fine-grained subscriptions
export const useMyStore = create<MyStore>()((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

#### ❌ INCORRECT: Wrong generic syntax
```typescript
// WRONG - missing double parentheses with middleware
export const useMyStore = create<MyStore>(
  subscribeWithSelector((set) => ({}))
);
```

---

## 3. State and Actions Separation

### 3.1 ✅ CORRECT: Separate Interfaces
```typescript
// State interface
export interface ProjectState {
  projects: Project[];
  selectedId: string | null;
  isLoading: boolean;
}

// Actions interface
export interface ProjectActions {
  addProject: (project: Project) => void;
  selectProject: (id: string) => void;
  loadProjects: () => Promise<void>;
}

// Combined store type
export type ProjectStore = ProjectState & ProjectActions;
```

### 3.2 ✅ CORRECT: Store with Separated Types
```typescript
export const useProjectStore = create<ProjectStore>()(
  subscribeWithSelector((set, get) => ({
    // State
    projects: [],
    selectedId: null,
    isLoading: false,

    // Actions
    addProject: (project) =>
      set((state) => ({
        projects: [...state.projects, project],
      })),

    selectProject: (id) =>
      set({ selectedId: id }),

    loadProjects: async () => {
      set({ isLoading: true });
      try {
        const projects = await fetchProjects();
        set({ projects, isLoading: false });
      } catch (error) {
        set({ isLoading: false });
      }
    },
  }))
);
```

---

## 4. Selector Patterns

### 4.1 ✅ CORRECT: Individual Selectors
```typescript
// Good - only re-renders when `count` changes
const count = useMyStore((state) => state.count);

// Good - selecting an action
const increment = useMyStore((state) => state.increment);
```

### 4.2 ✅ CORRECT: Multiple Selectors in Component
```typescript
function MyComponent() {
  const count = useMyStore((state) => state.count);
  const increment = useMyStore((state) => state.increment);
  
  return <button onClick={increment}>{count}</button>;
}
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Destructuring entire store
```typescript
// WRONG - re-renders on any state change
const { count, isLoading } = useMyStore();
```

#### ❌ INCORRECT: Creating new objects in selectors
```typescript
// WRONG - creates new object reference every render
const data = useMyStore((state) => ({
  count: state.count,
  isLoading: state.isLoading,
}));
```

### 4.4 ✅ CORRECT: Shallow comparison for multiple values
```typescript
import { useShallow } from 'zustand/react/shallow';

const { count, isLoading } = useMyStore(
  useShallow((state) => ({
    count: state.count,
    isLoading: state.isLoading,
  }))
);
```

---

## 5. Subscribe Outside React

### 5.1 ✅ CORRECT: Subscribe with Selector
```typescript
// Subscribe to specific state changes outside React
const unsubscribe = useMyStore.subscribe(
  (state) => state.selectedId,
  (selectedId, previousSelectedId) => {
    console.log('Selected ID changed from', previousSelectedId, 'to', selectedId);
  }
);

// Cleanup
unsubscribe();
```

### 5.2 ✅ CORRECT: Subscribe with Options
```typescript
useMyStore.subscribe(
  (state) => state.count,
  (count) => console.log('Count:', count),
  {
    fireImmediately: true,  // Fire callback immediately with current value
    equalityFn: Object.is,   // Custom equality function
  }
);
```

---

## 6. Persist Middleware

### 6.1 ✅ CORRECT: Persist to localStorage
```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { subscribeWithSelector } from 'zustand/middleware';

export const useSettingsStore = create<SettingsStore>()(
  subscribeWithSelector(
    persist(
      (set) => ({
        theme: 'dark',
        setTheme: (theme) => set({ theme }),
      }),
      {
        name: 'settings-storage',
        storage: createJSONStorage(() => localStorage),
      }
    )
  )
);
```

### 6.2 ✅ CORRECT: Partial Persistence
```typescript
persist(
  (set) => ({
    theme: 'dark',
    tempData: null,  // Won't be persisted
    setTheme: (theme) => set({ theme }),
  }),
  {
    name: 'settings-storage',
    partialize: (state) => ({ theme: state.theme }),  // Only persist theme
  }
)
```

---

## 7. Immer Middleware

### 7.1 ✅ CORRECT: Using Immer for Immutable Updates
```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { subscribeWithSelector } from 'zustand/middleware';

export const useTodoStore = create<TodoStore>()(
  subscribeWithSelector(
    immer((set) => ({
      todos: [],
      addTodo: (todo) =>
        set((state) => {
          state.todos.push(todo);  // Mutation is okay with immer
        }),
      toggleTodo: (id) =>
        set((state) => {
          const todo = state.todos.find((t) => t.id === id);
          if (todo) todo.completed = !todo.completed;
        }),
    }))
  )
);
```

---

## 8. Async Actions

### 8.1 ✅ CORRECT: Async Action Pattern
```typescript
export const useDataStore = create<DataStore>()(
  subscribeWithSelector((set, get) => ({
    data: null,
    isLoading: false,
    error: null,

    fetchData: async (id: string) => {
      set({ isLoading: true, error: null });
      try {
        const response = await api.getData(id);
        set({ data: response, isLoading: false });
      } catch (error) {
        set({ error: error.message, isLoading: false });
      }
    },
  }))
);
```

---

## 9. Store Slices Pattern

### 9.1 ✅ CORRECT: Combine Multiple Slices
```typescript
interface UISlice {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

interface DataSlice {
  items: Item[];
  addItem: (item: Item) => void;
}

type AppStore = UISlice & DataSlice;

const createUISlice = (set: SetState<AppStore>): UISlice => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
});

const createDataSlice = (set: SetState<AppStore>): DataSlice => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
});

export const useAppStore = create<AppStore>()(
  subscribeWithSelector((set, get) => ({
    ...createUISlice(set),
    ...createDataSlice(set),
  }))
);
```

---

## 10. Testing Patterns

### 10.1 ✅ CORRECT: Reset Store for Tests
```typescript
// In your store file
const initialState = {
  count: 0,
  items: [],
};

export const useMyStore = create<MyStore>()(
  subscribeWithSelector((set) => ({
    ...initialState,
    increment: () => set((state) => ({ count: state.count + 1 })),
    reset: () => set(initialState),
  }))
);

// In tests
beforeEach(() => {
  useMyStore.getState().reset();
});
```

---

## 11. Anti-Patterns Summary

### 11.1 ❌ Common Mistakes
```typescript
// WRONG - default import
import create from 'zustand';

// WRONG - missing subscribeWithSelector
create<Store>()((set) => ({}));

// WRONG - destructuring entire store
const { count, items } = useStore();

// WRONG - creating new objects in selectors
useStore((state) => ({ count: state.count }));

// WRONG - mutating state directly without immer
set((state) => {
  state.items.push(item);  // Won't work without immer
  return state;
});
```
