import { useMemo } from 'react';

export type Category = 'all' | string;

const CATEGORY_ORDER = [
  'all',
  'foundry',
  'm365',
  'general',
  'data',
  'messaging',
  'entra',
  'monitoring',
  'integration',
  'compute',
  'communication',
  'frontend',
  'partner',
];

const CATEGORY_LABELS: Record<string, string> = {
  all: 'All',
  foundry: 'Foundry',
  m365: 'M365',
  general: 'General',
  data: 'Data',
  messaging: 'Messaging',
  entra: 'Entra',
  monitoring: 'Monitoring',
  integration: 'Integration',
  compute: 'Compute',
  communication: 'Communication',
  frontend: 'Frontend',
  partner: 'Partner',
};

interface CategoryTabsProps {
  selectedCategory: Category;
  onSelect: (category: Category) => void;
  counts: Record<string, number>;
}

export function CategoryTabs({ selectedCategory, onSelect, counts }: CategoryTabsProps) {
  const totalCount = useMemo(() => {
    return Object.values(counts).reduce((sum, count) => sum + count, 0);
  }, [counts]);

  const categories = useMemo(() => {
    return CATEGORY_ORDER.filter(cat => cat === 'all' || counts[cat] > 0);
  }, [counts]);

  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-xs)',
    }}>
      {categories.map((category) => {
        const isSelected = selectedCategory === category;
        const count = category === 'all' ? totalCount : (counts[category] || 0);
        const label = CATEGORY_LABELS[category] || category;
        
        return (
          <button
            key={category}
            onClick={() => onSelect(category)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--space-xs)',
              padding: '6px 12px',
              fontSize: 'var(--text-xs)',
              fontWeight: 500,
              color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
              background: isSelected ? 'var(--accent-glow)' : 'var(--bg-secondary)',
              border: isSelected ? '1px solid var(--accent)' : '1px solid var(--border-primary)',
              borderRadius: '9999px',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              textTransform: 'capitalize',
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--border-hover)';
                e.currentTarget.style.background = 'var(--bg-tertiary)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--border-primary)';
                e.currentTarget.style.background = 'var(--bg-secondary)';
              }
            }}
          >
            <span>{label}</span>
            <span style={{
              fontSize: '10px',
              color: isSelected ? 'var(--accent)' : 'var(--text-muted)',
              fontWeight: 600,
            }}>
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default CategoryTabs;
