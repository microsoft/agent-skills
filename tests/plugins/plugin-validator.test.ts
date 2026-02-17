/**
 * Plugin Validator Tests
 *
 * Generic validation suite for any Claude Code plugin in .github/plugins/.
 * Validates structure, frontmatter, required fields, and cross-references.
 */

import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, it, expect } from "vitest";
import {
  discoverPlugins,
  pluginPath,
  loadManifest,
  parseFrontmatter,
  discoverFiles,
  discoverSkillDirs,
  collectPluginFiles,
} from "./utils.js";

const BASE_PATH = resolve(import.meta.dirname, "../..");

const plugins = discoverPlugins(BASE_PATH);

describe("Plugin Validation", () => {
  it("should discover at least one plugin", () => {
    expect(plugins.length).toBeGreaterThan(0);
  });

  for (const name of plugins) {
    describe(`Plugin: ${name}`, () => {
      const dir = pluginPath(BASE_PATH, name);

      // =====================================================================
      // Manifest
      // =====================================================================

      describe("plugin.json manifest", () => {
        it("should have .claude-plugin/plugin.json", () => {
          expect(
            existsSync(join(dir, ".claude-plugin", "plugin.json"))
          ).toBe(true);
        });

        it("should be valid JSON with required fields", () => {
          const manifest = loadManifest(dir);
          expect(manifest.name).toBeTruthy();
          expect(typeof manifest.name).toBe("string");
          expect(manifest.description).toBeTruthy();
          expect(typeof manifest.description).toBe("string");
          expect(manifest.version).toBeTruthy();
          expect(manifest.version).toMatch(/^\d+\.\d+\.\d+/);
        });
      });

      // =====================================================================
      // Commands
      // =====================================================================

      const commandsDir = join(dir, "commands");
      const commandFiles = existsSync(commandsDir)
        ? discoverFiles(commandsDir, ".md")
        : [];

      if (commandFiles.length > 0) {
        describe("commands/", () => {
          for (const file of commandFiles) {
            describe(file, () => {
              const filePath = join(commandsDir, file);

              it("should have valid YAML frontmatter with description", () => {
                const { frontmatter } = parseFrontmatter(filePath);
                expect(frontmatter["description"]).toBeTruthy();
                expect(typeof frontmatter["description"]).toBe("string");
              });

              it("should have body content", () => {
                const { body } = parseFrontmatter(filePath);
                expect(body.trim().length).toBeGreaterThan(0);
              });
            });
          }
        });
      }

      // =====================================================================
      // Skills
      // =====================================================================

      const skillsDir = join(dir, "skills");
      const skillDirs = existsSync(skillsDir)
        ? discoverSkillDirs(skillsDir)
        : [];

      if (skillDirs.length > 0) {
        describe("skills/", () => {
          for (const skillName of skillDirs) {
            describe(skillName, () => {
              const skillPath = join(skillsDir, skillName, "SKILL.md");

              it("should have valid YAML frontmatter with name and description", () => {
                const { frontmatter } = parseFrontmatter(skillPath);
                expect(frontmatter["name"]).toBeTruthy();
                expect(typeof frontmatter["name"]).toBe("string");
                expect(frontmatter["description"]).toBeTruthy();
                expect(typeof frontmatter["description"]).toBe("string");
              });

              it("should have frontmatter name matching directory name", () => {
                const { frontmatter } = parseFrontmatter(skillPath);
                expect(frontmatter["name"]).toBe(skillName);
              });

              it("should have body content", () => {
                const { body } = parseFrontmatter(skillPath);
                expect(body.trim().length).toBeGreaterThan(0);
              });
            });
          }
        });
      }

      // =====================================================================
      // Agents
      // =====================================================================

      const agentsDir = join(dir, "agents");
      const agentFiles = existsSync(agentsDir)
        ? discoverFiles(agentsDir, ".md")
        : [];

      if (agentFiles.length > 0) {
        describe("agents/", () => {
          const validModels = ["sonnet", "opus", "haiku"];

          for (const file of agentFiles) {
            describe(file, () => {
              const filePath = join(agentsDir, file);

              it("should have valid YAML frontmatter with name and description", () => {
                const { frontmatter } = parseFrontmatter(filePath);
                expect(frontmatter["name"]).toBeTruthy();
                expect(typeof frontmatter["name"]).toBe("string");
                expect(frontmatter["description"]).toBeTruthy();
                expect(typeof frontmatter["description"]).toBe("string");
              });

              it("should have a valid model if specified", () => {
                const { frontmatter } = parseFrontmatter(filePath);
                if (frontmatter["model"] !== undefined) {
                  expect(validModels).toContain(frontmatter["model"]);
                }
              });

              it("should have body content", () => {
                const { body } = parseFrontmatter(filePath);
                expect(body.trim().length).toBeGreaterThan(0);
              });
            });
          }
        });
      }

      // =====================================================================
      // Cross-reference: README consistency
      // =====================================================================

      const readmePath = join(dir, "README.md");
      if (existsSync(readmePath)) {
        describe("README cross-references", () => {
          const files = collectPluginFiles(dir);

          // TODO: JasonYe to check for future needs and adjustments
          //it("should have commands on disk", () => {
          //  expect(files.commands.length).toBeGreaterThan(0);
          //});

          it("should have skills on disk", () => {
            expect(files.skills.length).toBeGreaterThan(0);
          });

          //it("should have agents on disk", () => {
          //  expect(files.agents.length).toBeGreaterThan(0);
          //});
        });
      }
    });
  }
});
