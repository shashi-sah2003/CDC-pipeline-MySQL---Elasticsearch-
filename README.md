# MySQL to Elasticsearch CDC Pipeline

A Change Data Capture (CDC) pipeline that synchronizes data from MySQL to Elasticsearch using Debezium and RabbitMQ.

## Architecture

The system uses a microservices architecture with Docker-containerized components:

- **MySQL**: Source database storing product data
- **Debezium**: Captures database changes from MySQL binlog
- **RabbitMQ**: Message broker for change events
- **Elasticsearch**: Target database for storing synchronized data 
- **Product Insertion Service**: Adds sample products to MySQL
- **Elasticsearch Consumer**: Processes messages and updates Elasticsearch

## Prerequisites

- Docker Engine
- Docker Compose

## Setup & Running

1. Fork & Clone this repository
```bash
git clone <repository-url>
cd <project-directory>
```

2. Start all services:
```bash
sudo docker-compose up -build
```

3. Access Elasticsearch shell:
```bash 
sudo docker exec -it elasticsearch bash
```

4. Verify data synchronization:
```bash
curl -X GET "http://localhost:9200/products/_search?pretty&size=60"
```

## Service Ports:

1. MySQL on port 3307
2. RabbitMQ on ports 5672 (AMQP) and 15672 (Management UI)
3. Elasticsearch on port 9200
4. Debezium Server on port 8080

## Data Flow

1. The Product Insertion service adds sample products to MySQL every 2 seconds
2. Debezium captures changes from MySQL's binlog
3. Change events are published to RabbitMQ exchange
4. Elasticsearch Consumer processes the messages and updates Elasticsearch accordingly
