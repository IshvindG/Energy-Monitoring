FROM amazon/aws-lambda-python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY subscribe_lambda.py .

CMD [ "subscribe_lambda.lambda_handler" ]