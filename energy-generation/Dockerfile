FROM public.ecr.aws/lambda/python:3.13

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY load.py .

COPY pipeline.py .

CMD [ "pipeline.handler" ]