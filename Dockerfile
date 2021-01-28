FROM python:3.9-slim
WORKDIR /app
RUN apt-get -q update \
  && apt-get -qy install mkvtoolnix ffmpeg imagemagick ghostscript
COPY docker/policy.xml /etc/ImageMagick-6/policy.xml
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
RUN pip install -e .
