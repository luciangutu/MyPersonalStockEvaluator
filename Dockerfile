FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "Ticker_data.py", "--browser.gatherUsageStats", "false"]

