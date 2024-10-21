from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable, UnknownTopicOrPartitionError, IllegalStateError
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_DOMAIN = os.getenv("KAFKA_DOMAIN")

# SSL Configuration
CARoot = "/path_to_the_certificates/kafka-ssl-baremetal/CARoot.pem"
cert_file = "/path_to_the_certificates/kafka-ssl-baremetal/ca-cert"
key_file = "/path_to_the_certificates/kafka-ssl-baremetal/ca-key"
ssl_password = KAFKA_PASSWORD
bootstrap_servers = [KAFKA_DOMAIN]

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Kafka Router
kafka_router = APIRouter(prefix="/kafka", tags=["kafka"])

# Initialize the KafkaAdminClient
try:
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_check_hostname=False,
        ssl_cafile=CARoot,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file,
        ssl_password=ssl_password,
    )
except NoBrokersAvailable:
    raise HTTPException(status_code=500, detail="No Kafka brokers available. Please check your Kafka server.")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

class Topic(BaseModel):
    topic_name: str
    num_partitions: int = 1
    replication_factor: int = 1

app = FastAPI()

@app.get("/")
async def healthcheck():
    """
    Check if the ADMIN REST API is running
    """
    try:
        # Attempt to list topics to check the connection to Kafka
        admin_client.list_topics()
        return {"status": "ok", "message": "API is running and connected to Kafka"}
    except NoBrokersAvailable:
        raise HTTPException(status_code=500, detail="No Kafka brokers available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@kafka_router.post("/topics")
async def create_topic(topic: Topic):
    """
    Create a new Kafka topic
    """
    new_topic = NewTopic(
        name=topic.topic_name,
        num_partitions=topic.num_partitions,
        replication_factor=topic.replication_factor
    )

    try:
        admin_client.create_topics(new_topics=[new_topic], validate_only=False)
        return {"message": f"Topic '{topic.topic_name}' created successfully"}
    except TopicAlreadyExistsError:
        raise HTTPException(status_code=400, detail=f"Topic '{topic.topic_name}' already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@kafka_router.get("/topics")
async def list_topics():
    """
    List all Kafka topics
    """
    try:
        topics = admin_client.list_topics()
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@kafka_router.delete("/topics/{topic_name}")
async def delete_topic(topic_name: str):
    """
    Delete a Kafka topic only if there are no active consumers
    """
    try:
        admin_client.delete_topics([topic_name])
        return {"message": f"Topic '{topic_name}' deleted successfully"}
    except UnknownTopicOrPartitionError:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' does not exist")
    except IllegalStateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(kafka_router, tags=["kafka"])