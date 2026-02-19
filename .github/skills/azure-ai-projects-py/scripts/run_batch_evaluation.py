#!/usr/bin/env python3
"""
Batch Evaluation CLI Tool

Run batch evaluations on test datasets using Azure AI Projects SDK.
Supports quality, safety, agent evaluators, and OpenAI graders.

Usage:
    python run_batch_evaluation.py --data test_data.jsonl --evaluators coherence relevance
    python run_batch_evaluation.py --data test_data.jsonl --evaluators coherence --output results.json
    python run_batch_evaluation.py --data test_data.jsonl --safety
    python run_batch_evaluation.py --data test_data.jsonl --agent --evaluators intent_resolution task_adherence

Environment Variables:
    AZURE_AI_PROJECT_ENDPOINT     - Azure AI project endpoint (required)
    AZURE_AI_MODEL_DEPLOYMENT_NAME - Model deployment name (default: gpt-4o-mini)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom


# Built-in evaluators by category
QUALITY_EVALUATORS = [
    "coherence",
    "relevance",
    "fluency",
    "groundedness",
]
SAFETY_EVALUATORS = [
    "violence",
    "sexual",
    "self_harm",
    "hate_unfairness",
]
AGENT_EVALUATORS = [
    "intent_resolution",
    "response_completeness",
    "task_adherence",
    "tool_call_accuracy",
]
NLP_EVALUATORS = ["f1", "rouge", "bleu", "gleu", "meteor"]


def load_jsonl(path: str) -> list[dict]:
    """Load JSONL file into list of dicts."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def build_data_source(
    data: list[dict],
    is_agent: bool = False,
) -> CreateEvalJSONLRunDataSourceParam:
    """Build data source from loaded data."""
    content = []
    for item in data:
        if is_agent:
            # Agent data: extract sample fields from item
            sample = {
                "output_text": item.pop("output_text", item.get("response", "")),
            }
            if "output_items" in item:
                sample["output_items"] = item.pop("output_items")
            content.append(SourceFileContentContent(item=item, sample=sample))
        else:
            content.append(SourceFileContentContent(item=item, sample={}))

    return CreateEvalJSONLRunDataSourceParam(
        type="jsonl",
        source=SourceFileContent(type="file_content", content=content),
    )


def build_data_source_config(
    data: list[dict],
    is_agent: bool = False,
) -> DataSourceConfigCustom:
    """Build data source config based on data schema."""
    # Infer schema from first item
    if not data:
        raise ValueError("Data is empty")

    first_item = data[0]
    properties = {}
    required = []

    for key in first_item:
        if key not in ["output_text", "output_items"]:  # Agent fields go in sample
            properties[key] = {"type": "string"}
            required.append(key)

    return DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": properties,
            "required": required,
        },
        include_sample_schema=is_agent,
    )


def build_testing_criteria(
    evaluator_names: list[str],
    deployment_name: str,
    is_agent: bool = False,
) -> list[dict]:
    """Build testing criteria for the specified evaluators."""
    criteria = []

    for name in evaluator_names:
        # Determine data mapping based on evaluator type
        if name in QUALITY_EVALUATORS:
            if name == "groundedness":
                data_mapping = {
                    "query": "{{item.query}}",
                    "context": "{{item.context}}",
                    "response": "{{item.response}}",
                }
            else:
                data_mapping = {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                }
            needs_model = True

        elif name in SAFETY_EVALUATORS:
            data_mapping = {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            }
            needs_model = False  # Safety evaluators may not need deployment

        elif name in AGENT_EVALUATORS:
            if is_agent:
                if name == "tool_call_accuracy":
                    data_mapping = {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_items}}",
                    }
                else:
                    data_mapping = {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    }
            else:
                data_mapping = {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                }
            needs_model = True

        elif name in NLP_EVALUATORS:
            data_mapping = {
                "response": "{{item.response}}",
                "ground_truth": "{{item.ground_truth}}",
            }
            needs_model = False

        else:
            print(f"Warning: Unknown evaluator '{name}', skipping")
            continue

        criterion = {
            "type": "azure_ai_evaluator",
            "name": name,
            "evaluator_name": f"builtin.{name}",
            "data_mapping": data_mapping,
        }

        if needs_model:
            criterion["initialization_parameters"] = {"deployment_name": deployment_name}

        criteria.append(criterion)

    return criteria


