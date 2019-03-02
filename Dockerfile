FROM ubuntu:18.04

WORKDIR /app

COPY . ./

# install python2
RUN apt-get update
RUN apt-get install python -y


# cleanup
RUN apt-get clean -y
RUN rm -rf /var/lib/apt/lists/*



CMD tail -f /dev/null
