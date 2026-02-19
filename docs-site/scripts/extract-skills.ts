import * as fs from "fs";
import * as path from "path";
import matter from "gray-matter";

function preprocessYamlFrontmatter(content: string): string {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return content;

  const frontmatter = match[1];
  const fixedFrontmatter = frontmatter.replace(
    /^(\s*package:\s*)(@.+)$/gm,
    '$1"$2"'
  );

  return content.replace(frontmatter, fixedFrontmatter);
}

interface Skill {
  name: string;
  description: string;
  package?: string;
  lang: "py" | "dotnet" | "ts" | "java" | "rust" | "core";
  category: string;
  path: string;
}

interface SkillFrontmatter {
  name?: string;
  description?: string;
  package?: string;
}

const LANG_MAP: Record<string, Skill["lang"]> = {
  python: "py",
  dotnet: "dotnet",
  typescript: "ts",
  java: "java",
  rust: "rust",
  core: "core",
};

const SUFFIX_MAP: Record<string, Skill["lang"]> = {
  "-py": "py",
  "-dotnet": "dotnet",
  "-ts": "ts",
  "-java": "java",
  "-rust": "rust",
};

function inferLangFromName(skillName: string): Skill["lang"] {
  for (const [suffix, lang] of Object.entries(SUFFIX_MAP)) {
    if (skillName.endsWith(suffix)) {
      return lang;
    }
  }
  return "core";
}

function findSymlinkInfo(
  skillName: string,
  skillsDir: string
): { lang: Skill["lang"]; category: string } | null {
  const langDirs = fs.readdirSync(skillsDir);

  for (const langDir of langDirs) {
    const langPath = path.join(skillsDir, langDir);
    if (!fs.statSync(langPath).isDirectory()) continue;

    const categoryDirs = fs.readdirSync(langPath);
    for (const categoryDir of categoryDirs) {
      const categoryPath = path.join(langPath, categoryDir);
      if (!fs.statSync(categoryPath).isDirectory()) continue;

      const links = fs.readdirSync(categoryPath);
      for (const link of links) {
        const linkPath = path.join(categoryPath, link);
        try {
          const stat = fs.lstatSync(linkPath);
          if (stat.isSymbolicLink()) {
            const target = fs.readlinkSync(linkPath);
            const targetSkillName = path.basename(target);
            if (targetSkillName === skillName) {
              const lang = LANG_MAP[langDir] || "core";
              return { lang, category: categoryDir };
            }
          }
        } catch {
          continue;
        }
      }
    }
  }
  return null;
}

const PLUGIN_LANG_MAP: Record<string, Skill["lang"]> = {
  "azure-sdk-python": "py",
  "azure-sdk-dotnet": "dotnet",
  "azure-sdk-typescript": "ts",
  "azure-sdk-java": "java",
  "azure-sdk-rust": "rust",
};

function extractSkillFromDir(
  skillDir: string,
  skillPath: string,
  repoRelativePath: string,
  lang: Skill["lang"],
  category: string
): Skill | null {
  const skillMdPath = path.join(skillPath, "SKILL.md");
  if (!fs.existsSync(skillMdPath)) return null;

  try {
    const rawContent = fs.readFileSync(skillMdPath, "utf-8");
    const content = preprocessYamlFrontmatter(rawContent);
    const { data } = matter(content);
    const frontmatter = data as SkillFrontmatter;

    if (!frontmatter.name) {
      console.warn(`Skipping ${skillDir}: missing name in frontmatter`);
      return null;
    }

    const skill: Skill = {
      name: frontmatter.name,
      description: frontmatter.description || frontmatter.name,
      lang,
      category,
      path: repoRelativePath,
    };

    if (frontmatter.package) {
      skill.package = frontmatter.package;
    }

    return skill;
  } catch (err) {
    console.warn(`Skipping ${skillDir}: ${(err as Error).message}`);
    return null;
  }
}

function extractSkills(): Skill[] {
  const projectRoot = path.resolve(import.meta.dirname, "../..");
  const pluginsDir = path.join(projectRoot, ".github/plugins");
  const skillsSourceDir = path.join(projectRoot, ".github/skills");
  const skillsSymlinkDir = path.join(projectRoot, "skills");

  const skills: Skill[] = [];
  const seen = new Set<string>();

  // 1. Scan plugin bundles: .github/plugins/azure-sdk-*/skills/
  if (fs.existsSync(pluginsDir)) {
    for (const pluginName of fs.readdirSync(pluginsDir)) {
      const lang = PLUGIN_LANG_MAP[pluginName];
      if (!lang) continue;

      const pluginSkillsDir = path.join(pluginsDir, pluginName, "skills");
      if (!fs.existsSync(pluginSkillsDir)) continue;

      for (const skillDir of fs.readdirSync(pluginSkillsDir)) {
        const skillPath = path.join(pluginSkillsDir, skillDir);
        if (!fs.statSync(skillPath).isDirectory()) continue;

        const repoRelativePath = `.github/plugins/${pluginName}/skills/${skillDir}`;

        // Use symlink info from skills/ for category if available
        const symlinkInfo = findSymlinkInfo(skillDir, skillsSymlinkDir);
        const category = symlinkInfo?.category || "general";

        const skill = extractSkillFromDir(skillDir, skillPath, repoRelativePath, lang, category);
        if (skill) {
          skills.push(skill);
          seen.add(skillDir);
        }
      }
    }
  }

  // 2. Scan core skills still in .github/skills/ (real directories, not symlinks)
  if (fs.existsSync(skillsSourceDir)) {
    for (const skillDir of fs.readdirSync(skillsSourceDir)) {
      if (seen.has(skillDir)) continue;

      const skillPath = path.join(skillsSourceDir, skillDir);
      if (!fs.statSync(skillPath).isDirectory()) continue;

      const repoRelativePath = `.github/skills/${skillDir}`;
      const lang = inferLangFromName(skillDir);

      const symlinkInfo = findSymlinkInfo(skillDir, skillsSymlinkDir);
      const category = symlinkInfo?.category || "general";

      const skill = extractSkillFromDir(skillDir, skillPath, repoRelativePath, lang, category);
      if (skill) {
        skills.push(skill);
        seen.add(skillDir);
      }
    }
  }

  return skills.sort((a, b) => a.name.localeCompare(b.name));
}

function main() {
  const skills = extractSkills();
  const outputPath = path.resolve(
    import.meta.dirname,
    "../src/data/skills.json"
  );

  fs.writeFileSync(outputPath, JSON.stringify(skills, null, 2));
  console.log(`Extracted ${skills.length} skills to ${outputPath}`);

  const langCounts: Record<string, number> = {};
  for (const skill of skills) {
    langCounts[skill.lang] = (langCounts[skill.lang] || 0) + 1;
  }
  console.log("Language distribution:", langCounts);
}

main();
