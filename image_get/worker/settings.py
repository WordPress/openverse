import os

# S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

# Kafka
KAFKA_HOSTS = os.getenv('KAFKA_HOSTS', 'kafka:9092')
ZOOKEEPER_HOST = os.getenv('ZOOKEEPER_HOST', 'zookeeper:2181')

# Maximum size of the resized image
TARGET_RESOLUTION = (640, 480)

# Number of images to download and resize simultaneously
BATCH_SIZE = 500
