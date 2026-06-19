web: gunicorn crm_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
release: python manage.py migrate --run-syncdb
