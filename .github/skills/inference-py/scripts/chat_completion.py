#!/usr/bin/env python3
"""
CLI tool for Azure AI Inference chat completions.

Usage:
    # Basic chat
    python chat_completion.py --prompt "What is Azure AI?"

    # With system prompt
    python chat_completion.py --prompt "Explain quantum computing" --system "You are a physics teacher"

    # Streaming output
    python chat_completion.py --prompt "Write a poem" --stream

    # Interactive mode
    python chat_completion.py --interactive

    # With specific model
    python chat_completion.py --prompt "Hello" --model gpt-4o

    # Get embeddings
    python chat_completion.py --embed "Your text here"

Environment Variables:
    AZURE_INFERENCE_ENDPOINT: Inference endpoint URL
    AZURE_INFERENCE_CREDENTIAL: API key (optional if using Entra ID)
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Optional

from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


def get_client(endpoint: str, key: Optional[str] = None) -> ChatCompletionsClient:
    """Create chat completions client."""
    if key:
        credential = AzureKeyCredential(key)
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()

    return ChatCompletionsClient(endpoint=endpoint, credential=credential)


def get_embeddings_client(endpoint: str, key: Optional[str] = None) -> EmbeddingsClient:
    """Create embeddings client."""
    if key:
        credential = AzureKeyCredential(key)
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()

    return EmbeddingsClient(endpoint=endpoint, credential=credential)


def chat_completion(
    client: ChatCompletionsClient,
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
) -> str:
    """Send a chat completion request."""
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(UserMessage(content=prompt))

    kwargs = {"messages": messages, "temperature": temperature, "stream": stream}
    if model:
        kwargs["model"] = model
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    if stream:
        response = client.complete(**kwargs)
        chunks = []
        for update in response:
            if update.choices:
                content = update.choices[0].delta.content
                if content:
                    chunks.append(content)
                    print(content, end="", flush=True)
        print()
        return "".join(chunks)
    else:
        response = client.complete(**kwargs)
        content = response.choices[0].message.content
        print(content)
        return content


def get_embeddings(
    client: EmbeddingsClient, text: str, model: Optional[str] = None
) -> list[float]:
    """Get embeddings for text."""
    kwargs = {"input": [text]}
    if model:
        kwargs["model"] = model

    response = client.embed(**kwargs)
    embedding = response.data[0].embedding

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")

    return embedding


def interactive_mode(
    client: ChatCompletionsClient,
    system: Optional[str] = None,
    model: Optional[str] = None,
    stream: bool = True,
):
    """Run interactive chat session."""
    print("Interactive Chat Mode (type 'exit' or 'quit' to end)")
    print("-" * 50)

    messages = []
    if system:
        messages.append(SystemMessage(content=system))
        print(f"System: {system}")
        print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            messages.append(UserMessage(content=user_input))

            kwargs = {"messages": messages, "stream": stream}
            if model:
                kwargs["model"] = model

            print("\nAssistant: ", end="")

            if stream:
                response = client.complete(**kwargs)
                chunks = []
                for update in response:
                    if update.choices:
                        content = update.choices[0].delta.content
                        if content:
                            chunks.append(content)
                            print(content, end="", flush=True)
                print()
                full_response = "".join(chunks)
            else:
                response = client.complete(**kwargs)
                full_response = response.choices[0].message.content
                print(full_response)

            # Add assistant response to history
            from azure.ai.inference.models import AssistantMessage

            messages.append(AssistantMessage(content=full_response))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def model_info(client: ChatCompletionsClient):
    """Get and display model information."""
    try:
        info = client.get_model_info()
        print(f"Model Name: {info.model_name}")
        print(f"Provider: {info.model_provider_name}")
        print(f"Type: {info.model_type}")
    except Exception as e:
        print(f"Could not get model info: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Azure AI Inference CLI for chat completions and embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Connection options
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("AZURE_INFERENCE_ENDPOINT"),
        help="Inference endpoint URL (default: AZURE_INFERENCE_ENDPOINT env var)",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("AZURE_INFERENCE_CREDENTIAL"),
        help="API key (default: AZURE_INFERENCE_CREDENTIAL env var, or use Entra ID)",
    )

    # Chat options
    parser.add_argument("--prompt", "-p", help="User prompt for single completion")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--model", "-m", help="Model deployment name")
    parser.add_argument(
        "--temperature",
        "-t",
        type=float,
        default=0.7,
        help="Temperature (0.0-2.0, default: 0.7)",
    )
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens in response")
    parser.add_argument("--stream", action="store_true", help="Stream the response")

    # Modes
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive chat mode"
    )
    parser.add_argument("--embed", help="Get embeddings for text")
    parser.add_argument("--info", action="store_true", help="Show model information")

    args = parser.parse_args()

    # Validate endpoint
    if not args.endpoint:
        print(
            "Error: --endpoint or AZURE_INFERENCE_ENDPOINT environment variable required"
        )
        sys.exit(1)

    # Execute requested operation
    try:
        if args.embed:
            client = get_embeddings_client(args.endpoint, args.key)
            get_embeddings(client, args.embed, args.model)

        elif args.interactive:
            client = get_client(args.endpoint, args.key)
            interactive_mode(client, args.system, args.model, args.stream)

        elif args.info:
            client = get_client(args.endpoint, args.key)
            model_info(client)

        elif args.prompt:
            client = get_client(args.endpoint, args.key)
            chat_completion(
                client,
                args.prompt,
                args.system,
                args.model,
                args.temperature,
                args.max_tokens,
                args.stream,
            )

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
