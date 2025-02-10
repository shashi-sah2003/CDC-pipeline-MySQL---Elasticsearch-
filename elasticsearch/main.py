from elasticsearch import Elasticsearch
import json
import pika
import os
from dotenv import load_dotenv
import time

load_dotenv()

CLOUDAMQP_URL = os.getenv("CLOUDAMQP_URL")
params = pika.URLParameters(CLOUDAMQP_URL)

# Retry mechanism for the RabbitMQ connection
max_retries = 5
for i in range(max_retries):
    try:
        connection = pika.BlockingConnection(params)
        print("[✅] Connection over channel established")
        break
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[⚠️] Connection failed (attempt {i+1}/{max_retries}): {e}")
        time.sleep(5)
else:
    raise Exception("Failed to connect to RabbitMQ after several attempts.")


channel = connection.channel()

es = Elasticsearch(['http://elasticsearch:9200'])

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        payload = data.get('payload', {})

        if 'after' in payload:

            doc = payload['after']
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    es.index(index='products', id=doc['id'], body=doc)
                    print(f"[✅] Indexed to Elasticsearch: {doc}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Retry {attempt + 1}/{max_retries}: {e}")
                    time.sleep(1)

        elif 'before' in payload:

            doc = payload['before']
            es.delete(index='products', id=doc['id'])
            print(f"[✅] Deleted from Elasticsearch: {doc}")

        else:

            print(f"[⚠️] No 'after' & 'before' data in payload: {payload}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")

channel.basic_qos(prefetch_count=1000)
channel.basic_consume(
    queue='elasticsearch',
    on_message_callback=callback,
    auto_ack=False
)

print("[❎] Waiting for messages. To exit press CTRL+C")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.close()
    connection.close()
    print("Connection closed.")