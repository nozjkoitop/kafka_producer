#!/usr/bin/env sh
set -eu

: "${BOOTSTRAP_SERVER:=kafka:9092}"
: "${TEST_TOPIC_NAME:?TEST_TOPIC_NAME is required}"

/opt/kafka/bin/kafka-topics.sh \
  --create \
  --if-not-exists \
  --topic "$TEST_TOPIC_NAME" \
  --bootstrap-server "$BOOTSTRAP_SERVER"

echo "topic $TEST_TOPIC_NAME is ready"