FROM alpine:latest

# No clue what this does
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache python3~=3.12
WORKDIR /app
COPY . .
CMD ["python3", "bardak.py"]

