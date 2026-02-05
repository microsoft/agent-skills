import { useState, useMemo, useCallback } from 'react';
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

export function SkillsSection({ skills }: SkillsSectionProps) {
  const [selectedLang, setSelectedLang] = useState<Language>('all');
  const [selectedCategory, setSelectedCategory] = useState<Category>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

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
  }, []);

  return (
    <section style={{ padding: 'var(--space-md) 0 var(--space-2xl)' }}>
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
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

      <div className="skills-grid">
        {filteredSkills.map((skill) => {
          const mappedSkill: Skill = {
            name: skill.name,
            description: skill.description,
            language: skill.lang,
            category: skill.category,
            path: `.github/skills/${skill.name}`,
            package: skill.package,
          };
          return (
            <SkillCard
              key={skill.name}
              skill={mappedSkill}
              onClick={() => setSelectedSkill(mappedSkill)}
            />
          );
        })}
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
        onClose={() => setSelectedSkill(null)}
      />
    </section>
  );
}

export default SkillsSection;
