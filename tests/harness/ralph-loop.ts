/**
 * Ralph Loop Controller
 *
 * Iterative code generation and improvement system that re-generates code
 * until quality thresholds are met or max iterations reached.
 *
 * This implementation is inspired by the Sensei iterative quality improvement
 * patterns developed by Shayne Boyer (@spboyer) for the GitHub Copilot for Azure
 * extension. The core insight: LLMs improve dramatically when given structured
 * feedback about what went wrong and specific guidance on how to fix it.
 *
 * @see https://github.com/microsoft/GitHub-Copilot-for-Azure/tree/main/.github/skills/sensei
 * @author Shayne Boyer <shayne.boyer@microsoft.com> - Original Sensei technique
 *
 * Flow:
 * 1. Generate code for a given skill/scenario
 * 2. Evaluate against acceptance criteria (score 0-100)
 * 3. Analyze failures and build LLM-actionable feedback
 * 4. Re-generate with feedback until quality threshold is met
 * 5. Report on quality improvements across iterations
 */

import type {
  AcceptanceCriteria,
  CopilotClient,
  EvaluationResult,
  Finding,
} from "./types.js";
import { CodeEvaluator } from "./evaluator.js";
import { createFeedbackBuilder, type FeedbackBuilder } from "./feedback-builder.js";

// =============================================================================
// Types
// =============================================================================

/**
 * Configuration for the Ralph Loop.
 */
export interface RalphLoopConfig {
  /** Maximum number of iterations before stopping (default: 5) */
  maxIterations: number;
  /** Score threshold to consider quality met (0-100, default: 80) */
  qualityThreshold: number;
  /** Minimum improvement required between iterations (default: 5) */
  improvementThreshold: number;
  /** Stop immediately when score reaches 100 (default: true) */
  earlyStopOnPerfect: boolean;
  /** Include feedback in re-generation prompts (default: true) */
  includeFeedback: boolean;
}

/**
 * Default Ralph Loop configuration.
 */
export const DEFAULT_RALPH_CONFIG: RalphLoopConfig = {
  maxIterations: 5,
  qualityThreshold: 80,
  improvementThreshold: 5,
  earlyStopOnPerfect: true,
  includeFeedback: true,
};

/**
 * Result of a single iteration.
 */
export interface IterationResult {
  /** Iteration number (1-indexed) */
  iteration: number;
  /** Score from evaluation (0-100) */
  score: number;
  /** Findings from evaluation */
  findings: Finding[];
  /** Generated code */
  generatedCode: string;
  /** Feedback provided for next iteration (empty on last iteration) */
  feedbackProvided: string;
  /** Duration of this iteration in milliseconds */
  durationMs: number;
}

/**
 * Stop reason for the loop.
 */
export type StopReason =
  | "quality_threshold_met"
  | "perfect_score"
  | "max_iterations_reached"
  | "no_improvement"
  | "score_regression";

/**
 * Final result of the Ralph Loop.
 */
export interface RalphLoopResult {
  /** Final score achieved */
  finalScore: number;
  /** All iteration results */
  iterations: IterationResult[];
  /** Improvement from first to last iteration */
  improvement: number;
  /** Whether the loop converged to quality threshold */
  converged: boolean;
  /** Which iteration had the best score (1-indexed) */
  bestIteration: number;
  /** Why the loop stopped */
  stopReason: StopReason;
  /** Total duration in milliseconds */
  totalDurationMs: number;
}

// =============================================================================
// Ralph Loop Controller
// =============================================================================

/**
 * Controls the iterative code generation loop.
 *
 * Usage:
 * ```typescript
 * const controller = new RalphLoopController(
 *   criteria,
 *   evaluator,
 *   copilotClient,
 *   { maxIterations: 5, qualityThreshold: 85 }
 * );
 * const result = await controller.run(prompt, "basic_usage");
 * console.log(`Final score: ${result.finalScore}, Converged: ${result.converged}`);
 * ```
 */
export class RalphLoopController {
  private readonly criteria: AcceptanceCriteria;
  private readonly evaluator: CodeEvaluator;
  private readonly client: CopilotClient;
  private readonly config: RalphLoopConfig;
  private readonly feedbackBuilder: FeedbackBuilder;

  constructor(
    criteria: AcceptanceCriteria,
    evaluator: CodeEvaluator,
    client: CopilotClient,
    config?: Partial<RalphLoopConfig>
  ) {
    this.criteria = criteria;
    this.evaluator = evaluator;
    this.client = client;
    this.config = { ...DEFAULT_RALPH_CONFIG, ...config };
    this.feedbackBuilder = createFeedbackBuilder();
  }

