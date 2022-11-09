#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "DB not yet run..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "DB did run."
fi
python manage.py flush --no-input
python manage.py migrate

exec "$@"
