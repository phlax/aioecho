FROM python:3.8-slim
RUN pip3 install -q aiodocker aiohttp aiohttp_cors pyyaml
RUN mkdir /certs
COPY servercert.pem /certs
COPY serverkey.pem /certs

ENTRYPOINT ["python3", "/code/control/run.py"]
