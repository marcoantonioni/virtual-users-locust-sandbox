#/bin/bash

#==================================================
# Deploy BAWVUT
#==================================================

if [[ "$TNS" == "" ]]; then
    TNS="bawvut"
fi
if [[ "$BAWVUT_IMAGE" == "" ]]; then
    BAWVUT_IMAGE="quay.io/marco_antonioni/bawvut"
fi
if [[ "$BAWVUT_NAME" == "" ]]; then
    BAWVUT_NAME="bawvut"
fi
if [[ "$BAWVUT_REPLICAS" == "" ]]; then
    BAWVUT_REPLICAS=1
fi
if [[ "$BAWVUT_OUTPUT_FOLDER" == "" ]]; then
    BAWVUT_OUTPUT_FOLDER="./outputdata"
fi
if [[ "$BAWVUT_CONFIG_FILE_NAME" == "" ]]; then
    BAWVUT_CONFIG_FILE_NAME="bawvut.conf"
fi


createNS () {
    ns_status=$(oc get ns ${TNS} -o json | jq .status.phase -r)
    if [[ $ns_status == "Active" ]];
    then
        echo "Namespace ["${TNS}"] exists"
    else
        oc new-project ${TNS}
    fi
}

deployBAWVUT () {

echo "
kind: Deployment
apiVersion: apps/v1
metadata:
  namespace: ${TNS}
  name: ${BAWVUT_NAME}
  labels:
    app: ${BAWVUT_NAME}
spec:
  replicas: ${BAWVUT_REPLICAS}
  selector:
    matchLabels:
      app: ${BAWVUT_NAME}
  template:
    metadata:
      labels:
        app: ${BAWVUT_NAME}
    spec:
      containers:
        - resources: {}
          name: ${BAWVUT_NAME}
          env:
            - name: BAWVUT_OUTPUT_FOLDER
              value: \"${BAWVUT_OUTPUT_FOLDER}\"
          imagePullPolicy: Always
          image: >-
            ${BAWVUT_IMAGE}
          command: [ \"/bin/bash\", \"-c\", \"locust --config=/bawvut/configurations/${BAWVUT_CONFIG_FILE_NAME} && echo 'BAWVUT terminated.' && sleep infinity\" ]
          securityContext:
            capabilities:
              drop: ["ALL"]
            seccompProfile:
              type: RuntimeDefault
            runAsNonRoot: true
            allowPrivilegeEscalation: false
          volumeMounts:
            - name: configurations
              mountPath: /bawvut/configurations
            - name: outputdata
              mountPath: /bawvut/outputdata
      restartPolicy: Always
      dnsPolicy: ClusterFirst
      volumes:
        - name: configurations
          configMap:
            name: bawvut-configurations
        - name: outputdata
          emptyDir: {}

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  revisionHistoryLimit: 10
  progressDeadlineSeconds: 600
" | oc apply --force -f -

}

#----------------------------------
createNS
deployBAWVUT
