FROM public.ecr.aws/lambda/python:3.11

RUN yum install -y postgresql-devel gcc python3-devel

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["main.lambda_handler"]