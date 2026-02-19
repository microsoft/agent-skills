#!/usr/bin/env python3
"""
Service Bus Administration CLI Tool

Create and manage Azure Service Bus queues, topics, and subscriptions.

Usage:
    python setup_servicebus.py queue create myqueue --max-delivery 10 --ttl 3600
    python setup_servicebus.py queue info myqueue
    python setup_servicebus.py topic create mytopic
    python setup_servicebus.py subscription create mytopic mysub --filter "priority='high'"
    python setup_servicebus.py dlq count myqueue

Environment Variables:
    SERVICEBUS_FULLY_QUALIFIED_NAMESPACE  - Service Bus namespace (e.g., myns.servicebus.windows.net)
    SERVICEBUS_CONNECTION_STRING          - Alternative: full connection string
"""

import argparse
import json
import os
import sys
from datetime import timedelta
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.servicebus.management import (
    QueueProperties,
    TopicProperties,
    SubscriptionProperties,
    SqlRuleFilter,
    CorrelationRuleFilter,
)


def get_admin_client() -> ServiceBusAdministrationClient:
    """Create Service Bus administration client."""
    namespace = os.environ.get("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE")
    conn_str = os.environ.get("SERVICEBUS_CONNECTION_STRING")

    if conn_str:
        return ServiceBusAdministrationClient.from_connection_string(conn_str)
    elif namespace:
        return ServiceBusAdministrationClient(
            fully_qualified_namespace=namespace, credential=DefaultAzureCredential()
        )
    else:
        raise ValueError(
            "Set SERVICEBUS_FULLY_QUALIFIED_NAMESPACE or SERVICEBUS_CONNECTION_STRING"
        )


def create_queue(
    client: ServiceBusAdministrationClient,
    name: str,
    max_delivery_count: int = 10,
    ttl_seconds: int | None = None,
    lock_duration_seconds: int = 60,
    enable_sessions: bool = False,
    enable_partitioning: bool = False,
) -> dict[str, Any]:
    """Create a Service Bus queue."""
    kwargs = {
        "max_delivery_count": max_delivery_count,
        "lock_duration": timedelta(seconds=lock_duration_seconds),
        "requires_session": enable_sessions,
        "enable_partitioning": enable_partitioning,
    }

    if ttl_seconds:
        kwargs["default_message_time_to_live"] = timedelta(seconds=ttl_seconds)

    queue = client.create_queue(name, **kwargs)

    return {
        "name": queue.name,
        "max_delivery_count": queue.max_delivery_count,
        "lock_duration": str(queue.lock_duration),
        "requires_session": queue.requires_session,
        "enable_partitioning": queue.enable_partitioning,
    }


def get_queue_info(client: ServiceBusAdministrationClient, name: str) -> dict[str, Any]:
    """Get queue properties and runtime info."""
    queue = client.get_queue(name)
    runtime = client.get_queue_runtime_properties(name)

    return {
        "name": queue.name,
        "max_delivery_count": queue.max_delivery_count,
        "lock_duration": str(queue.lock_duration),
        "default_ttl": str(queue.default_message_time_to_live),
        "requires_session": queue.requires_session,
        "enable_partitioning": queue.enable_partitioning,
        "runtime": {
            "active_message_count": runtime.active_message_count,
            "dead_letter_message_count": runtime.dead_letter_message_count,
            "scheduled_message_count": runtime.scheduled_message_count,
            "total_message_count": runtime.total_message_count,
        },
    }


def create_topic(
    client: ServiceBusAdministrationClient,
    name: str,
    ttl_seconds: int | None = None,
    enable_partitioning: bool = False,
) -> dict[str, Any]:
    """Create a Service Bus topic."""
    kwargs = {"enable_partitioning": enable_partitioning}

    if ttl_seconds:
        kwargs["default_message_time_to_live"] = timedelta(seconds=ttl_seconds)

    topic = client.create_topic(name, **kwargs)

    return {"name": topic.name, "enable_partitioning": topic.enable_partitioning}


def create_subscription(
    client: ServiceBusAdministrationClient,
    topic_name: str,
    subscription_name: str,
    sql_filter: str | None = None,
    max_delivery_count: int = 10,
    lock_duration_seconds: int = 60,
    enable_sessions: bool = False,
) -> dict[str, Any]:
    """Create a subscription with optional filter."""
    subscription = client.create_subscription(
        topic_name=topic_name,
        subscription_name=subscription_name,
        max_delivery_count=max_delivery_count,
        lock_duration=timedelta(seconds=lock_duration_seconds),
        requires_session=enable_sessions,
    )

    result = {
        "topic": topic_name,
        "subscription": subscription.name,
        "max_delivery_count": subscription.max_delivery_count,
        "requires_session": subscription.requires_session,
    }

    # Add SQL filter if provided
    if sql_filter:
        # Delete default rule and create filtered rule
        client.delete_rule(topic_name, subscription_name, "$Default")
        client.create_rule(
            topic_name=topic_name,
            subscription_name=subscription_name,
            rule_name="CustomFilter",
            filter=SqlRuleFilter(sql_filter),
        )
        result["filter"] = sql_filter

    return result


def get_dlq_count(
    client: ServiceBusAdministrationClient,
    name: str,
    is_subscription: bool = False,
    topic_name: str | None = None,
) -> dict[str, Any]:
    """Get dead-letter queue message count."""
    if is_subscription:
        runtime = client.get_subscription_runtime_properties(topic_name, name)
    else:
        runtime = client.get_queue_runtime_properties(name)

    return {
        "entity": f"{topic_name}/{name}" if is_subscription else name,
        "dead_letter_message_count": runtime.dead_letter_message_count,
        "active_message_count": runtime.active_message_count,
    }


