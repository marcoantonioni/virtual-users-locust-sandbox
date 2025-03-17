
# BAWVUT Docker

## Base images

Choose RH or Alpine base images

### RHEL base image
```
# needs RH registry login
podman login -u $REGISTRY_USER -p $REGISTRY_PWD registry.redhat.io

# old
docker pull rhel8/python-38
podman pull rhel8/python-38

# new
podman pull registry.redhat.io/ubi9/python-312:9.5-1742197730
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

Update dockerfile with image name (ex: FROM registry.redhat.io/ubi9/python-312:9.5-1742197730)

```
cd ./virtual-users-locust-sandbox

REPO_NAME=marco_antonioni
TAG=$(date +"%Y-%m-%dT%H-%M-%S")
podman build -t quay.io/${REPO_NAME}/bawvut:${TAG} -f ./Dockerfile
```

Optionally tag and push to your image registry
```
podman login -u $QUAY_USER -p $QUAY_PWD quay.io

podman push quay.io/${REPO_NAME}/bawvut:${TAG}

podman tag quay.io/${REPO_NAME}/bawvut:${TAG} quay.io/${REPO_NAME}/bawvut:latest
podman push quay.io/${REPO_NAME}/bawvut:latest
```

## Prepare containerized configuration

use '-p 8089:8089' when Locust configuration is set to 'headless = false'

create dedicate folders
```
cd ./virtual-users-locust-sandbox

mkdir -p ../test-configs/{conf1,conf2}
mkdir -p ../test-configs/conf1/outputdata
mkdir -p ../test-configs/conf2/outputdata
```

Example: setup configuration folder to use configuration: baw-vu-cfg-1.conf

copy files to test folder
```
cp ../virtual-users-locust-test-configs/configurations/baw-cp4ba/baw-vu-cfg-1.conf ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/baw-cp4ba/env1.properties ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/users/creds-cfg1.csv ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/users/TS-TEST1.csv ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/users/US-TS-TEST1.csv ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/managers/payloadManager-type1.py ../test-configs/conf1/
cp ../virtual-users-locust-test-configs/configurations/managers/assertsManager-type1.py ../test-configs/conf1/
```

modify paths in **../test-configs/conf1/baw-vu-cfg-1.conf** to poin to to container internal folder **/bawvut/configurations**

example for **../test-configs/conf1/baw-vu-cfg-1.conf**
```
BAW_ENV = /bawvut/configurations/env1.properties 
BAW_USERS = /bawvut/configurations/creds-cfg1.csv 
BAW_TASK_SUBJECTS = /bawvut/configurations/TS-TEST1.csv 
BAW_USER_TASK_SUBJECTS = /bawvut/configurations/US-TS-TEST1.csv 
```

modify paths in **../test-configs/conf1/env1.properties** to poin to to container internal folder **/bawvut/configurations**

example for **../test-configs/conf1/env1.properties**
```
BAW_PAYLOAD_MANAGER=/bawvut/configurations/payloadManager-type1.py
BAW_UNIT_TEST_ASSERTS_MANAGER=/bawvut/configurations/assertsManager-type1.py
BAW_UNIT_TEST_OUT_FILE_NAME=/bawvut/configurations/outputdata/unittest-scenario1.json
BAW_UNIT_TEST_OUT_SQLITEDB_NAME=/bawvut/configurations/outputdata/unittest-scenario1-sqlite.db
```

## Run BAWVUT image

Run container using internal configuration via -v volumes
```
REPO_NAME=marco_antonioni
podman run -it --rm --name bawvut \
    -p 8089:8089 \
    -v ../test-configs/conf1:/bawvut/configurations:Z \
    -v ../test-configs/conf1/outputdata:/bawvut/outputdata:Z \
    -t quay.io/${REPO_NAME}/bawvut:latest locust --config=/bawvut/configurations/baw-vu-cfg-1.conf
```
