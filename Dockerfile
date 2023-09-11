# base image
FROM nikolaik/python-nodejs:latest

WORKDIR /app
COPY ./ /app

# install and cache app dependencies
RUN npm install

# build app for production w/ minification
RUN npm run build
RUN pip install -r requirements.txt

# start app
EXPOSE 8000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]