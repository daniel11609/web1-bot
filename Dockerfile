FROM alpine

RUN apk add py-cryptography python3

COPY requirements.txt /

RUN pip3 install -r requirements.txt

COPY src/ /app

WORKDIR /app

ENV schuldestmirbot 1117353580:AAGS4amHBzBbydCX2edeBO2CduvGiABskjs

CMD ["python3", "./main.py"]


