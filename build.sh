#!/bin/bash

docker stop dnsbenchmark_instance
docker rm dnsbenchmark_instance 
docker rmi dnsbenchmark


docker build -t dnsbenchmark .
docker run --restart=always --name dnsbenchmark_instance -d -t dnsbenchmark 


#docker logs -f dnsbenchmark_instance