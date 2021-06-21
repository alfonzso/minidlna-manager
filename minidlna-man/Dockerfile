FROM python:3.9-alpine3.12
WORKDIR /opt/minidlna-man/
RUN PYTHONIOENCODING=UTF-8 pip3 install docker six
ADD main.py .
ADD res res

ENTRYPOINT [ "python3", "/opt/minidlna-man/main.py" ]
