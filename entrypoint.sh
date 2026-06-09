#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py compilemessages -l hu -l ro 2>/dev/null || true
exec "$@"
