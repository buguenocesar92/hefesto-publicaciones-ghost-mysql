#!/bin/sh
set -eu
cd /var/lib/ghost
if [ "${HEFESTO_BOOTSTRAP:-false}" != true ]; then
  [ "${SMTP_READY:-false}" = true ] || { echo 'Configurar y confirmar SMTP real'; exit 1; }
  case "$url" in https://*) ;; *) echo 'Produccion requiere HTTPS'; exit 1;; esac
  case "$mail__options__host" in mailpit|smtp.example.com|'') echo 'Falta servidor SMTP real'; exit 1;; esac
fi
exec /usr/local/bin/docker-entrypoint.sh node current/index.js
