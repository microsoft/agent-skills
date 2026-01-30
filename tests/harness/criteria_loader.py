"""
Acceptance Criteria Loader

Parses acceptance criteria markdown files from skill directories and extracts
structured validation rules including correct/incorrect code patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class CodePattern:
    """A code pattern that represents correct or incorrect usage."""
    
    code: str
    language: str = "python"
    description: str = ""
    is_correct: bool = True
    section: str = ""


@dataclass
class ValidationRule:
    """A rule for validating generated code."""
    
    name: str
    description: str
    correct_patterns: list[CodePattern] = field(default_factory=list)
    incorrect_patterns: list[CodePattern] = field(default_factory=list)
    required_imports: list[str] = field(default_factory=list)
    forbidden_imports: list[str] = field(default_factory=list)
    required_patterns: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)


@dataclass
class AcceptanceCriteria:
    """Complete acceptance criteria for a skill."""
    
    skill_name: str
    source_path: Path
    rules: list[ValidationRule] = field(default_factory=list)
    correct_patterns: list[CodePattern] = field(default_factory=list)
    incorrect_patterns: list[CodePattern] = field(default_factory=list)
    
    def get_rule(self, name: str) -> ValidationRule | None:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name.lower() == name.lower():
                return rule
        return None


class AcceptanceCriteriaLoader:
    """
    Loads and parses acceptance criteria from skill markdown files.
    
    Expected structure in acceptance-criteria.md:
    
    ## Section Name
    
    ### ✅ Correct
    ```python
    # correct code
    ```
    
    ### ❌ Incorrect  
    ```python
    # incorrect code
    ```
    """
    
    SKILLS_DIR = Path(".github/skills")
    CRITERIA_FILENAME = "references/acceptance-criteria.md"
    
    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or Path.cwd()
        self.skills_dir = self.base_path / self.SKILLS_DIR
    
    def list_skills_with_criteria(self) -> list[str]:
        """List all skills that have acceptance criteria."""
        skills = []
        if not self.skills_dir.exists():
            return skills
            
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                criteria_path = skill_dir / self.CRITERIA_FILENAME
                if criteria_path.exists():
                    skills.append(skill_dir.name)
        return sorted(skills)
    
    def load(self, skill_name: str) -> AcceptanceCriteria:
        """Load acceptance criteria for a skill."""
        criteria_path = self.skills_dir / skill_name / self.CRITERIA_FILENAME
        
        if not criteria_path.exists():
            raise FileNotFoundError(
                f"Acceptance criteria not found: {criteria_path}"
            )
        
        content = criteria_path.read_text(encoding="utf-8")
        return self._parse_criteria(skill_name, criteria_path, content)
    
    def _parse_criteria(
        self, 
        skill_name: str, 
        path: Path, 
        content: str
    ) -> AcceptanceCriteria:
        """Parse markdown content into structured criteria."""
        criteria = AcceptanceCriteria(
            skill_name=skill_name,
            source_path=path,
        )
        
        # Extract all code blocks with context
        for pattern in self._extract_code_patterns(content):
            if pattern.is_correct:
                criteria.correct_patterns.append(pattern)
            else:
                criteria.incorrect_patterns.append(pattern)
        
        # Extract validation rules from sections
        criteria.rules = list(self._extract_rules(content))
        
        return criteria
    
    def _extract_code_patterns(self, content: str) -> Iterator[CodePattern]:
        """Extract code blocks with their context (correct/incorrect)."""
        # Split by sections (## headers)
        sections = re.split(r'^## ', content, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Get section title (first line)
            lines = section.split('\n', 1)
            section_title = lines[0].strip()
            section_content = lines[1] if len(lines) > 1 else ""
            
            # Determine if this section contains correct or incorrect examples
            # Look for ### markers or emoji indicators
            is_correct_section = self._is_correct_section(section_content)
            
            # Extract code blocks
            code_blocks = re.findall(
                r'```(\w+)?\n(.*?)```',
                section_content,
                re.DOTALL
            )
            
            for lang, code in code_blocks:
                # Check surrounding context for correct/incorrect markers
                is_correct = self._determine_correctness(
                    code, section_content, is_correct_section
                )
                
                yield CodePattern(
                    code=code.strip(),
                    language=lang or "python",
                    is_correct=is_correct,
                    section=section_title,
                )
    
    def _is_correct_section(self, content: str) -> bool | None:
        """Determine if section primarily contains correct examples."""
        correct_markers = ['✅', 'Correct', 'DO:', 'Good']
        incorrect_markers = ['❌', 'Incorrect', "DON'T:", 'Bad', 'Anti-pattern']
        
        correct_count = sum(content.count(m) for m in correct_markers)
        incorrect_count = sum(content.count(m) for m in incorrect_markers)
        
        if correct_count > incorrect_count:
            return True
        elif incorrect_count > correct_count:
            return False
        return None  # Mixed or unclear
    
    def _determine_correctness(
        self, 
        code: str, 
        context: str,
        section_default: bool | None
    ) -> bool:
        """Determine if a specific code block is correct or incorrect."""
        # Find the position of this code in the context
        code_pos = context.find(code[:50]) if len(code) > 50 else context.find(code)
        if code_pos == -1:
            return section_default if section_default is not None else True
        
        # Look at the 200 characters before the code block
        preceding = context[max(0, code_pos - 200):code_pos]
        
        # Check for markers
        if '❌' in preceding or 'Incorrect' in preceding or "DON'T" in preceding:
            return False
        if '✅' in preceding or 'Correct' in preceding:
            return True
        
        return section_default if section_default is not None else True
    
    def _extract_rules(self, content: str) -> Iterator[ValidationRule]:
        """Extract structured validation rules from content."""
        # Find sections that define rules
        sections = re.split(r'^## ', content, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.split('\n', 1)
            title = lines[0].strip()
            body = lines[1] if len(lines) > 1 else ""
            
            # Skip non-rule sections
            if any(skip in title.lower() for skip in ['overview', 'introduction', 'quick reference']):
                continue
            
            rule = ValidationRule(
                name=title,
                description=self._extract_description(body),
            )
            
            # Extract patterns for this rule
            for pattern in self._extract_code_patterns(f"## {section}"):
                if pattern.is_correct:
                    rule.correct_patterns.append(pattern)
                else:
                    rule.incorrect_patterns.append(pattern)
            
            # Extract import requirements
            rule.required_imports = self._extract_required_imports(body)
            rule.forbidden_imports = self._extract_forbidden_imports(body)
            
            if rule.correct_patterns or rule.incorrect_patterns:
                yield rule
    
    def _extract_description(self, content: str) -> str:
        """Extract the description (first paragraph) from content."""
        lines = []
        for line in content.split('\n'):
            if line.startswith('#') or line.startswith('```'):
                break
            if line.strip():
                lines.append(line.strip())
            elif lines:  # Empty line after content
                break
        return ' '.join(lines)
    
    def _extract_required_imports(self, content: str) -> list[str]:
        """Extract required imports mentioned in the content."""
        imports = []
        # Look for patterns like "must import", "required import", etc.
        import_pattern = r'from\s+([\w.]+)\s+import\s+([\w,\s]+)'
        for match in re.finditer(import_pattern, content):
            module = match.group(1)
            names = [n.strip() for n in match.group(2).split(',')]
            for name in names:
                imports.append(f"from {module} import {name}")
        return imports
    
    def _extract_forbidden_imports(self, content: str) -> list[str]:
        """Extract forbidden imports (from incorrect sections)."""
        # This would need context about which imports are in "incorrect" examples
        return []


# CLI for testing
if __name__ == "__main__":
    import sys
    
    loader = AcceptanceCriteriaLoader()
    
    if len(sys.argv) > 1:
        skill_name = sys.argv[1]
        try:
            criteria = loader.load(skill_name)
            print(f"Loaded criteria for: {criteria.skill_name}")
            print(f"Source: {criteria.source_path}")
            print(f"Rules: {len(criteria.rules)}")
            print(f"Correct patterns: {len(criteria.correct_patterns)}")
            print(f"Incorrect patterns: {len(criteria.incorrect_patterns)}")
            
            for rule in criteria.rules[:5]:
                print(f"\n  Rule: {rule.name}")
                print(f"    Correct: {len(rule.correct_patterns)}")
                print(f"    Incorrect: {len(rule.incorrect_patterns)}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        skills = loader.list_skills_with_criteria()
        print(f"Skills with acceptance criteria ({len(skills)}):")
        for skill in skills:
            print(f"  - {skill}")
