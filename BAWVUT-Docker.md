
# BAWVUT in Docker

## Base images

### RHEL base image
```
# needs RH registry login
podman login registry.redhat.io

docker pull rhel8/python-38
podman pull rhel8/python-38
```

### Alpine base image
```
docker pull python:latest
docker pull python:alpine3.18
# or
podman pull python:latest
podman pull python:alpine3.18
```

## Build BAWVUT image
```
podman login -u $QUAY_USER -p $QUAY_PWD quay.io

REPO_NAME=marco_antonioni
podman build -t quay.io/${REPO_NAME}/bawvut:latest -f ./Dockerfile
podman push quay.io/${REPO_NAME}/bawvut:latest
```

## Run BAWVUT image

use '-p 8089:8089' when Locust configuration is set to 'headless = false'

```
mkdir -p ./test-configs/{conf1,conf2}
mkdir -p ./test-configs/conf1/outputdata
mkdir -p ./test-configs/conf2/outputdata


touch ./test-configs/conf1/cfg1.conf
touch ./test-configs/conf1/env1.properties
touch ./test-configs/conf1/ts1.csv
touch ./test-configs/conf1/us-ts1.csv
touch ./test-configs/conf1/creds1.csv
touch ./test-configs/conf1/assertManager1.py
touch ./test-configs/conf1/payloadManager1.py


REPO_NAME=marco_antonioni
podman run -it --rm --name bawvut \
    -p 8089:8089 \
    -v ./test-configs/conf1:/bawvut/configurations:Z \
    -v ./test-configs/conf1/outputdata:/bawvut/outputdata:Z \
    -t quay.io/${REPO_NAME}/bawvut:latest locust --config=./configurations/cfg1.conf

# or from inside the container
locust --config=/bawvut/configurations/cfg1.conf
```
