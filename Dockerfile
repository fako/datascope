FROM python:3.6

RUN apt-get update && \
    apt-get install -y vim binutils libproj-dev gdal-bin gettext

# Setup directories and users
RUN mkdir -p /usr/etc/datascope
COPY deploy/environments /usr/etc/datascope
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN useradd -ms /bin/bash app

# Install Python dependencies and copy app
RUN pip install --upgrade pip
COPY src/datascope/requirements /usr/src/app/datascope/requirements
RUN pip install --no-cache-dir -r datascope/requirements/production.txt
COPY --chown=app:app src /usr/src/app

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI
# NB: runs with production settings
RUN python manage.py collectstatic --noinput

# We're switching user to a non-priviliged user
# The Python packages directory needs to belong to that user for dynamic packaging (see entrypoint)
RUN chown app:app /usr/local/lib/python3.6/site-packages
RUN chown -R app:app /usr/local/lib/python3.6/site-packages/datagrowth*
USER app:app

# Compiling translations
# NB: runs with production settings
# NB: not enabled
# RUN python manage.py compilemessages

# Entrypoint handles some edge cases before running
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
