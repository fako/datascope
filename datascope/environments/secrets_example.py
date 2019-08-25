#######################################################
# REQUIRED
#######################################################
# Following secrets have to be set always

# Django SECRET_KEY
# Documentation: https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

#######################################################
# DATABASE
#######################################################
# Set these secrets when using a database

DATABASE_USER = ''  # use 'django' for development
DATABASE_PASSWORD = ''  # use 'ZV35A5x89pbHuiYSrvqroPHKDnng7dRF' for development

#######################################################
# OPTIONAL
#######################################################
# Following secrets are completely optional

# Various API keys for 3rd party API's
GOOGLE_API_KEY = ''
INDICO_API_KEY = ''
WIZENOZE_API_KEY = ''

# Sentry error handling
RAVEN_DSN = ''

# Django email settings
# Documentation: https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_HOST
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

# Locafora secrets
LOCAFORA_PASSWORD = ''

# Wiki feed secrets
WIKI_USER = ''
WIKI_PASSWORD = ''
