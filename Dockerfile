FROM python:3.6

RUN apt-get update && \
    apt-get install -y vim binutils libproj-dev gdal-bin gettext

# Setup directories, 3rd party models and users
RUN mkdir -p /usr/etc/datascope
COPY deploy/environments /usr/etc/datascope
RUN mkdir -p /usr/etc/models
COPY models /usr/etc/models
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN useradd -ms /bin/bash app

# Install Python dependencies and copy app
RUN pip install --upgrade pip
COPY src/datascope/requirements /usr/src/app/datascope/requirements
RUN pip install --no-cache-dir -r datascope/requirements/production.txt
COPY --chown=app:app src /usr/src/app

# We setup spaCy models outside of the pip flow to prevent repetious downloads
RUN python -m spacy link /usr/etc/models/spacy/en_core_web_lg-2.0.0/en_core_web_lg en_core_web_lg
RUN python -m spacy link /usr/etc/models/spacy/nl_core_news_sm-2.0.0/nl_core_news_sm nl_core_news_sm

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI
# NB: runs with production settings
RUN python manage.py collectstatic --noinput

# We're switching user to a non-priviliged user
# The Python packages directory and datagrowth package needs to belong to that user
# for dynamic packaging (see entrypoint)
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
