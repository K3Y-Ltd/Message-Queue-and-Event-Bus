![ACROSS](/docs/logo_across.jpg)

# Message Queue and Event Bus (MQEB)



This Repository Holds the configuration and instruction for setting up a Message Queue and Event Bus (MQEB) utilizing Apache Kafka as the underlying software tool. MQEB has also been configured with SSL and it is integrated with a REST API for facilitating CRUD operations on topics.

![Architecture](/docs/MQEB.jpg)

## Description
MQEB is running inside an Ubuntu Contianer and all the necessary steps to create the associated certificates are performed during the docker build step.

## Prerequisite
In order to run and deploy Apache Kafka the following must be included:
- docker
- docker-compose


## MQEB Instalation
To deploy and create the associated certificates you must follow the steps:
1) Create a `.env` file following the `.env.local` descriptions.
2) Change the `PASSWORD` in Dockerfile in the same as you specified in the `.env` file.
3) Change the `DOMAIN` in the Dockerfile in the same as you specified in the `.env` file.
4) Run `docker-compose up -d` to build the MQEB container and the associated certificates in the `/ssl` folder
5) Copy the certificates that have been created from inside the container to the hostmachine in order to provide them to potential clients to connect
   1) ***NOTE***: Before you copy the certificates you must change the ca-cert into CARoot that follow PEM format which is compatible with python
      1) Attach into the running container `docker exec -it {kafkassl} bash`
      2) Run the command to convert the ca-cert, `openssl x509 -in ca-cert -out CARoot.pem -outform PEM` inside the docker's container directory `/kafka_2.11-2.2.0/ssl`
      3) Disconnect from the running container
   2) Copy the certificates out with the command: `docker cp <container_id>:/kafka_2.11-2.2.0/ssl /path/on/your/host/vm`
6) Change the paths for the certificates inside the admin.py

## REST API
In order to run the REST API the following criteria must be met:
1) [FastAPI](https://fastapi.tiangolo.com/)
2) [Uvicorn](https://www.uvicorn.org/)
3) [Kafka-Python](https://kafka-python.readthedocs.io/en/master/)

### Execute
Run the Admin REST API in a long running process in the background which will log every operation in a uvicorn.log file for tracing:

`nohup uvicorn admin:app --host 0.0.0.0 --port 5001 > uvicorn.log 2>&1 &`

A Swagger file is also provided under the `{VM_IP_ADDRESS}:5001/docs` or `{VM_IP_ADDRESS}:5001/redocs`.

A `swagger.json` is provided for the reusability of the endpoints.


## Validation
In order to validate the connectivity with the running SSL Apache Kafka Broker in the repository two python clients are provided under the clients directory:
- A publisher for broadcasting data
- A subscriber for receiving data

In order to run these clients the following steps must take place:
1) Change the file paths for reading the certificates:
```python
CARoot = "{path_to_the_created_certificate}/CARoot.pem"
cert_file = "{path_to_the_created_certificate}/ca-cert"
key_file = "{path_to_the_created_certificate}/ca-key"
Topic = "{topic_name}"
```
2) Change the IP Address for the running broker:
```python
# E.g., bootstrap_servers=["10.10.10.10:9093"],
bootstrap_servers=["{ip_address}:{ssl_port_number}"]
```
3) Change the `ssl_password` with the one you specified in the env:
```python
# E.g., sl_password="your_must_add_password_here",
sl_password="{ssl_password}"
```
4) Run the clients with the respective commands:
   1) `python subscriber.py`
   2) `python publisher.py`

## Build a Docker Image
Due the fact that the Dockerfile has some environment variables the docker image is built localy when `docker-compose` command is executed.

In order to build it for the Github Registry you must change the following entries first and then run the commands:
1) Change the values to be the same as the `.env.local`
```Dockerfile
ENV PASSWORD="your_must_add_password_here"
ENV DOMAIN="10.10.10.10"
```
2) Build the docker image for linux/AMD64 platform

```bash
docker build . -t ghcr.io/k3y-ltd/apache-kafka-ssl:0.0.1 --platform linux/amd64
```
3) Push image to Github Registry
```shell
docker push ghcr.io/k3y-ltd/apache-kafka-ssl:0.0.1
```
4) Once you have uploaded the Docker Image to the Company Registry you can pull it in the `doker-compose.yml` file and change the following line
```yml
(-) build:
(-)     context: .
(-)     dockerfile: Dockerfile

# Change the above lines to the bottom
(+) build:
(+)     iamge: ghcr.io/k3y-ltd/apache-kafka-ssl:0.0.1
```
5) Run or build the container `docker-compose up -d`

![K3Y Ltd.](/docs/logo_k3y.png)