#!/bin/bash
set -e
 
# Load docker defaults and check conf
docker info

# Change folder to the root folder
PARENTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../ && pwd )"
cd $PARENTDIR

docker build -f tests/docker/Dockerfile . -t weevely
docker rm -f weevely-inst || echo ''
docker run  --rm --name weevely-inst -v `pwd`:/app/ -p 80:80 -d weevely 

# Wait until the http server is serving
until $(curl --output /dev/null --silent --head http://localhost/); do
    sleep 1
done

if [ -z "$1" ]
  then
    docker exec -it weevely-inst python -m unittest discover ./tests/ "test_*.py"
elif [ "$1" = "bash" ]
  then
    docker exec -it weevely-inst /bin/bash
else
    docker exec -it weevely-inst python -m unittest discover ./tests/ "test_$1.py"
fi



docker rm -f weevely-inst 