def run_evaluation(
    endpoint: str,
    data_path: str,
    evaluator_names: list[str],
    deployment_name: str,
    is_agent: bool = False,
) -> dict[str, Any]:
    """Run batch evaluation using Azure AI Projects SDK."""
    # Load data
    data = load_jsonl(data_path)
    print(f"Loaded {len(data)} items from {data_path}")

    # Build data source and config
    data_source = build_data_source(data, is_agent=is_agent)
    data_source_config = build_data_source_config(data, is_agent=is_agent)

    # Build testing criteria
    testing_criteria = build_testing_criteria(
        evaluator_names,
        deployment_name,
        is_agent=is_agent,
    )

    if not testing_criteria:
        raise ValueError("No valid testing criteria configured")

    print(f"Configured {len(testing_criteria)} evaluators")

    # Create client and run evaluation
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        openai_client = project_client.get_openai_client()

        # Create evaluation definition
        eval_object = openai_client.evals.create(
            name=f"Batch Evaluation - {Path(data_path).stem}",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        print(f"Created evaluation: {eval_object.id}")

        # Create and run evaluation
        run = openai_client.evals.runs.create(
            eval_id=eval_object.id,
            name="CLI Run",
            data_source=data_source,
        )
        print(f"Started run: {run.id}")

        # Poll for completion
        while run.status not in ["completed", "failed", "cancelled"]:
            print(f"Status: {run.status}...")
            time.sleep(5)
            run = openai_client.evals.runs.retrieve(
                eval_id=eval_object.id,
                run_id=run.id,
            )

        if run.status != "completed":
            raise RuntimeError(f"Evaluation run {run.status}: {getattr(run, 'error', 'Unknown error')}")

        print(f"Run completed: {run.status}")

        # Retrieve results
        output_items = list(
            openai_client.evals.runs.output_items.list(
                eval_id=eval_object.id,
                run_id=run.id,
            )
        )

        # Aggregate metrics
        metrics: dict[str, list[float]] = {}
        rows = []

        for output_item in output_items:
            row_results = {}
            for result in output_item.results:
                if result.score is not None:
                    if result.name not in metrics:
                        metrics[result.name] = []
                    metrics[result.name].append(result.score)
                    row_results[result.name] = result.score
            rows.append(row_results)

        # Calculate averages
        avg_metrics = {}
        for name, scores in metrics.items():
            avg_metrics[name] = sum(scores) / len(scores) if scores else 0.0

        return {
            "eval_id": eval_object.id,
            "run_id": run.id,
            "status": run.status,
            "metrics": avg_metrics,
            "rows": rows,
            "total_items": len(output_items),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Run batch evaluation on test datasets using Azure AI Projects SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--data", "-d", required=True, help="Path to JSONL data file")
    parser.add_argument(
        "--evaluators",
        "-e",
        nargs="+",
        default=["coherence", "relevance"],
        help=f"Evaluators to run. Quality: {QUALITY_EVALUATORS}, "
        f"Safety: {SAFETY_EVALUATORS}, Agent: {AGENT_EVALUATORS}, NLP: {NLP_EVALUATORS}",
    )
    parser.add_argument(
        "--safety",
        action="store_true",
        help="Include all safety evaluators",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Include all agent evaluators (uses sample.output_text for response)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for results (JSON)",
    )
    parser.add_argument(
        "--deployment",
        default=None,
        help="Model deployment name (overrides AZURE_AI_MODEL_DEPLOYMENT_NAME)",
    )

    args = parser.parse_args()

    # Validate environment
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("Error: AZURE_AI_PROJECT_ENDPOINT environment variable required")
        sys.exit(1)

    deployment = args.deployment or os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

    # Validate data file
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    # Build evaluator list
    evaluator_names = list(args.evaluators)
    if args.safety:
        evaluator_names.extend(SAFETY_EVALUATORS)
    if args.agent:
        evaluator_names.extend(AGENT_EVALUATORS)

    # Remove duplicates while preserving order
    seen = set()
    unique_evaluators = []
    for e in evaluator_names:
        if e not in seen:
            seen.add(e)
            unique_evaluators.append(e)
    evaluator_names = unique_evaluators

    print(f"Running evaluation with: {evaluator_names}")
    print(f"Data file: {args.data}")
    print(f"Deployment: {deployment}")
    print(f"Agent mode: {args.agent}")

    # Run evaluation
    try:
        result = run_evaluation(
            endpoint=endpoint,
            data_path=str(data_path),
            evaluator_names=evaluator_names,
            deployment_name=deployment,
            is_agent=args.agent,
        )
    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)

    # Output results
    print("\n=== Evaluation Results ===")
    print(f"Eval ID: {result['eval_id']}")
    print(f"Run ID: {result['run_id']}")
    print(f"Status: {result['status']}")
    print(f"Total Items: {result['total_items']}")
    print("\nMetrics:")
    for metric, value in sorted(result["metrics"].items()):
        print(f"  {metric}: {value:.4f}")

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {args.output}")

    print("\nEvaluation complete!")


if __name__ == "__main__":
    main()
