# Import required packages
from kafka import KafkaProducer
import time

# Globally define variables that should be handy to change
TOPIC_NAME = 'meetup_topic'


# Create a producer and implement a retry mechanism
# The retry mechanism is required to consider the startup of the Kafka service
def create_producer(max_retries=20, retry_timeout=5):
    for attempt in range(max_retries):
        try:
            print(f'Attempt {attempt + 1} to create KafkaProducer...')
            producer = KafkaProducer(bootstrap_servers='kafka:9092')
            if producer:
                print('Successfully created KafkaProducer...')
                return producer

        # Catch exception
        except Exception as e: \
                print(
                    f'Attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_timeout} seconds. Error: {str(e)}')
        time.sleep(retry_timeout)

        # Wait for 5 seconds before retrying
        time.sleep(retry_timeout)
    raise Exception(f'KafkaProducer could not be created after {max_retries} retries')


# Create a producer and stream the data_source for each line in the json file
def stream_data_to_kafka(file_path, topic_name):
    producer = create_producer()
    with open(file_path) as file:
        for line in file:
            # Strip the line of any whitespaces
            data = line.strip()

            # Send to topic
            producer.send(topic_name, data.encode('utf-8'))
            producer.flush()

            # Wait 0.1 seconds to simulate a real data_source stream
            time.sleep(0.1)


if __name__ == '__main__':
    stream_data_to_kafka('/data_source/meetup.json', TOPIC_NAME)
