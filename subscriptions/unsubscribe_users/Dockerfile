FROM amazon/aws-lambda-python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY unsubscribe_lambda.py .

CMD [ "unsubscribe_lambda.lambda_handler" ]