# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is used to deploy the website to Heroku
#
# See here for more:
# https://devcenter.heroku.com/articles/procfile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

release: flask db migrate & flask clear-cache
web: gunicorn --worker-class="egg:meinheld#gunicorn_worker" "app.main:create_app()"
worker: flask celery worker
