FROM python:latest
SHELL ["/bin/bash", "-c"]
WORKDIR /opt/app-root/src/
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "startprocessing.py"]