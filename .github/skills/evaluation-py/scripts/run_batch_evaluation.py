#!/usr/bin/env python3
"""
Batch Evaluation CLI Tool

Run batch evaluations on test datasets using Azure AI Evaluation SDK.
Supports quality, safety, and custom evaluators with Foundry integration.

Usage:
    python run_batch_evaluation.py --data test_data.jsonl --evaluators groundedness relevance
    python run_batch_evaluation.py --data test_data.jsonl --evaluators qa --output results.json
    python run_batch_evaluation.py --data test_data.jsonl --safety --log-to-foundry

Environment Variables:
    AZURE_OPENAI_ENDPOINT      - Azure OpenAI endpoint URL
    AZURE_OPENAI_API_KEY       - Azure OpenAI API key (optional if using DefaultAzureCredential)
    AZURE_OPENAI_DEPLOYMENT    - Model deployment name (default: gpt-4o-mini)
    AIPROJECT_CONNECTION_STRING - Foundry project connection string (for safety/logging)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential


# Available evaluators by category
QUALITY_EVALUATORS = [
    "groundedness",
    "relevance",
    "coherence",
    "fluency",
    "similarity",
    "retrieval",
]
NLP_EVALUATORS = ["f1", "rouge", "bleu", "gleu", "meteor"]
SAFETY_EVALUATORS = ["violence", "sexual", "self_harm", "hate_unfairness"]
COMPOSITE_EVALUATORS = ["qa", "content_safety"]


def get_model_config() -> dict[str, Any]:
    """Build model configuration from environment variables."""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable required")

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

    config = {
        "azure_endpoint": endpoint,
        "azure_deployment": deployment,
        "api_version": "2024-06-01",
    }

    if api_key:
        config["api_key"] = api_key
    else:
        config["credential"] = DefaultAzureCredential()

    return config


def get_project_scope() -> dict[str, str] | None:
    """Get Foundry project scope for safety evaluators."""
    conn_str = os.environ.get("AIPROJECT_CONNECTION_STRING")
    if not conn_str:
        return None

    from azure.ai.projects import AIProjectClient

    project = AIProjectClient.from_connection_string(
        conn_str=conn_str, credential=DefaultAzureCredential()
    )
    return project.scope


def build_evaluators(
    evaluator_names: list[str],
    model_config: dict[str, Any],
    project_scope: dict[str, str] | None,
) -> dict[str, Any]:
    """Build evaluator instances from names."""
    from azure.ai.evaluation import (
        GroundednessEvaluator,
        RelevanceEvaluator,
        CoherenceEvaluator,
        FluencyEvaluator,
        SimilarityEvaluator,
        RetrievalEvaluator,
        F1ScoreEvaluator,
        RougeScoreEvaluator,
        BleuScoreEvaluator,
        GleuScoreEvaluator,
        MeteorScoreEvaluator,
        QAEvaluator,
    )

    evaluators = {}

    # Quality evaluators (AI-assisted)
    quality_map = {
        "groundedness": GroundednessEvaluator,
        "relevance": RelevanceEvaluator,
        "coherence": CoherenceEvaluator,
        "fluency": FluencyEvaluator,
        "similarity": SimilarityEvaluator,
        "retrieval": RetrievalEvaluator,
    }

    # NLP evaluators
    nlp_map = {
        "f1": F1ScoreEvaluator,
        "rouge": RougeScoreEvaluator,
        "bleu": BleuScoreEvaluator,
        "gleu": GleuScoreEvaluator,
        "meteor": MeteorScoreEvaluator,
    }

    for name in evaluator_names:
        if name in quality_map:
            evaluators[name] = quality_map[name](model_config)
        elif name in nlp_map:
            evaluators[name] = nlp_map[name]()
        elif name == "qa":
            evaluators[name] = QAEvaluator(model_config)
        elif name in SAFETY_EVALUATORS or name == "content_safety":
            if not project_scope:
                print(
                    f"Warning: Skipping {name} - requires AIPROJECT_CONNECTION_STRING"
                )
                continue
            evaluators[name] = build_safety_evaluator(name, project_scope)
        else:
            print(f"Warning: Unknown evaluator '{name}', skipping")

    return evaluators


def build_safety_evaluator(name: str, project_scope: dict[str, str]) -> Any:
    """Build safety evaluator instance."""
    from azure.ai.evaluation import (
        ViolenceEvaluator,
        SexualEvaluator,
        SelfHarmEvaluator,
        HateUnfairnessEvaluator,
        ContentSafetyEvaluator,
    )

    safety_map = {
        "violence": ViolenceEvaluator,
        "sexual": SexualEvaluator,
        "self_harm": SelfHarmEvaluator,
        "hate_unfairness": HateUnfairnessEvaluator,
        "content_safety": ContentSafetyEvaluator,
    }

    return safety_map[name](azure_ai_project=project_scope)


def run_evaluation(
    data_path: str,
    evaluators: dict[str, Any],
    column_mapping: dict[str, str],
    project_scope: dict[str, str] | None = None,
    log_to_foundry: bool = False,
) -> dict[str, Any]:
    """Run batch evaluation."""
    from azure.ai.evaluation import evaluate

    eval_config = {"default": {"column_mapping": column_mapping}}

    kwargs = {
        "data": data_path,
        "evaluators": evaluators,
        "evaluator_config": eval_config,
    }

    if log_to_foundry and project_scope:
        kwargs["azure_ai_project"] = project_scope

    return evaluate(**kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="Run batch evaluation on test datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--data", "-d", required=True, help="Path to JSONL data file")
    parser.add_argument(
        "--evaluators",
        "-e",
        nargs="+",
        default=["groundedness", "relevance", "coherence"],
        help=f"Evaluators to run. Quality: {QUALITY_EVALUATORS}, "
        f"NLP: {NLP_EVALUATORS}, Composite: {COMPOSITE_EVALUATORS}",
    )
    parser.add_argument(
        "--safety", action="store_true", help="Include all safety evaluators"
    )
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    parser.add_argument(
        "--log-to-foundry", action="store_true", help="Log results to Foundry project"
    )
    parser.add_argument(
        "--query-column",
        default="query",
        help="Column name for query in data (default: query)",
    )
    parser.add_argument(
        "--context-column",
        default="context",
        help="Column name for context in data (default: context)",
    )
    parser.add_argument(
        "--response-column",
        default="response",
        help="Column name for response in data (default: response)",
    )
    parser.add_argument(
        "--ground-truth-column",
        default="ground_truth",
        help="Column name for ground truth in data (default: ground_truth)",
    )

    args = parser.parse_args()

    # Validate data file
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    # Build column mapping
    column_mapping = {
        "query": f"${{data.{args.query_column}}}",
        "context": f"${{data.{args.context_column}}}",
        "response": f"${{data.{args.response_column}}}",
        "ground_truth": f"${{data.{args.ground_truth_column}}}",
    }

    # Get configurations
    try:
        model_config = get_model_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    project_scope = get_project_scope()

    # Build evaluator list
    evaluator_names = list(args.evaluators)
    if args.safety:
        evaluator_names.extend(SAFETY_EVALUATORS)

    # Build evaluators
    evaluators = build_evaluators(evaluator_names, model_config, project_scope)

    if not evaluators:
        print("Error: No valid evaluators configured")
        sys.exit(1)

    print(f"Running evaluation with: {list(evaluators.keys())}")
    print(f"Data file: {args.data}")

    # Run evaluation
    try:
        result = run_evaluation(
            data_path=str(data_path),
            evaluators=evaluators,
            column_mapping=column_mapping,
            project_scope=project_scope,
            log_to_foundry=args.log_to_foundry,
        )
    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)

    # Output results
    metrics = result.get("metrics", {})

    print("\n=== Evaluation Results ===")
    for metric, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")
        else:
            print(f"  {metric}: {value}")

    if "studio_url" in result:
        print(f"\nView in Foundry: {result['studio_url']}")

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(
                {
                    "metrics": metrics,
                    "studio_url": result.get("studio_url"),
                    "rows": result.get("rows", []),
                },
                f,
                indent=2,
                default=str,
            )
        print(f"\nResults saved to: {args.output}")

    print("\nEvaluation complete!")


if __name__ == "__main__":
    main()
