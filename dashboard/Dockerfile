FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pages/ ./pages/

COPY utils/ ./utils/

COPY assets/ ./assets/

COPY Home.py .

EXPOSE 8501

CMD [ "streamlit", "run", "Home.py"]