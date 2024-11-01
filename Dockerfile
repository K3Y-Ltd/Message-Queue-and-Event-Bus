FROM ubuntu
WORKDIR /
RUN apt-get update > /dev/null && apt-get install runit -y > /dev/null
RUN apt-get update > /dev/null && apt-get install libssl-dev openssl -y > /dev/null
RUN apt-get update > /dev/null && apt-get install openjdk-8-jdk -y > /dev/null


ADD https://archive.apache.org/dist/kafka/2.2.0/kafka_2.11-2.2.0.tgz .
RUN tar xzf kafka_2.11-2.2.0.tgz && rm kafka_2.11-2.2.0.tgz

RUN mkdir -p /etc/service/zookeeper/
RUN mkdir -p /etc/service/kafka/

COPY serverssl.properties .
COPY prepStartup.sh .

RUN /bin/bash -c "echo -e '#!/bin/bash\nexec /kafka_2.11-2.2.0/bin/zookeeper-server-start.sh /kafka_2.11-2.2.0/config/zookeeper.properties \n' > /etc/service/zookeeper/run"
RUN /bin/bash -c "echo -e '#!/bin/bash\n/prepStartup.sh\nexec /kafka_2.11-2.2.0/bin/kafka-server-start.sh /kafka_2.11-2.2.0/config/serverssl.properties \n' > /etc/service/kafka/run"

RUN chmod +x /etc/service/zookeeper/run
RUN chmod +x /etc/service/kafka/run

ENV KAFKA_HOME=/kafka_2.11-2.2.0
ENV PASSWORD="your_must_add_password_here"
ENV DOMAIN="10.10.10.10"

EXPOSE 2181/tcp
EXPOSE 9093/tcp
EXPOSE 9094/tcp

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s \
CMD [[ $(sv status kafka) =~ "run" ]] || exit 1

CMD ["runsvdir", "/etc/service"]
