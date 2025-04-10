FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    wget \
    unzip \
    fonts-liberation \
    libnss3 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV CHROME_BIN=/usr/bin/chromium


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY extract_power_outage1.py .
COPY clean_power_outage1.py .
COPY load_power_outage.py .
COPY run_etl.sh .

RUN chmod +x run_etl.sh

CMD ["/bin/bash", "run_etl.sh"]