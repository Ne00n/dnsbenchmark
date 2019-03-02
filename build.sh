#!/bin/bash

docker stop dnsbenchmark_instance
docker rm dnsbenchmark_instance 
docker rmi dnsbenchmark


docker build -t dnsbenchmark .
docker run --restart=always --name dnsbenchmark_instance -d -t dnsbenchmark 

#docker exec -i -t dnsbenchmark_instance /bin/bash

timeout 5 docker exec -i -t dnsbenchmark_instance sh -c "python2 bot.py --dns 1.1.1.1 --hostnames domains.dat --threads 30"


