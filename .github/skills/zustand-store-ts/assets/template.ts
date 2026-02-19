import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

// ============================================================================
// Types
// ============================================================================

/**
 * {{StoreName}}State - The state shape for this store
 */
export interface {{StoreName}}State {
  // Add state properties
  items: unknown[];
  selectedId: string | null;
  isLoading: boolean;
  error: string | null;
}

/**
 * {{StoreName}}Actions - Actions that can be performed on this store
 */
export interface {{StoreName}}Actions {
  // Setters
  setItems: (items: unknown[]) => void;
  setSelectedId: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Complex actions
  loadItems: () => Promise<void>;
  addItem: (item: unknown) => void;
  removeItem: (id: string) => void;

  // Reset
  reset: () => void;
}

/**
 * {{StoreName}}Store - Combined store type
 */
export type {{StoreName}}Store = {{StoreName}}State & {{StoreName}}Actions;

// ============================================================================
// Initial State
// ============================================================================

const initialState: {{StoreName}}State = {
  items: [],
  selectedId: null,
  isLoading: false,
  error: null,
};

// ============================================================================
// Store
// ============================================================================

/**
 * use{{StoreName}}Store - Zustand store for managing {{description}}
 *
 * @example
 * ```typescript
 * // In a component - use individual selectors for performance
 * const items = use{{StoreName}}Store((state) => state.items);
 * const loadItems = use{{StoreName}}Store((state) => state.loadItems);
 *
 * // Subscribe to changes outside React
 * use{{StoreName}}Store.subscribe(
 *   (state) => state.selectedId,
 *   (selectedId) => console.log('Selected:', selectedId)
 * );
 * ```
 */
export const use{{StoreName}}Store = create<{{StoreName}}Store>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    ...initialState,

    // Simple setters
    setItems: (items) => set({ items }),
    setSelectedId: (selectedId) => set({ selectedId }),
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),

    // Async action example
    loadItems: async () => {
      set({ isLoading: true, error: null });
      try {
        // const items = await fetchItems();
        const items: unknown[] = []; // Replace with actual fetch
        set({ items, isLoading: false });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to load',
          isLoading: false,
        });
      }
    },

    // Add item (immutable update)
    addItem: (item) => {
      set({ items: [...get().items, item] });
    },

    // Remove item (immutable update)
    removeItem: (id) => {
      set({
        items: get().items.filter((item) => (item as { id: string }).id !== id),
        // Clear selection if removed item was selected
        selectedId: get().selectedId === id ? null : get().selectedId,
      });
    },

    // Reset to initial state
    reset: () => set(initialState),
  }))
);
