FROM python:3.6
WORKDIR /app
RUN wget -q -O - https://mkvtoolnix.download/gpg-pub-moritzbunkus.txt | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add - \
  && echo deb https://mkvtoolnix.download/debian/ buster main > /etc/apt/sources.list.d/mkvtoolnix.list \
  && apt-get -q update \
  && apt-get -qy install mkvtoolnix ffmpeg imagemagick ghostscript
COPY docker/policy.xml /etc/ImageMagick-6/policy.xml
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
