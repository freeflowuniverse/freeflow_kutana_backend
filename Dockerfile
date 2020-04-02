FROM python:3.8-alpine
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers make libffi-dev
COPY requirements.txt requirements.txt
COPY /config/freeflow_config.py /opt/freeflow/config/freeflow_config.py 
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]