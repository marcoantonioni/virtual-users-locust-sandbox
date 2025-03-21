# BAW Virtual Users Tool in Docker image

# FROM registry.redhat.io/rhel8/python-38:latest
FROM registry.redhat.io/ubi9/python-312:9.5-1742197730

#ENV BAWVUT_USER=1001
ENV BAWVUT_USER=root
EXPOSE 8089

RUN pip install locust \
    && pip install jproperties \
    && pip install jsonpath-ng \
    && pip install sqlite-utils \
    && pip install warlock

USER root
RUN dnf install -y iputils telnet \
    && dnf clean all

RUN mkdir -p /bawvut/{bawsys,configurations,outputdata}
WORKDIR /bawvut
ADD ./bawsys/*.py /bawvut/bawsys/
ADD ./bawsys/*.yp /bawvut/bawsys/
ADD ./*.py /bawvut/
#RUN chown -R ${BAWVUT_USER}:root /bawvut
RUN echo "echo -e '\nUsage:\nlocust --config=path-to-cfg-file\n'" > /bawvut/usage.sh \
    && chmod a+x /bawvut/usage.sh

#USER ${BAWVUT_USER}
CMD ["/bawvut/usage.sh"]
