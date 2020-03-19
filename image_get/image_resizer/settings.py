import os

# Kafka configuration
KAFKA_HOSTS = os.getenv('KAFKA_HOSTS', 'kafka:9092')
ZOOKEEPER_HOST = os.getenv('ZOOKEEPER_HOST', 'zookeeper:2181')

# Maximum size of the resized image
TARGET_RESOLUTION = (640, 480)

# Number of images to download and resize simultaneously
BATCH_SIZE = 300
