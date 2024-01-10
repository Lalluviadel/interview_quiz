"""Contains kafka files: user statistics publisher & consumer."""
import os
KAFKA_BOOTSTRAP_SERVERS = os.environ.get(
    'KAFKA_BOOTSTRAP_SERVERS', '172.30.0.2:9092'
)  # 'localhost:29092'
KAFKA_TOPIC_TEST = os.environ.get('KAFKA_TOPIC_TEST', 'test')
KAFKA_API_VERSION = os.environ.get('KAFKA_API_VERSION', (7, 5, 3))
