#!/bin/bash
set -e
 
# Load docker defaults and check conf
docker info

ENTRYPOINT=""
if [ "$1" = "bash" ];then
    ENTRYPOINT=" --entrypoint /bin/bash"
fi

# Change folder to the root folder
PARENTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../ && pwd )"
cd $PARENTDIR

docker build -f tests/docker/Dockerfile . -t weevely
docker run -v `pwd`:/app/ -it${ENTRYPOINT} -p 80:80 weevely 