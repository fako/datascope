# DATASCOPE_VERSION gets prepended during deploy
#######################################################
# Digital Ocean
#######################################################

# Required variables needed to complete setup
PATH_TO_PROJECT = '/srv/artefacts/datascope/{}/src/'.format(DATASCOPE_VERSION)
URL_TO_PROJECT = '/'

# Optional variables that control features of an installation
USE_WEBSOCKETS = False
