import argparse
import json
import logging
import random
import time
import uuid

from confluent_kafka import Producer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_data_point():
    timestamp = "2024-03-13T" + f"{time.time() % 1:.6f}Z"  # Generate unique timestamps
    value1 = round(random.random() * 100, 2)  # Random value between 0 and 100 (2 decimals)
    value2 = "data_" + str(uuid.uuid4())[:8]  # Random string identifier
    return {"timestamp": timestamp, "value1": value1, "value2": value2}


def delivery_report(err, msg):
    if err is not None:
        logger.error(f'Delivery failed: {err}')
    else:
        logger.info(f'Message {msg.value().decode("utf-8")}'
                    f' delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


def produce(host, port, topic, num_messages, interval):
    kafka_config = {
        'bootstrap.servers': f'{host}:{port}',
        'client.id': 'python-producer'
    }

    kafka_topic = topic

    producer = Producer(kafka_config)

    try:
        for i in range(num_messages):
            event_data = generate_data_point()
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
    parser.add_argument('-g', '--host', type=str,  required=True, help='Kafka broker host')
    parser.add_argument('-p', '--port', type=int, required=True, help='Kafka broker port')
    parser.add_argument('-t', '--topic', required=True, help='Kafka topic to produce messages')
    parser.add_argument('-a', '--amount', type=int, default=100, help='Number of messages to produce (default: 100)')
    parser.add_argument('-i', '--interval', type=int, default=1,
                        help='Interval between messages in seconds (default: 1)')

    args = parser.parse_args()
    produce(args.host, args.port, args.topic, args.amount, args.interval)
