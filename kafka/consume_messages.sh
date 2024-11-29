#!/bin/bash
sleep 5

/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $TEST_TOPIC_NAME --bootstrap-server kafka:9092

sleep 1

/opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic $TEST_TOPIC_NAME --group $TEST_TOPIC_GROUP_NAME --from-beginning

