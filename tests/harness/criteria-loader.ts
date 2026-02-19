/**
 * Acceptance Criteria Loader
 *
 * Parses acceptance criteria markdown files from skill directories and extracts
 * structured validation rules including correct/incorrect code patterns.
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import type {
  AcceptanceCriteria,
  CodePattern,
  ValidationRule,
  Language,
} from "./types.js";
import {
  createAcceptanceCriteria,
  createCodePattern,
  createValidationRule,
  detectLanguage,
} from "./types.js";

// =============================================================================
// Constants
// =============================================================================

const SKILLS_DIR = ".github/skills";
const CRITERIA_FILENAME = "references/acceptance-criteria.md";

// =============================================================================
// AcceptanceCriteriaLoader
// =============================================================================

/**
 * Loads and parses acceptance criteria from skill markdown files.
 *
 * Expected structure in acceptance-criteria.md:
 *
 * ## Section Name
 *
 * ### ✅ Correct
 * ```python
 * # correct code
 * ```
 *
 * ### ❌ Incorrect
 * ```python
 * # incorrect code
 * ```
 */
export class AcceptanceCriteriaLoader {
  private readonly basePath: string;
  private readonly skillsDir: string;

  constructor(basePath?: string) {
    this.basePath = basePath ?? process.cwd();
    this.skillsDir = join(this.basePath, SKILLS_DIR);
  }

  /**
   * List all skills that have acceptance criteria.
   */
  listSkillsWithCriteria(): string[] {
    const skills: string[] = [];

    if (!existsSync(this.skillsDir)) {
      return skills;
    }

    const entries = readdirSync(this.skillsDir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory() || entry.isSymbolicLink()) {
        const criteriaPath = join(
          this.skillsDir,
          entry.name,
          CRITERIA_FILENAME
        );
        if (existsSync(criteriaPath)) {
          skills.push(entry.name);
        }
      }
    }

