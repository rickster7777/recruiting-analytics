FROM ubuntu:18.04

MAINTAINER Sachinj@trinesis.com

# Install required packages and remove the apt packages cache when done.

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git \
	nano \
	python3-dev \
	python3-pip\
	python3-setuptools \
	python-smbus \
	build-essential \
    apt-utils \
	libreadline-gplv2-dev \
	libncursesw5-dev \
	libgdbm-dev \
	libc6-dev \ 
	libbz2-dev \
	zlib1g-dev \	
	libssl-dev \
	openssl \
	libffi-dev \
	nginx \
	supervisor \
	libmysqlclient-dev \
	libpq-dev \
	wget \
	tk-dev \
  	&& rm -rf /var/lib/apt/lists/*
	  
RUN wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
RUN tar xzf Python-3.7.0.tgz
RUN rm -f Python-3.7.0.tgz


RUN cd Python-3.7.0 && ./configure --enable-optimizations && make altinstall


RUN pip3.7 install --upgrade pip
RUN pip install uwsgi

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y curl
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
RUN dpkg -i /chrome.deb || apt-get install -yf
RUN rm /chrome.deb

# Install chromedriver for Selenium
# RUN version=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
# RUN curl https://chromedriver.storage.googleapis.com/${version}/chromedriver_linux64.zip -o /usr/local/bin/chromedriver
# RUN chmod +x /usr/local/bin/chromedriver

# RUN /usr/local/bin/chromedriver --version
# ARG test=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
# RUN echo "this is $test"
# ARG version=$test
# RUN echo "$version"
RUN wget "http://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip"
RUN apt-get update && apt-get install -y unzip
RUN unzip chromedriver* -d /usr/bin/
# RUN cd /usr/local/bin/ && pwd && ls
# RUN chmod +x chromedriver
# COPY chromedriver /usr/local/bin/chromedriver
# COPY chromedriver /usr/bin/chromedriver

# Install Selenium
RUN pip install selenium

# Setup all the config files

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-app.conf /etc/nginx/sites-available/default
COPY supervisor-app.conf /etc/supervisor/conf.d/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of our code, this will cause Docker's caching mechanism
# to prevent re-installinig (all our) dependencies when we made a change in a line or two in our app.

COPY requirements.txt /home/ra/

RUN pip install -r /home/ra/requirements.txt

ARG build_environment=PROD

RUN  echo "Build Envirment is: $build_environment"

ENV RA_APIS_ENVIRON=$build_environment


COPY . /home/ra/

# Adding configuration file inside settings directory
ADD ./config_ra.py /home/ra/ra/ra/settings/

ADD ./certs/www.recruiting-analytics.com.crt /home/ra/certs/
ADD ./certs/www.recruiting-analytics.com.key /home/ra/certs/

VOLUME /var/log/supervisor/

EXPOSE 80
EXPOSE 443

CMD ["supervisord", "-n"]
