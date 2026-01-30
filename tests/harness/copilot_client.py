"""
Copilot Client

Wraps the GitHub Copilot SDK for generating code with skill context.
Manages sessions, sends prompts, and captures generated code.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .criteria_loader import AcceptanceCriteria

# Try to import Copilot SDK (optional dependency)
try:
    from github_copilot_sdk import CopilotClient, Session
    COPILOT_SDK_AVAILABLE = True
except ImportError:
    COPILOT_SDK_AVAILABLE = False
    CopilotClient = None
    Session = None


@dataclass
class GenerationResult:
    """Result of code generation."""
    
    code: str
    prompt: str
    skill_name: str
    model: str = ""
    tokens_used: int = 0
    duration_ms: float = 0.0
    raw_response: str = ""


@dataclass
class GenerationConfig:
    """Configuration for code generation."""
    
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3
    include_skill_context: bool = True
    skill_paths: list[Path] = field(default_factory=list)


class MockCopilotClient:
    """
    Mock client for testing without Copilot SDK.
    Returns predefined responses for test scenarios.
    """
    
    def __init__(self):
        self._mock_responses: dict[str, str] = {}
    
    def add_mock_response(self, prompt_contains: str, response: str) -> None:
        """Add a mock response for prompts containing specific text."""
        self._mock_responses[prompt_contains.lower()] = response
    
    def generate(
        self, 
        prompt: str, 
        skill_context: str = "",
        config: GenerationConfig | None = None
    ) -> GenerationResult:
        """Generate a mock response."""
        prompt_lower = prompt.lower()
        
        for key, response in self._mock_responses.items():
            if key in prompt_lower:
                return GenerationResult(
                    code=response,
                    prompt=prompt,
                    skill_name="mock",
                    model="mock",
                )
        
        # Default mock response
        return GenerationResult(
            code="# No mock response configured for this prompt\npass",
            prompt=prompt,
            skill_name="mock",
            model="mock",
        )


class SkillCopilotClient:
    """
    Client for generating code using GitHub Copilot SDK with skill context.
    
    Features:
    - Loads skill content as context
    - Manages conversation sessions
    - Extracts code from responses
    - Falls back to mock client if SDK unavailable
    """
    
    SKILLS_DIR = Path(".github/skills")
    
    def __init__(
        self, 
        base_path: Path | None = None,
        use_mock: bool = False
    ):
        self.base_path = base_path or Path.cwd()
        self.skills_dir = self.base_path / self.SKILLS_DIR
        self._use_mock = use_mock or not COPILOT_SDK_AVAILABLE
        
        if self._use_mock:
            self._client = MockCopilotClient()
        else:
            self._client = self._create_copilot_client()
        
        self._skill_cache: dict[str, str] = {}
    
    def _create_copilot_client(self) -> CopilotClient:
        """Create and configure the Copilot SDK client."""
        if not COPILOT_SDK_AVAILABLE:
            raise RuntimeError(
                "Copilot SDK not available. Install with: "
                "pip install github-copilot-sdk"
            )
        
        # Initialize Copilot client
        # This assumes copilot CLI is installed and authenticated
        return CopilotClient()
    
    def load_skill_context(self, skill_name: str) -> str:
        """Load skill content as context for code generation."""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]
        
        skill_dir = self.skills_dir / skill_name
        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill not found: {skill_name}")
        
        context_parts = []
        
        # Load main SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            context_parts.append(f"# Skill: {skill_name}\n\n")
            context_parts.append(skill_md.read_text(encoding="utf-8"))
        
        # Load reference files
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in refs_dir.glob("*.md"):
                if ref_file.name != "acceptance-criteria.md":  # Skip test criteria
                    context_parts.append(f"\n\n# Reference: {ref_file.stem}\n\n")
                    context_parts.append(ref_file.read_text(encoding="utf-8"))
        
        context = "\n".join(context_parts)
        self._skill_cache[skill_name] = context
        return context
    
    def generate(
        self,
        prompt: str,
        skill_name: str,
        config: GenerationConfig | None = None
    ) -> GenerationResult:
        """Generate code using Copilot with skill context."""
        config = config or GenerationConfig()
        
        # Build full prompt with skill context
        if config.include_skill_context:
            skill_context = self.load_skill_context(skill_name)
            full_prompt = self._build_prompt(prompt, skill_context)
        else:
            full_prompt = prompt
            skill_context = ""
        
        if self._use_mock:
            return self._client.generate(prompt, skill_context, config)
        
        # Use real Copilot SDK
        return self._generate_with_copilot(full_prompt, skill_name, config)
    
    def _build_prompt(self, user_prompt: str, skill_context: str) -> str:
        """Build the full prompt with skill context."""
        return f"""You are an expert Python developer. Use the following skill documentation as reference for correct SDK usage patterns.

<skill-context>
{skill_context}
</skill-context>

<task>
{user_prompt}
</task>

Generate only Python code. Follow the patterns from the skill documentation exactly.
"""
    
    def _generate_with_copilot(
        self,
        prompt: str,
        skill_name: str,
        config: GenerationConfig
    ) -> GenerationResult:
        """Generate code using the actual Copilot SDK."""
        import time
        
        start_time = time.time()
        
        # Create session and send message
        session = self._client.create_session()
        
        response = session.send_message(
            prompt,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Extract code from response
        code = self._extract_code(response.content)
        
        return GenerationResult(
            code=code,
            prompt=prompt,
            skill_name=skill_name,
            model=config.model,
            duration_ms=duration_ms,
            raw_response=response.content,
        )
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from a response."""
        import re
        
        # Look for code blocks
        code_blocks = re.findall(
            r'```(?:python)?\n(.*?)```',
            response,
            re.DOTALL
        )
        
        if code_blocks:
            return "\n\n".join(block.strip() for block in code_blocks)
        
        # If no code blocks, try to find Python-like content
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Heuristic: lines starting with import, def, class, or indented
            if (line.startswith('import ') or 
                line.startswith('from ') or
                line.startswith('def ') or
                line.startswith('class ') or
                line.startswith('    ') or
                line.startswith('\t')):
                in_code = True
                code_lines.append(line)
            elif in_code and line.strip() == '':
                code_lines.append(line)
            elif in_code and not line.startswith('#') and line.strip():
                # Non-code line, might be end of code
                if not line[0].isalpha():
                    code_lines.append(line)
        
        return '\n'.join(code_lines).strip() or response
    
    def add_mock_response(self, prompt_contains: str, response: str) -> None:
        """Add a mock response (only works in mock mode)."""
        if isinstance(self._client, MockCopilotClient):
            self._client.add_mock_response(prompt_contains, response)


def check_copilot_available() -> bool:
    """Check if Copilot SDK and CLI are available."""
    if not COPILOT_SDK_AVAILABLE:
        return False
    
    # Check if copilot CLI is installed
    try:
        result = subprocess.run(
            ["copilot", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# CLI for testing
if __name__ == "__main__":
    print(f"Copilot SDK available: {COPILOT_SDK_AVAILABLE}")
    print(f"Copilot CLI available: {check_copilot_available()}")
    
    if len(sys.argv) > 1:
        skill_name = sys.argv[1]
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Create a basic agent"
        
        client = SkillCopilotClient(use_mock=not check_copilot_available())
        
        try:
            result = client.generate(prompt, skill_name)
            print(f"\nGenerated code for {skill_name}:")
            print("-" * 50)
            print(result.code)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
