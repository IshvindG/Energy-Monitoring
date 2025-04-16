FROM amazon/aws-lambda-python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY newsletter.py .

COPY newsletter.html .

COPY turbines.jpg .

COPY newsletter_pdf.py .

COPY send_email.py .

COPY monthly_email_report.py .

CMD [ "monthly_email_report.lambda_handler" ]