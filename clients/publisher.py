from kafka import KafkaProducer
import time
import random


def kafka_publisher_ssl():
    CARoot = "/user/ubuntu/home/apache-kafka-ssl/CARoot.pem"
    cert_file = "/user/ubuntu/home/apache-kafka-ssl/ca-cert"
    key_file = "/user/ubuntu/home/apache-kafka-ssl/ca-key"
    Topic = "test"

    publisher = KafkaProducer(
        bootstrap_servers=["10.10.10.10:9093"],
        security_protocol="SSL",
        ssl_check_hostname=False,
        ssl_cafile=CARoot,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file,
        ssl_password="your_must_add_password_here",
    )

    for i in range(20):
        paylod = random.randint(1, 100)
        publisher.send(Topic, value=f"Message {paylod}".encode("utf-8"))
        publisher.flush()
        print(f"Message {paylod} sent to topic {Topic} successfully.")
        time.sleep(5)


kafka_publisher_ssl()