FROM ubuntu:trusty

# Basic package setup
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3.4 \
    python3-pip \
    python3-psycopg2

# Make python point to python3
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

RUN mkdir /srv/kubeshark
WORKDIR /srv/kubeshark
ADD requirements /srv/kubeshark/requirements
RUN pip3 install -r requirements/test.txt
ADD kubeshark /srv/kubeshark/
RUN python3 manage.py collectstatic --noinput

COPY apache.vhost /etc/apache2/sites-available/000-kubeshark.conf
RUN a2enmod wsgi && a2ensite 000-kubeshark && a2dissite 000-default

# Set up the load balancer's "health PING"
RUN echo 'OK, thanks' > /var/www/html/health.html

# Go
EXPOSE 80
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
