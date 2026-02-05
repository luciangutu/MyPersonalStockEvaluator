FROM python:3.11-slim

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "Ticker_data.py", "--browser.gatherUsageStats", "false"]
