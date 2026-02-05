import { useState, useCallback } from 'react';

export interface Skill {
  name: string;
  description: string;
  language: string;
  category: string;
  path: string;
  package?: string;
}

interface SkillCardProps {
  skill: Skill;
}

const LANG_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  py: {
    bg: 'rgba(96, 165, 250, 0.15)',
    text: '#60a5fa',
    border: 'rgba(96, 165, 250, 0.3)',
  },
  dotnet: {
    bg: 'rgba(167, 139, 250, 0.15)',
    text: '#a78bfa',
    border: 'rgba(167, 139, 250, 0.3)',
  },
  ts: {
    bg: 'rgba(250, 204, 21, 0.15)',
    text: '#facc15',
    border: 'rgba(250, 204, 21, 0.3)',
  },
  java: {
    bg: 'rgba(248, 113, 113, 0.15)',
    text: '#f87171',
    border: 'rgba(248, 113, 113, 0.3)',
  },
  rust: {
    bg: 'rgba(251, 146, 60, 0.15)',
    text: '#fb923c',
    border: 'rgba(251, 146, 60, 0.3)',
  },
  core: {
    bg: 'rgba(156, 163, 175, 0.15)',
    text: '#9ca3af',
    border: 'rgba(156, 163, 175, 0.3)',
  },
};

const LANG_LABELS: Record<string, string> = {
  py: 'Python',
  dotnet: '.NET',
  ts: 'TypeScript',
  java: 'Java',
  rust: 'Rust',
  core: 'Core',
};

export function SkillCard({ skill }: SkillCardProps) {
  const [copied, setCopied] = useState(false);
  
  const langStyle = LANG_STYLES[skill.language] || LANG_STYLES.core;
  const langLabel = LANG_LABELS[skill.language] || skill.language;
  
  const installCommand = `npx skills add microsoft/skills --skill ${skill.name}`;
  
  const handleCopy = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      await navigator.clipboard.writeText(installCommand);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [installCommand]);

  const githubUrl = `https://github.com/microsoft/skills/tree/main/${skill.path}`;

  return (
    <a
      href={githubUrl}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'block',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-lg)',
        textDecoration: 'none',
        transition: 'all var(--transition-base)',
        cursor: 'pointer',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'var(--bg-card-hover)';
        e.currentTarget.style.borderColor = 'var(--border-hover)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'var(--bg-card)';
        e.currentTarget.style.borderColor = 'var(--border-primary)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', height: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-sm)' }}>
          <h3 style={{
            fontSize: 'var(--text-base)',
            fontWeight: 600,
            color: 'var(--text-primary)',
            margin: 0,
            lineHeight: 1.4,
            wordBreak: 'break-word',
          }}>
            {skill.name}
          </h3>
          
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '2px 8px',
              fontSize: 'var(--text-xs)',
              fontWeight: 500,
              borderRadius: 'var(--radius-sm)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              background: langStyle.bg,
              color: langStyle.text,
              border: `1px solid ${langStyle.border}`,
              flexShrink: 0,
            }}
          >
            {langLabel}
          </span>
        </div>
        
        <p style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--text-secondary)',
          margin: 0,
          lineHeight: 1.6,
          flex: 1,
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}>
          {skill.description}
        </p>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-sm)',
          marginTop: 'auto',
        }}>
          <span style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--text-muted)',
            textTransform: 'capitalize',
          }}>
            {skill.category}
          </span>
          
          <button
            onClick={handleCopy}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              fontSize: 'var(--text-xs)',
              fontWeight: 500,
              color: copied ? '#22c55e' : 'var(--text-secondary)',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-primary)',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
            }}
            onMouseEnter={(e) => {
              if (!copied) {
                e.currentTarget.style.color = 'var(--text-primary)';
                e.currentTarget.style.borderColor = 'var(--border-hover)';
              }
            }}
            onMouseLeave={(e) => {
              if (!copied) {
                e.currentTarget.style.color = 'var(--text-secondary)';
                e.currentTarget.style.borderColor = 'var(--border-primary)';
              }
            }}
            title={`Copy: ${installCommand}`}
          >
            {copied ? (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
                Copy
              </>
            )}
          </button>
        </div>
      </div>
    </a>
  );
}

export default SkillCard;
