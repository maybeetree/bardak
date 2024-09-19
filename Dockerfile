FROM alpine:latest

RUN apk add --no-cache python3~=3.12
WORKDIR /app
COPY . .
CMD ["python3", "bardak.py"]

