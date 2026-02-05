import { useState, useMemo, useCallback } from 'react';
import { LanguageTabs, type Language } from './LanguageTabs';
import { CategoryTabs, type Category } from './CategoryTabs';
import { CommandPalette } from './CommandPalette';
import { SkillCard } from './SkillCard';

interface Skill {
  name: string;
  description: string;
  lang: string;
  category: string;
  package?: string;
}

interface SkillsSectionProps {
  skills: Skill[];
}

const LANG_DISPLAY: Record<string, string> = {
  py: 'Python',
  dotnet: '.NET',
  ts: 'TypeScript',
  java: 'Java',
  rust: 'Rust',
  core: 'Core',
};

export function SkillsSection({ skills }: SkillsSectionProps) {
  const [selectedLang, setSelectedLang] = useState<Language>('all');
  const [selectedCategory, setSelectedCategory] = useState<Category>('all');

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
    return skills.filter(skill => {
      const langMatch = selectedLang === 'all' || skill.lang === selectedLang;
      const catMatch = selectedCategory === 'all' || skill.category === selectedCategory;
      return langMatch && catMatch;
    });
  }, [skills, selectedLang, selectedCategory]);

  const handleLangChange = useCallback((lang: Language) => {
    setSelectedLang(lang);
    setSelectedCategory('all');
  }, []);

  const handleSkillSelect = useCallback((skill: Skill) => {
    const url = `https://github.com/microsoft/skills/tree/main/.github/skills/${skill.name}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, []);

  return (
    <section style={{ padding: 'var(--space-2xl) 0' }}>
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          fontSize: 'var(--text-xs)',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--text-secondary)',
          marginBottom: 'var(--space-sm)',
        }}>
          <span style={{ color: 'var(--accent)', fontSize: '0.5rem' }}>●</span>
          Skills
        </span>
        <h2 style={{
          fontSize: 'var(--text-2xl)',
          fontWeight: 700,
          color: 'var(--text-primary)',
          margin: 0,
        }}>
          Browse all {skills.length} skills
        </h2>
      </div>

      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <CommandPalette skills={skills} onSelect={handleSkillSelect} />
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
          onSelect={setSelectedCategory}
          counts={categoryCounts}
        />
      </div>

      <div style={{
        marginBottom: 'var(--space-lg)',
        fontSize: 'var(--text-sm)',
        color: 'var(--text-secondary)',
      }}>
        Showing <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{filteredSkills.length}</span> skills
        {selectedLang !== 'all' && (
          <span> in <span style={{ color: 'var(--text-primary)' }}>{LANG_DISPLAY[selectedLang] || selectedLang}</span></span>
        )}
        {selectedCategory !== 'all' && (
          <span> / <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{selectedCategory}</span></span>
        )}
      </div>

      <div className="skills-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 'var(--space-lg)',
      }}>
        {filteredSkills.map((skill) => (
          <SkillCard
            key={skill.name}
            skill={{
              name: skill.name,
              description: skill.description,
              language: skill.lang,
              category: skill.category,
              path: `.github/skills/${skill.name}`,
              package: skill.package,
            }}
          />
        ))}
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
    </section>
  );
}

export default SkillsSection;
