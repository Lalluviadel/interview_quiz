"""Kafka Consumer class."""
import json
import logging

from django.core.exceptions import ObjectDoesNotExist

from kafka import KafkaConsumer

from kafka_files import (
    KAFKA_API_VERSION, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_TEST
)

from user_log.models import UserLog


class UserLogConsumer:
    """Consumer class."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize Consumer."""
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC_TEST,
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            group_id='test',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            api_version=KAFKA_API_VERSION,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.logger.info('Consumer is running.')

    def get_message(self, msg):
        """
        Process user statistics messages from kafka publisher.

        Args:
            msg (kafka.consumer.fetcher.ConsumerRecord):
                consumer message.
        Returns:
            bool: result of the message getting and processing.
        """
        try:
            user_log_id = msg.value.get('user_id')
            guessed = msg.value.get('guessed')

            if user_log_id:
                try:
                    user_log = UserLog.objects.get(id=user_log_id)
                    user_log.question_count += 1
                    if guessed:
                        user_log.right_answers += 1
                    else:
                        user_log.wrong_answers += 1
                    user_log.save()
                    return True
                except ObjectDoesNotExist:
                    self.logger.error(
                        'User log with id %s does not exist.',
                        user_log_id
                    )
                    return False
            self.logger.error('The message does not contain an id.')
            return False
        except Exception as err:
            self.consumer.close()
            self.logger.error('Consumer is stopped due %s', err)
            return False
