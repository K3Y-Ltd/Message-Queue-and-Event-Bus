from kafka import KafkaConsumer


def kafka_consumer_ssl():
    CARoot = "/user/ubuntu/home/apache-kafka-ssl/CARoot.pem"
    cert_file = "/user/ubuntu/home/apache-kafka-ssl/ca-cert"
    key_file = "/user/ubuntu/home/apache-kafka-ssl/ca-key"
    Topic = "test"

    consumer = KafkaConsumer(
        Topic,
        bootstrap_servers=["10.10.10.10:9093"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda x: x.decode("utf-8"),
        security_protocol="SSL",
        ssl_check_hostname=False,
        ssl_cafile=CARoot,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file,
        ssl_password="your_must_add_password_here",
    )
    for event in consumer:
        print(event.value)


kafka_consumer_ssl()