def list_entities(
    client: ServiceBusAdministrationClient,
    entity_type: str,
    topic_name: str | None = None,
) -> list[str]:
    """List queues, topics, or subscriptions."""
    if entity_type == "queues":
        return [q.name for q in client.list_queues()]
    elif entity_type == "topics":
        return [t.name for t in client.list_topics()]
    elif entity_type == "subscriptions" and topic_name:
        return [s.name for s in client.list_subscriptions(topic_name)]
    else:
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Manage Azure Service Bus entities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="entity", required=True)

    # Queue commands
    queue_parser = subparsers.add_parser("queue", help="Queue operations")
    queue_subparsers = queue_parser.add_subparsers(dest="action", required=True)

    queue_create = queue_subparsers.add_parser("create", help="Create queue")
    queue_create.add_argument("name", help="Queue name")
    queue_create.add_argument(
        "--max-delivery", type=int, default=10, help="Max delivery count"
    )
    queue_create.add_argument("--ttl", type=int, help="Default message TTL in seconds")
    queue_create.add_argument(
        "--lock-duration", type=int, default=60, help="Lock duration in seconds"
    )
    queue_create.add_argument("--sessions", action="store_true", help="Enable sessions")
    queue_create.add_argument(
        "--partitioned", action="store_true", help="Enable partitioning"
    )

    queue_info = queue_subparsers.add_parser("info", help="Get queue info")
    queue_info.add_argument("name", help="Queue name")

    queue_list = queue_subparsers.add_parser("list", help="List queues")

    queue_delete = queue_subparsers.add_parser("delete", help="Delete queue")
    queue_delete.add_argument("name", help="Queue name")

    # Topic commands
    topic_parser = subparsers.add_parser("topic", help="Topic operations")
    topic_subparsers = topic_parser.add_subparsers(dest="action", required=True)

    topic_create = topic_subparsers.add_parser("create", help="Create topic")
    topic_create.add_argument("name", help="Topic name")
    topic_create.add_argument("--ttl", type=int, help="Default message TTL in seconds")
    topic_create.add_argument(
        "--partitioned", action="store_true", help="Enable partitioning"
    )

    topic_list = topic_subparsers.add_parser("list", help="List topics")

    topic_delete = topic_subparsers.add_parser("delete", help="Delete topic")
    topic_delete.add_argument("name", help="Topic name")

    # Subscription commands
    sub_parser = subparsers.add_parser("subscription", help="Subscription operations")
    sub_subparsers = sub_parser.add_subparsers(dest="action", required=True)

    sub_create = sub_subparsers.add_parser("create", help="Create subscription")
    sub_create.add_argument("topic", help="Topic name")
    sub_create.add_argument("name", help="Subscription name")
    sub_create.add_argument("--filter", help="SQL filter expression")
    sub_create.add_argument(
        "--max-delivery", type=int, default=10, help="Max delivery count"
    )
    sub_create.add_argument("--sessions", action="store_true", help="Enable sessions")

    sub_list = sub_subparsers.add_parser("list", help="List subscriptions")
    sub_list.add_argument("topic", help="Topic name")

    sub_delete = sub_subparsers.add_parser("delete", help="Delete subscription")
    sub_delete.add_argument("topic", help="Topic name")
    sub_delete.add_argument("name", help="Subscription name")

    # DLQ commands
    dlq_parser = subparsers.add_parser("dlq", help="Dead-letter queue operations")
    dlq_subparsers = dlq_parser.add_subparsers(dest="action", required=True)

    dlq_count = dlq_subparsers.add_parser("count", help="Get DLQ message count")
    dlq_count.add_argument("name", help="Queue or subscription name")
    dlq_count.add_argument("--topic", help="Topic name (for subscriptions)")

    parser.add_argument("--output", "-o", choices=["json", "text"], default="text")

    args = parser.parse_args()

    try:
        client = get_admin_client()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    result = None

    try:
        if args.entity == "queue":
            if args.action == "create":
                result = create_queue(
                    client,
                    args.name,
                    max_delivery_count=args.max_delivery,
                    ttl_seconds=args.ttl,
                    lock_duration_seconds=args.lock_duration,
                    enable_sessions=args.sessions,
                    enable_partitioning=args.partitioned,
                )
            elif args.action == "info":
                result = get_queue_info(client, args.name)
            elif args.action == "list":
                result = list_entities(client, "queues")
            elif args.action == "delete":
                client.delete_queue(args.name)
                result = {"deleted": args.name}

        elif args.entity == "topic":
            if args.action == "create":
                result = create_topic(
                    client,
                    args.name,
                    ttl_seconds=args.ttl,
                    enable_partitioning=args.partitioned,
                )
            elif args.action == "list":
                result = list_entities(client, "topics")
            elif args.action == "delete":
                client.delete_topic(args.name)
                result = {"deleted": args.name}

        elif args.entity == "subscription":
            if args.action == "create":
                result = create_subscription(
                    client,
                    args.topic,
                    args.name,
                    sql_filter=args.filter,
                    max_delivery_count=args.max_delivery,
                    enable_sessions=args.sessions,
                )
            elif args.action == "list":
                result = list_entities(client, "subscriptions", args.topic)
            elif args.action == "delete":
                client.delete_subscription(args.topic, args.name)
                result = {"deleted": f"{args.topic}/{args.name}"}

        elif args.entity == "dlq":
            if args.action == "count":
                result = get_dlq_count(
                    client,
                    args.name,
                    is_subscription=bool(args.topic),
                    topic_name=args.topic,
                )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Output result
    if result:
        if args.output == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            if isinstance(result, list):
                for item in result:
                    print(f"  - {item}")
            elif isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, dict):
                        print(f"{key}:")
                        for k, v in value.items():
                            print(f"  {k}: {v}")
                    else:
                        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