  /**
   * Run the Ralph Loop for a given prompt.
   *
   * @param prompt - The original prompt to generate code for
   * @param scenarioName - Name of the scenario (for mock responses)
   * @returns Final result with all iterations
   */
  async run(prompt: string, scenarioName: string): Promise<RalphLoopResult> {
    const startTime = Date.now();
    const iterations: IterationResult[] = [];
    let currentPrompt = prompt;
    let bestScore = 0;
    let bestIteration = 1;

    for (let i = 1; i <= this.config.maxIterations; i++) {
      const iterationStart = Date.now();

      // Generate code
      const generationResult = await this.client.generate(
        currentPrompt,
        this.criteria.skillName,
        undefined,
        scenarioName
      );

      // Evaluate the generated code
      const evalResult = this.evaluator.evaluate(
        generationResult.code,
        scenarioName
      );

      // Build feedback for next iteration
      const feedback = this.buildFeedback(evalResult);

      // Track best score
      if (evalResult.score > bestScore) {
        bestScore = evalResult.score;
        bestIteration = i;
      }

      // Create iteration result
      const iterationResult: IterationResult = {
        iteration: i,
        score: evalResult.score,
        findings: evalResult.findings,
        generatedCode: generationResult.code,
        feedbackProvided: feedback,
        durationMs: Date.now() - iterationStart,
      };
      iterations.push(iterationResult);

      // Check if we should stop
      const [shouldStop, stopReason] = this.shouldStop(iterations);
      if (shouldStop) {
        return this.buildResult(iterations, bestIteration, stopReason, startTime);
      }

      // Prepare prompt for next iteration with feedback
      if (this.config.includeFeedback && feedback) {
        currentPrompt = this.buildPromptWithFeedback(prompt, feedback, evalResult);
      }
    }

    // Max iterations reached
    return this.buildResult(
      iterations,
      bestIteration,
      "max_iterations_reached",
      startTime
    );
  }

  /**
   * Determine if the loop should stop and why.
   */
  private shouldStop(iterations: IterationResult[]): [boolean, StopReason] {
    if (iterations.length === 0) {
      return [false, "max_iterations_reached"];
    }

    const latest = iterations[iterations.length - 1]!;
    const latestScore = latest.score;

    // Check for perfect score
    if (this.config.earlyStopOnPerfect && latestScore >= 100) {
      return [true, "perfect_score"];
    }

    // Check for quality threshold met
    if (latestScore >= this.config.qualityThreshold) {
      return [true, "quality_threshold_met"];
    }

    // Check for improvement plateau or regression (need at least 2 iterations)
    if (iterations.length >= 2) {
      const previous = iterations[iterations.length - 2]!;
      const improvement = latestScore - previous.score;

      // Score went down
      if (improvement < 0) {
        return [true, "score_regression"];
      }

      // No meaningful improvement
      if (improvement < this.config.improvementThreshold) {
        return [true, "no_improvement"];
      }
    }

    return [false, "max_iterations_reached"];
  }

  /**
   * Build actionable feedback from evaluation findings.
   *
   * Delegates to FeedbackBuilder for consistent, LLM-optimized feedback formatting.
   */
  private buildFeedback(evalResult: EvaluationResult): string {
    return this.feedbackBuilder.buildFeedback(evalResult, this.criteria);
  }

  /**
   * Build a prompt that includes feedback from previous iteration.
   */
  private buildPromptWithFeedback(
    originalPrompt: string,
    feedback: string,
    evalResult: EvaluationResult
  ): string {
    return `${originalPrompt}

---

## Feedback from Previous Attempt

Your previous attempt scored ${evalResult.score}/100. Please address the following issues:

${feedback}

Generate improved code that fixes these issues while maintaining the original requirements.
`;
  }

  /**
   * Build the final result object.
   */
  private buildResult(
    iterations: IterationResult[],
    bestIteration: number,
    stopReason: StopReason,
    startTime: number
  ): RalphLoopResult {
    const firstScore = iterations[0]?.score ?? 0;
    const lastScore = iterations[iterations.length - 1]?.score ?? 0;

    return {
      finalScore: lastScore,
      iterations,
      improvement: lastScore - firstScore,
      converged:
        stopReason === "quality_threshold_met" || stopReason === "perfect_score",
      bestIteration,
      stopReason,
      totalDurationMs: Date.now() - startTime,
    };
  }
}

// =============================================================================
// Factory Functions
// =============================================================================

/**
 * Create a Ralph Loop configuration with overrides.
 */
export function createRalphConfig(
  partial: Partial<RalphLoopConfig> = {}
): RalphLoopConfig {
  return { ...DEFAULT_RALPH_CONFIG, ...partial };
}

/**
 * Create a Ralph Loop controller with default evaluator.
 */
export function createRalphLoopController(
  criteria: AcceptanceCriteria,
  client: CopilotClient,
  config?: Partial<RalphLoopConfig>
): RalphLoopController {
  const evaluator = new CodeEvaluator(criteria);
  return new RalphLoopController(criteria, evaluator, client, config);
}
