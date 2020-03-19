from pykafka import KafkaClient

urls = [
    'https://live.staticflickr.com/7454/8728178381_00be690ebc_b.jpg',
    'https://farm4.staticflickr.com/3289/3103459782_1a2041a696_b.jpg',
    'https://farm9.staticflickr.com/8116/8606654389_e56c706e2c_b.jpg'
]

client = KafkaClient(hosts='kafka:9092')
topic = client.topics['inbound_images']
with topic.get_sync_producer() as producer:
    for url in urls:
        producer.produce(bytes(url, 'utf-8'))

