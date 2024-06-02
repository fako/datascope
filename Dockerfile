FROM python:3.11
SHELL ["/bin/bash", "-c"]
ARG UID=1000
ARG GID=1000

RUN apt-get update && \
    apt-get install -y vim binutils libproj-dev gdal-bin gettext default-jdk

# Setup directories and 3rd party models
RUN mkdir -p /usr/etc/datascope
COPY deploy/environments /usr/etc/datascope
RUN mkdir -p /usr/etc/models
COPY models /usr/etc/models
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
# We also add default Python user path to PATH so installed binaries get found
RUN groupadd -r app -g $GID && useradd app -u $UID -r -m -g app
ENV PATH="/home/app/.local/bin:${PATH}"
ENV PYTHONPATH="/usr/src/app"

# We're switching user to a non-priviliged user to prevent attacks
RUN chown app:app /usr/src/app/
USER app:app

# Install Python dependencies and copy app
RUN pip install --user --upgrade pip
COPY src/datascope/requirements /usr/src/app/datascope/requirements
RUN pip install --no-cache-dir --user -r datascope/requirements/production.txt
COPY --chown=app:app src /usr/src/app
RUN mkdir -p /usr/src/app/data

# We setup spaCy models outside of the pip flow to prevent repetious downloads
RUN python -m spacy link /usr/etc/models/spacy/en_core_web_lg-2.3.0/en_core_web_lg en_core_web_lg
RUN python -m spacy link /usr/etc/models/spacy/nl_core_news_sm-2.3.0/nl_core_news_sm nl_core_news_sm

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI
# NB: runs with production settings
RUN python manage.py collectstatic --noinput

# Compiling translations
RUN python manage.py compilemessages

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
