#!/usr/bin/env python3

import argparse
import datetime as dt
import json
import logging
import random
import time
import uuid

from confluent_kafka import Producer


logger = logging.getLogger(__name__)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def format_timestamp(value: dt.datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def random_today_timestamp() -> dt.datetime:
    now = utc_now()
    return now.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999) * 1000,
    )


def generate_event() -> dict:
    return {
        "timestamp": format_timestamp(random_today_timestamp()),
        "value1": round(random.random() * 100, 2),
        "value2": f"data_{str(uuid.uuid4())[:8]}",
    }


def delivery_report(err, msg) -> None:
    if err:
        logger.error("Delivery failed: %s", err)
        return

    logger.debug(
        "Delivered to %s [%s] offset %s",
        msg.topic(),
        msg.partition(),
        msg.offset(),
    )


def validate_args(args: argparse.Namespace) -> None:
    if not args.host.strip():
        raise ValueError("host must not be blank")
    if args.port <= 0:
        raise ValueError("port must be > 0")
    if not args.topic.strip():
        raise ValueError("topic must not be blank")
    if args.amount < 0:
        raise ValueError("amount must be >= 0")
    if args.interval < 0:
        raise ValueError("interval must be >= 0")


def produce(args: argparse.Namespace) -> None:
    validate_args(args)

    producer = Producer({
        "bootstrap.servers": f"{args.host}:{args.port}",
        "client.id": "python-producer",
    })

    try:
        for i in range(args.amount):
            value = json.dumps(generate_event(), separators=(",", ":"))

            producer.produce(
                topic=args.topic,
                key=f"key-{i}",
                value=value,
                callback=delivery_report,
            )

            producer.poll(0)
            logger.info("Produced message %s/%s: %s", i + 1, args.amount, value)

            if args.interval:
                time.sleep(args.interval)
    finally:
        producer.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce JSON messages to Kafka.")

    parser.add_argument("--host", default="localhost", help="Kafka broker host")
    parser.add_argument("--port", type=int, default=9093, help="Kafka broker port")
    parser.add_argument("-t", "--topic", default="test", help="Kafka topic")
    parser.add_argument("-a", "--amount", type=int, default=100, help="Number of messages")
    parser.add_argument("-i", "--interval", type=float, default=1, help="Delay between messages in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    produce(args)


if __name__ == "__main__":
    main()