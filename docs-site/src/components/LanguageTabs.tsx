import { useMemo } from 'react';

export type Language = 'all' | 'core' | 'py' | 'dotnet' | 'ts' | 'java' | 'rust';

interface LanguageOption {
  value: Language;
  label: string;
  color: string;
}

const LANGUAGE_OPTIONS: LanguageOption[] = [
  { value: 'all', label: 'All', color: 'var(--text-secondary)' },
  { value: 'core', label: 'Core', color: 'var(--lang-core)' },
  { value: 'py', label: 'Python', color: 'var(--lang-python)' },
  { value: 'dotnet', label: '.NET', color: 'var(--lang-dotnet)' },
  { value: 'ts', label: 'TypeScript', color: 'var(--lang-typescript)' },
  { value: 'java', label: 'Java', color: 'var(--lang-java)' },
  { value: 'rust', label: 'Rust', color: 'var(--lang-rust)' },
];

interface LanguageTabsProps {
  selectedLang: Language;
  onSelect: (lang: Language) => void;
  counts: Record<string, number>;
}

export function LanguageTabs({ selectedLang, onSelect, counts }: LanguageTabsProps) {
  const totalCount = useMemo(() => {
    return Object.values(counts).reduce((sum, count) => sum + count, 0);
  }, [counts]);

  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-sm)',
      padding: 'var(--space-xs)',
      background: 'var(--bg-secondary)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--border-primary)',
    }}>
      {LANGUAGE_OPTIONS.map((option) => {
        const isSelected = selectedLang === option.value;
        const count = option.value === 'all' ? totalCount : (counts[option.value] || 0);
        
        return (
          <button
            key={option.value}
            onClick={() => onSelect(option.value)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-xs)',
              padding: 'var(--space-sm) var(--space-md)',
              fontSize: 'var(--text-sm)',
              fontWeight: 500,
              color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
              background: isSelected ? 'var(--bg-tertiary)' : 'transparent',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              position: 'relative',
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                e.currentTarget.style.color = 'var(--text-primary)';
                e.currentTarget.style.background = 'var(--bg-card)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                e.currentTarget.style.color = 'var(--text-secondary)';
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            {/* Color indicator dot */}
            {option.value !== 'all' && (
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: option.color,
                  flexShrink: 0,
                }}
              />
            )}
            
            <span>{option.label}</span>
            
            {/* Count badge */}
            <span
              style={{
                fontSize: 'var(--text-xs)',
                color: isSelected ? 'var(--accent)' : 'var(--text-muted)',
                fontWeight: 600,
                minWidth: '20px',
                textAlign: 'center',
              }}
            >
              {count}
            </span>
            
            {/* Active indicator underline */}
            {isSelected && (
              <span
                style={{
                  position: 'absolute',
                  bottom: '2px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '24px',
                  height: '2px',
                  background: 'var(--accent)',
                  borderRadius: '1px',
                }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

export default LanguageTabs;
