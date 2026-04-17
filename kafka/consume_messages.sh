#!/usr/bin/env sh
set -eu

: "${BOOTSTRAP_SERVER:=kafka:9092}"
: "${TEST_TOPIC_NAME:?TEST_TOPIC_NAME is required}"
: "${TEST_TOPIC_GROUP_NAME:?TEST_TOPIC_GROUP_NAME is required}"

exec /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server "$BOOTSTRAP_SERVER" \
  --topic "$TEST_TOPIC_NAME" \
  --group "$TEST_TOPIC_GROUP_NAME" \
  --from-beginning