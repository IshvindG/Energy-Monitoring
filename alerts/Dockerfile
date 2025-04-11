FROM amazon/aws-lambda-python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY postcode_lookup.py .

COPY send_alerts.py .

CMD [ "send_alerts.lambda_handler" ]