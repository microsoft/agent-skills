import { useState, useMemo, useCallback, useEffect } from 'react';
import { LanguageTabs, type Language } from './LanguageTabs';
import { CategoryTabs, type Category } from './CategoryTabs';
import { SearchInput } from './SearchInput';
import { SkillCard, type Skill } from './SkillCard';
import { SkillDetailModal } from './SkillDetailModal';

interface SkillInput {
  name: string;
  description: string;
  lang: string;
  category: string;
  path?: string;
  package?: string;
}

interface SkillsSectionProps {
  skills: SkillInput[];
}

const LANG_DISPLAY: Record<string, string> = {
  py: 'Python',
  dotnet: '.NET',
  ts: 'TypeScript',
  java: 'Java',
  rust: 'Rust',
  core: 'Core',
};

function getSkillFromHash(): string | null {
  if (typeof window === 'undefined') return null;
  const hash = window.location.hash;
  if (hash.startsWith('#skill=')) {
    return decodeURIComponent(hash.slice('#skill='.length));
  }
  return null;
}

export function SkillsSection({ skills }: SkillsSectionProps) {
  const [selectedLang, setSelectedLang] = useState<Language>('all');
  const [selectedCategory, setSelectedCategory] = useState<Category>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // On mount, check URL hash for a skill deep link
  useEffect(() => {
    const openSkillFromHash = () => {
      const skillName = getSkillFromHash();
      if (!skillName) return;
      const found = skills.find(s => s.name === skillName);
      if (found) {
        setSelectedSkill({
          name: found.name,
          description: found.description,
          language: found.lang,
          category: found.category,
          path: found.path || `.github/skills/${found.name}`,
          package: found.package,
        });
      }
    };

    openSkillFromHash();
    window.addEventListener('hashchange', openSkillFromHash);
    return () => window.removeEventListener('hashchange', openSkillFromHash);
  }, [skills]);

  // Number of rows to show when collapsed (responsive: more columns = fewer items visible per row)
  const COLLAPSED_ROWS = 2;
  const ITEMS_PER_ROW_DESKTOP = 4;
  const MAX_VISIBLE_COLLAPSED = COLLAPSED_ROWS * ITEMS_PER_ROW_DESKTOP;
  
  // Card height estimate: padding (24px * 2) + title (~24px) + description (~72px) + footer (~24px) + gaps (~16px) = ~184px
  // Add some buffer for longer titles that wrap = ~200px per card
  // Plus grid gap (24px) between rows
  const CARD_HEIGHT_ESTIMATE = 200;
  const GRID_GAP = 24; // var(--space-lg)
  const COLLAPSED_HEIGHT = (CARD_HEIGHT_ESTIMATE * COLLAPSED_ROWS) + (GRID_GAP * (COLLAPSED_ROWS - 1)) + 40; // +40 for button overlap space

  const langCounts = useMemo(() => {
    return skills.reduce((acc, skill) => {
      acc[skill.lang] = (acc[skill.lang] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }, [skills]);

  const categoryCounts = useMemo(() => {
    const filtered = selectedLang === 'all' 
      ? skills 
      : skills.filter(s => s.lang === selectedLang);
    
    return filtered.reduce((acc, skill) => {
      acc[skill.category] = (acc[skill.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }, [skills, selectedLang]);

  const filteredSkills = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();
    return skills.filter(skill => {
      const langMatch = selectedLang === 'all' || skill.lang === selectedLang;
      const catMatch = selectedCategory === 'all' || skill.category === selectedCategory;
      const searchMatch = !query || 
        skill.name.toLowerCase().includes(query) || 
        skill.description.toLowerCase().includes(query);
      return langMatch && catMatch && searchMatch;
    });
  }, [skills, selectedLang, selectedCategory, searchQuery]);

  const handleLangChange = useCallback((lang: Language) => {
    setSelectedLang(lang);
    setSelectedCategory('all');
    setIsExpanded(false);
  }, []);

  const handleCategoryChange = useCallback((category: Category) => {
    setSelectedCategory(category);
    setIsExpanded(false);
  }, []);

  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
    setIsExpanded(false);
  }, []);

  return (
    <section style={{ padding: 'var(--space-md) 0 var(--space-2xl)' }}>
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <SearchInput
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Search skills by name or description..."
        />
      </div>

      <div style={{ marginBottom: 'var(--space-md)' }}>
        <LanguageTabs
          selectedLang={selectedLang}
          onSelect={handleLangChange}
          counts={langCounts}
        />
      </div>

      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <CategoryTabs
          selectedCategory={selectedCategory}
          onSelect={handleCategoryChange}
          counts={categoryCounts}
        />
      </div>

      <div style={{
        marginBottom: 'var(--space-lg)',
        fontSize: 'var(--text-sm)',
        color: 'var(--text-secondary)',
      }}>
        Showing <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{filteredSkills.length}</span> skills
        {searchQuery && (
          <span> matching "<span style={{ color: 'var(--text-primary)' }}>{searchQuery}</span>"</span>
        )}
        {selectedLang !== 'all' && (
          <span> in <span style={{ color: 'var(--text-primary)' }}>{LANG_DISPLAY[selectedLang] || selectedLang}</span></span>
        )}
        {selectedCategory !== 'all' && (
          <span> / <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{selectedCategory}</span></span>
        )}
      </div>

      <div style={{ position: 'relative' }}>
        <div 
          className="skills-grid"
          style={{
            maxHeight: isExpanded || filteredSkills.length <= MAX_VISIBLE_COLLAPSED ? 'none' : `${COLLAPSED_HEIGHT}px`,
            overflow: 'hidden',
            transition: 'max-height 0.3s ease-out',
          }}
        >
          {filteredSkills.map((skill) => {
            const mappedSkill: Skill = {
              name: skill.name,
              description: skill.description,
              language: skill.lang,
              category: skill.category,
              path: skill.path || `.github/skills/${skill.name}`,
              package: skill.package,
            };
            return (
              <SkillCard
                key={skill.name}
                skill={mappedSkill}
                onClick={() => {
                  setSelectedSkill(mappedSkill);
                  window.history.replaceState(null, '', `#skill=${encodeURIComponent(mappedSkill.name)}`);
                }}
              />
            );
          })}
        </div>
        
        {!isExpanded && filteredSkills.length > MAX_VISIBLE_COLLAPSED && (
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '120px',
            background: 'linear-gradient(to bottom, transparent, var(--bg-primary) 80%)',
            pointerEvents: 'none',
          }} />
        )}
        
        {filteredSkills.length > MAX_VISIBLE_COLLAPSED && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginTop: isExpanded ? 'var(--space-xl)' : '-40px',
            position: 'relative',
            zIndex: 10,
          }}>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-sm)',
                padding: 'var(--space-sm) var(--space-lg)',
                fontSize: 'var(--text-sm)',
                fontWeight: 500,
                color: 'var(--text-primary)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--bg-card-hover)';
                e.currentTarget.style.borderColor = 'var(--border-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'var(--bg-tertiary)';
                e.currentTarget.style.borderColor = 'var(--border-primary)';
              }}
            >
              {isExpanded ? (
                <>
                  Show Less
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ transform: 'rotate(180deg)' }}>
                    <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </>
              ) : (
                <>
                  Show More ({filteredSkills.length - MAX_VISIBLE_COLLAPSED} more)
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {filteredSkills.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: 'var(--space-3xl) var(--space-xl)',
          color: 'var(--text-secondary)',
        }}>
          <p style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-sm)' }}>
            No skills found
          </p>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
            Try adjusting your filters or search query
          </p>
        </div>
      )}

      <SkillDetailModal
        skill={selectedSkill}
        onClose={() => {
          setSelectedSkill(null);
          window.history.replaceState(null, '', window.location.pathname + window.location.search);
        }}
      />
    </section>
  );
}

export default SkillsSection;
