#!/bin/sh
set -eu
export MYSQL_PWD="$MYSQL_PASSWORD"
query() { mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" "$MYSQL_DATABASE" -Nse "$1"; }
[ "$(query 'SELECT 1')" = 1 ] || exit 1
if [ "${HEFESTO_BOOTSTRAP:-false}" != true ]; then
  [ "${INITIAL_SETUP_COMPLETE:-false}" = true ] || { echo 'Complete alta privada del propietario'; exit 1; }
  exists=$(query "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='users'")
  [ "$exists" = 1 ] || { echo 'Falta instalacion Ghost'; exit 1; }
  active=$(query "SELECT COUNT(*) FROM users WHERE status='active'")
  [ "$active" -ge 1 ] || { echo 'Falta cuenta activa; completar bootstrap'; exit 1; }
fi
echo 'Preflight completado'
