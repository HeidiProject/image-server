FROM python:3.11-slim
ENV LANG C.UTF-8 -*- 


#
WORKDIR /data/
COPY ./testing/tracking_ids.json /data/tracking_ids.json

# 
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

EXPOSE 8443

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8443"]
