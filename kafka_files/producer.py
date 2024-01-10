"""Kafka Producer class."""

import json
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from kafka_files import (
    KAFKA_API_VERSION,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_TEST,
)


class UserLogProducer:
    """Producer class."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize Producer."""
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            retries=2,
            api_version=KAFKA_API_VERSION
        )

    def send_msg(self, msg):
        """
        Send message to the Kafka server.

        Args:
            msg (dict): message to the Kafka server.

        Returns:
            None:
        """
        try:
            self.producer.send(
                KAFKA_TOPIC_TEST, msg
            )
            self.producer.flush()
        except KafkaTimeoutError as err:
            self.logger.error(err)
