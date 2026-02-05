import { useEffect, useState, useCallback } from 'react';
import { Command } from 'cmdk';

interface Skill {
  name: string;
  description: string;
  lang: string;
  category: string;
}

interface CommandPaletteProps {
  skills: Skill[];
  onSelect: (skill: Skill) => void;
}

const LANG_COLORS: Record<string, string> = {
  py: '#60a5fa',
  dotnet: '#a78bfa',
  ts: '#facc15',
  java: '#f87171',
  rust: '#fb923c',
  core: '#9ca3af',
};

const LANG_LABELS: Record<string, string> = {
  py: 'Python',
  dotnet: '.NET',
  ts: 'TypeScript',
  java: 'Java',
  rust: 'Rust',
  core: 'Core',
};

export function CommandPalette({ skills, onSelect }: CommandPaletteProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === 'Escape') {
        setOpen(false);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const handleSelect = useCallback((skill: Skill) => {
    onSelect(skill);
    setOpen(false);
    setSearch('');
  }, [onSelect]);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-md)',
          padding: 'var(--space-sm) var(--space-md)',
          minWidth: '240px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-primary)',
          borderRadius: 'var(--radius-lg)',
          color: 'var(--text-muted)',
          fontSize: 'var(--text-sm)',
          cursor: 'pointer',
          transition: 'all var(--transition-fast)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-hover)';
          e.currentTarget.style.background = 'var(--bg-tertiary)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-primary)';
          e.currentTarget.style.background = 'var(--bg-secondary)';
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <span style={{ flex: 1, textAlign: 'left' }}>Search skills...</span>
        <kbd style={{
          padding: '2px 6px',
          fontSize: 'var(--text-xs)',
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-primary)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-secondary)',
        }}>
          ⌘K
        </kbd>
      </button>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.6)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '15vh',
        zIndex: 9999,
      }}
      onClick={() => setOpen(false)}
    >
      <Command
        style={{
          width: '100%',
          maxWidth: '560px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-primary)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-md)',
          padding: 'var(--space-md) var(--space-lg)',
          borderBottom: '1px solid var(--border-primary)',
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <Command.Input
            value={search}
            onValueChange={setSearch}
            placeholder="Search skills by name or description..."
            autoFocus
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: 'var(--text-base)',
              color: 'var(--text-primary)',
            }}
          />
          <kbd style={{
            padding: '2px 8px',
            fontSize: 'var(--text-xs)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-muted)',
          }}>
            ESC
          </kbd>
        </div>

        <Command.List style={{
          maxHeight: '400px',
          overflow: 'auto',
          padding: 'var(--space-sm)',
        }}>
          <Command.Empty style={{
            padding: 'var(--space-xl)',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: 'var(--text-sm)',
          }}>
            No skills found.
          </Command.Empty>

          {skills.map((skill) => (
            <Command.Item
              key={skill.name}
              value={`${skill.name} ${skill.description}`}
              onSelect={() => handleSelect(skill)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 'var(--space-md)',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                transition: 'background var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--bg-tertiary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              <span
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: LANG_COLORS[skill.lang] || LANG_COLORS.core,
                  flexShrink: 0,
                  marginTop: '4px',
                }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-sm)',
                }}>
                  <span style={{
                    fontSize: 'var(--text-sm)',
                    fontWeight: 500,
                    color: 'var(--text-primary)',
                  }}>
                    {skill.name}
                  </span>
                  <span style={{
                    fontSize: '10px',
                    color: LANG_COLORS[skill.lang] || LANG_COLORS.core,
                    textTransform: 'uppercase',
                    fontWeight: 600,
                  }}>
                    {LANG_LABELS[skill.lang] || skill.lang}
                  </span>
                </div>
                <p style={{
                  margin: 0,
                  marginTop: '2px',
                  fontSize: 'var(--text-xs)',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {skill.description}
                </p>
              </div>
            </Command.Item>
          ))}
        </Command.List>
      </Command>
    </div>
  );
}

export default CommandPalette;
