# OPTIONAL — only if you already have Docker installed.
# Runs the vulnerable "victim server" as a separate container so your attack
# clearly goes host -> container.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY templates ./templates
COPY loot ./loot
ENV HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]
