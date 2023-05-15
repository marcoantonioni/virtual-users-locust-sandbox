
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
REPO_NAME=marco_antonioni
podman build -t quay.io/${REPO_NAME}/bawvut:latest -f ./Dockerfile
```

## Run BAWVUT image
```
podman run -it --rm --name bawvut \
    -v /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/configurations:/bawvut/configurations:Z \
    -v /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/outputdata:/bawvut/outputdata:Z \
    -t quay.io/${REPO_NAME}/bawvut:latest /bin/bash

# from inside the container
locust --config=./configurations/baw-vu-cfg-ut1.conf
```