    return skills.sort();
  }

  /**
   * Load acceptance criteria for a skill.
   */
  load(skillName: string): AcceptanceCriteria {
    const criteriaPath = join(this.skillsDir, skillName, CRITERIA_FILENAME);

    if (!existsSync(criteriaPath)) {
      throw new Error(`Acceptance criteria not found: ${criteriaPath}`);
    }

    const content = readFileSync(criteriaPath, "utf-8");
    return this.parseCriteria(skillName, criteriaPath, content);
  }

  /**
   * Parse markdown content into structured criteria.
   */
  private parseCriteria(
    skillName: string,
    sourcePath: string,
    content: string
  ): AcceptanceCriteria {
    const language = detectLanguage(skillName);

    const criteria = createAcceptanceCriteria({
      skillName,
      sourcePath,
      language,
    });

    // Extract all code blocks with context
    for (const pattern of this.extractCodePatterns(content)) {
      if (pattern.isCorrect) {
        criteria.correctPatterns.push(pattern);
      } else {
        criteria.incorrectPatterns.push(pattern);
      }
    }

    // Extract validation rules from sections
    criteria.rules = Array.from(this.extractRules(content));

    return criteria;
  }

  /**
   * Extract code blocks with their context (correct/incorrect).
   */
  private *extractCodePatterns(content: string): Generator<CodePattern> {
    // Split by sections (## headers)
    const sections = content.split(/^## /m);

    for (const section of sections) {
      if (!section.trim()) {
        continue;
      }

      // Get section title (first line)
      const lines = section.split("\n");
      const sectionTitle = lines[0]?.trim() ?? "";
      const sectionContent = lines.slice(1).join("\n");

      // Determine if this section contains correct or incorrect examples
      const isCorrectSection = this.isCorrectSection(sectionContent);

      // Extract code blocks: ```lang\ncode\n```
      const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
      let match: RegExpExecArray | null;

      while ((match = codeBlockRegex.exec(sectionContent)) !== null) {
        const lang = match[1] ?? "python";
        const code = match[2]?.trim() ?? "";

        // Check surrounding context for correct/incorrect markers
        const isCorrect = this.determineCorrectness(
          code,
          sectionContent,
          isCorrectSection
        );

        yield createCodePattern({
          code,
          language: lang as Language,
          isCorrect,
          section: sectionTitle,
        });
      }
    }
  }

  /**
   * Determine if section primarily contains correct examples.
   */
  private isCorrectSection(content: string): boolean | null {
    const correctMarkers = ["✅", "Correct", "DO:", "Good"];
    const incorrectMarkers = ["❌", "Incorrect", "DON'T:", "Bad", "Anti-pattern"];

    let correctCount = 0;
    let incorrectCount = 0;

    for (const marker of correctMarkers) {
      correctCount += (content.match(new RegExp(marker, "g")) ?? []).length;
    }

    for (const marker of incorrectMarkers) {
      incorrectCount += (content.match(new RegExp(marker, "g")) ?? []).length;
    }

    if (correctCount > incorrectCount) {
      return true;
    } else if (incorrectCount > correctCount) {
      return false;
    }
    return null; // Mixed or unclear
  }

  /**
   * Determine if a specific code block is correct or incorrect.
   */
  private determineCorrectness(
    code: string,
    context: string,
    sectionDefault: boolean | null
  ): boolean {
    // Find the position of this code in the context
    const searchCode = code.length > 50 ? code.slice(0, 50) : code;
    const codePos = context.indexOf(searchCode);

    if (codePos === -1) {
      return sectionDefault ?? true;
    }

    // Look at the 200 characters before the code block
    const preceding = context.slice(Math.max(0, codePos - 200), codePos);

    // Check for markers
    if (
      preceding.includes("❌") ||
      preceding.includes("Incorrect") ||
      preceding.includes("DON'T")
    ) {
      return false;
    }
    if (preceding.includes("✅") || preceding.includes("Correct")) {
      return true;
    }

    return sectionDefault ?? true;
  }

  /**
   * Extract structured validation rules from content.
   */
  private *extractRules(content: string): Generator<ValidationRule> {
    // Split by sections (## headers)
    const sections = content.split(/^## /m);

    for (const section of sections) {
      if (!section.trim()) {
        continue;
      }

      const lines = section.split("\n");
      const title = lines[0]?.trim() ?? "";
      const body = lines.slice(1).join("\n");

      // Skip non-rule sections
      const skipKeywords = ["overview", "introduction", "quick reference"];
      if (skipKeywords.some((kw) => title.toLowerCase().includes(kw))) {
        continue;
      }

      const rule = createValidationRule({
        name: title,
        description: this.extractDescription(body),
      });

      // Extract patterns for this rule
      for (const pattern of this.extractCodePatterns(`## ${section}`)) {
        if (pattern.isCorrect) {
          rule.correctPatterns.push(pattern);
        } else {
          rule.incorrectPatterns.push(pattern);
        }
      }

      // Extract import requirements
      rule.requiredImports = this.extractRequiredImports(body);
      rule.forbiddenImports = this.extractForbiddenImports(body);

      if (rule.correctPatterns.length > 0 || rule.incorrectPatterns.length > 0) {
        yield rule;
      }
    }
  }

  /**
   * Extract the description (first paragraph) from content.
   */
  private extractDescription(content: string): string {
    const lines: string[] = [];

    for (const line of content.split("\n")) {
      if (line.startsWith("#") || line.startsWith("```")) {
        break;
      }
      if (line.trim()) {
        lines.push(line.trim());
      } else if (lines.length > 0) {
        // Empty line after content
        break;
      }
    }

    return lines.join(" ");
  }

  /**
   * Extract required imports mentioned in the content.
   */
  private extractRequiredImports(content: string): string[] {
    const imports: string[] = [];
    // Look for patterns like "from module import name"
    const importPattern = /from\s+([\w.]+)\s+import\s+([\w,\s]+)/g;
    let match: RegExpExecArray | null;

    while ((match = importPattern.exec(content)) !== null) {
      const module = match[1];
      const names = match[2]?.split(",").map((n) => n.trim()) ?? [];
      for (const name of names) {
        if (name && module) {
          imports.push(`from ${module} import ${name}`);
        }
      }
    }

    return imports;
  }

  /**
   * Extract forbidden imports (from incorrect sections).
   * Note: This is a placeholder - would need context about which imports are in "incorrect" examples.
   */
  private extractForbiddenImports(_content: string): string[] {
    // This would need more sophisticated parsing to determine
    // which imports appear specifically in incorrect examples
    return [];
  }
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get rule by name from criteria.
 */
export function getRule(
  criteria: AcceptanceCriteria,
  name: string
): ValidationRule | undefined {
  return criteria.rules.find(
    (rule) => rule.name.toLowerCase() === name.toLowerCase()
  );
}

/**
 * Auto-detect language from code patterns.
 */
export function detectLanguageFromPatterns(
  criteria: AcceptanceCriteria
): Language {
  const allPatterns = [
    ...criteria.correctPatterns,
    ...criteria.incorrectPatterns,
  ];

  if (allPatterns.length === 0) {
    return "python";
  }

  const langCounts: Record<string, number> = {};

  for (const pattern of allPatterns) {
    const lang = pattern.language.toLowerCase();
    langCounts[lang] = (langCounts[lang] ?? 0) + 1;
  }

  let maxCount = 0;
  let detected: Language = "python";

  for (const [lang, count] of Object.entries(langCounts)) {
    if (count > maxCount) {
      maxCount = count;
      detected = lang as Language;
    }
  }

  return detected;
}

// =============================================================================
// CLI Entry Point
// =============================================================================

/**
 * CLI for testing the criteria loader.
 */
export async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const loader = new AcceptanceCriteriaLoader();

  if (args.length > 0) {
    const skillName = args[0];
    if (!skillName) {
      console.error("Error: skill name is required");
      process.exit(1);
    }
    try {
      const criteria = loader.load(skillName);
      console.log(`Loaded criteria for: ${criteria.skillName}`);
      console.log(`Source: ${criteria.sourcePath}`);
      console.log(`Rules: ${criteria.rules.length}`);
      console.log(`Correct patterns: ${criteria.correctPatterns.length}`);
      console.log(`Incorrect patterns: ${criteria.incorrectPatterns.length}`);

      for (const rule of criteria.rules.slice(0, 5)) {
        console.log(`\n  Rule: ${rule.name}`);
        console.log(`    Correct: ${rule.correctPatterns.length}`);
        console.log(`    Incorrect: ${rule.incorrectPatterns.length}`);
      }
    } catch (error) {
      console.error(`Error: ${error instanceof Error ? error.message : error}`);
      process.exit(1);
    }
  } else {
    const skills = loader.listSkillsWithCriteria();
    console.log(`Skills with acceptance criteria (${skills.length}):`);
    for (const skill of skills) {
      console.log(`  - ${skill}`);
    }
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
