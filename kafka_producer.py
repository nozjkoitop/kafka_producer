import argparse
import datetime
import json
import logging
import random
import time
import uuid

from confluent_kafka import Producer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_data_point_default(ratio_prev):
    """Generates data points with current day or previous day timestamps."""
    today = datetime.datetime.utcnow()
    if random.random() < ratio_prev:
        chosen_day = today - datetime.timedelta(days=1)
    else:
        chosen_day = today

    timestamp = chosen_day.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    ).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    value1 = round(random.random() * 100, 2)  # Random value between 0 and 100 (2 decimals)
    value2 = "data_" + str(uuid.uuid4())[:8]  # Random string identifier
    return {"timestamp": timestamp, "value1": value1, "value2": value2}


def generate_data_point_prev_month(ratio_prev):
    """Generates data points with a mix of previous and current month timestamps."""
    today = datetime.datetime.utcnow()
    first_day_current_month = today.replace(day=1)
    first_day_prev_month = (first_day_current_month - datetime.timedelta(days=1)).replace(day=1)

    if random.random() < ratio_prev:
        random_day = random.randint(1, (first_day_current_month - first_day_prev_month).days)
        timestamp = (first_day_prev_month + datetime.timedelta(days=random_day - 1)).replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    else:
        random_day = random.randint(1, today.day)
        timestamp = (first_day_current_month + datetime.timedelta(days=random_day - 1)).replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    value1 = round(random.random() * 100, 2)  # Random value between 0 and 100 (2 decimals)
    value2 = "data_" + str(uuid.uuid4())[:8]  # Random string identifier
    return {"timestamp": timestamp, "value1": value1, "value2": value2}


def delivery_report(err, msg):
    if err is not None:
        logger.error(f'Delivery failed: {err}')
    else:
        logger.info(f'Message {msg.value().decode("utf-8")}'
                    f' delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


def produce(host, port, topic, num_messages, interval, ratio_prev, flow):
    kafka_config = {
        'bootstrap.servers': f'{host}:{port}',
        'client.id': 'python-producer'
    }

    kafka_topic = topic
    producer = Producer(kafka_config)

    # Choose the data generation flow
    if flow == 'default':
        generate_data_point = generate_data_point_default
    elif flow == 'prev_month':
        def generate_data_point():
            return generate_data_point_prev_month(ratio_prev)
    else:
        raise ValueError(f"Unknown flow: {flow}")

    try:
        for i in range(num_messages):
            event_data = generate_data_point(ratio_prev)
            value_json = json.dumps(event_data)
            producer.produce(kafka_topic, key=f'key-{i}', value=value_json, callback=delivery_report)
            producer.poll(0)
            time.sleep(interval)

    except KeyboardInterrupt:
        pass

    finally:
        producer.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produce JSON messages to a Kafka topic.')
    parser.add_argument('-g', '--host', type=str, required=True, help='Kafka broker host')
    parser.add_argument('-p', '--port', type=int, required=True, help='Kafka broker port')
    parser.add_argument('-t', '--topic', required=True, help='Kafka topic to produce messages')
    parser.add_argument('-a', '--amount', type=int, default=100, help='Number of messages to produce (default: 100)')
    parser.add_argument('-i', '--interval', type=int, default=1,
                        help='Interval between messages in seconds (default: 1)')
    parser.add_argument('-r', '--ratio_prev', type=float, default=0.5,
                        help='Ratio of messages from the previous day/month (default: 0.5)')
    parser.add_argument('-f', '--flow', type=str, default='default',
                        choices=['default', 'prev_month'],
                        help='Flow to use for generating data points (default: "default")')

    args = parser.parse_args()
    produce(args.host, args.port, args.topic, args.amount, args.interval, args.ratio_prev, args.flow)
