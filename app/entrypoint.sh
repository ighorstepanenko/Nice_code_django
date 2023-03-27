#!/bin/sh

if [ "$POSTGRES_DB" = "nicecode" ]
then
    # если база еще не запущена
    echo "DB not yet run..."

    # Проверяем доступность хоста и порта
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "DB did run."
fi
# Удаляем все старые данные
python3 manage.py flush --no-input
# Выполняем миграции
python3 manage.py makemigrations
python3 manage.py migrate

exec "$@"
