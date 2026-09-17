release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn stockflow.wsgi --log-file -
