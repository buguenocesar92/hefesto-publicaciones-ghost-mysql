#!/bin/sh
set -eu
cd /var/lib/ghost
if [ "${HEFESTO_BOOTSTRAP:-false}" != true ]; then
  case "$url" in
    https://*) ;;
    *) echo 'Produccion requiere HTTPS'; exit 1;;
  esac
  if [ "${SMTP_READY:-false}" = true ]; then
    case "$mail__options__host" in mailpit|smtp.example.com|'') echo 'Falta servidor SMTP real'; exit 1;; esac
  else
    # Sin SMTP: el transporte stub acepta el envío en null:// sin entregar nada.
    unset mail__options__host mail__options__port mail__options__secure mail__options__auth__user mail__options__auth__pass 2>/dev/null || true
    export mail__transport=stub
  fi
fi
exec /usr/local/bin/docker-entrypoint.sh node current/index.js
