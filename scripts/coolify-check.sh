#!/usr/bin/env bash
# Verifica que el compose del kit cumple el contrato de Coolify (MVP Hefesto):
#   1. Servicios sin `profiles` no exponen puertos ni poder sobre el host.
#   2. Nombres estables sin forzar (sin `name:` fijo a nivel raíz ni en
#      volúmenes o redes).
#
# El contrato completo y los motivos de cada regla viven en la sección
# «Despliegue en Coolify (MVP Hefesto)» del README; este script es solo el
# guardián automatizable.
#
# jq no distingue los `name:` declarados en el fuente de los que Docker
# Compose auto-asigna a partir del nombre del proyecto, así que el chequeo de
# punto 2 se hace contra el YAML fuente con PyYAML; el chequeo de punto 1 va
# contra el JSON normalizado de `docker compose config`.
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE_FILE="compose.yaml"
TMP_ENV="$(mktemp)"
trap 'rm -f "$TMP_ENV"' EXIT

# ---------------------------------------------------------------------------
# 1. Extraer todas las variables referenciadas en el compose y rellenar un
#    .env ficticio no secreto. Las de host/URL van con https://ejemplo.invalid.
# ---------------------------------------------------------------------------
vars=$(grep -oE '\$\{[A-Z_][A-Z0-9_]*(:[-?][^}]*)?\}' "$COMPOSE_FILE" \
  | sed -E 's/^\$\{([A-Z_][A-Z0-9_]*).*$/\1/' \
  | sort -u)

declare -A VALUES=()
for v in $vars; do
  case "$v" in
    MYSQL_ROOT_PASSWORD|MYSQL_PASSWORD|SMTP_USERNAME|SMTP_PASSWORD)
      VALUES[$v]="x1234567890abcdef1234567890abcdef" ;;
    PUBLIC_URL|MAIL_FROM|SMTP_HOST)
      VALUES[$v]="https://ejemplo.invalid" ;;
    SMTP_READY|INITIAL_SETUP_COMPLETE)
      VALUES[$v]="false" ;;
    *)
      VALUES[$v]="x1234567890abcdef" ;;
  esac
done

{
  for v in $vars; do
    echo "$v=${VALUES[$v]}"
  done
} > "$TMP_ENV"

# ---------------------------------------------------------------------------
# 2. Renderizar el compose con el .env ficticio (JSON normalizado).
# ---------------------------------------------------------------------------
RENDER=$(docker compose \
    --project-directory . \
    -f "$COMPOSE_FILE" \
    --env-file "$TMP_ENV" \
    config --format json 2>/dev/null) || {
  docker compose \
    --project-directory . \
    -f "$COMPOSE_FILE" \
    --env-file "$TMP_ENV" \
    config --format json >&2 || true
  echo "$COMPOSE_FILE: error de render con .env ficticio"
  exit 1
}

FAIL=0
report() { echo "$1"; FAIL=1; }

# ---------------------------------------------------------------------------
# 3.a) Sin `name:` fijo a nivel raíz. Docker Compose siempre rellena `name`
# en el JSON normalizado con el nombre del directorio del proyecto, así que
# se valida contra el YAML fuente.
# ---------------------------------------------------------------------------
ROOT_NAME=$(python3 - "$COMPOSE_FILE" <<'PY'
import sys, yaml
src = sys.argv[1]
with open(src) as f:
    doc = yaml.safe_load(f) or {}
print(doc.get("name") or "")
PY
)
if [ -n "$ROOT_NAME" ]; then
  report "compose: nombre fijo a nivel raiz ($ROOT_NAME); Coolify pone el del proyecto"
fi

# ---------------------------------------------------------------------------
# 3.b) y 3.c) Sin `name:` fijo en volúmenes ni redes. Se valida contra el YAML
# fuente porque el JSON normalizado siempre rellena `name:` con el patrón
# "<project>_<key>" y no se puede distinguir del declarado.
# ---------------------------------------------------------------------------
NAMES_BAD=$(python3 - "$COMPOSE_FILE" <<'PY'
import sys, yaml, re
src = sys.argv[1]
with open(src) as f:
    doc = yaml.safe_load(f) or {}
violations = []
# Los volumenes pueden fijar `name:` si parametrizan con ${VOLUME_PREFIX}
# (con valor por defecto) para no cambiar el nombre real entre despliegues.
for key, val in (doc.get("volumes") or {}).items():
    if isinstance(val, dict) and val.get("name"):
        name_val = str(val["name"])
        if not re.search(r"\$\{VOLUME_PREFIX", name_val):
            violations.append(f"volumen {key}:{name_val}")
for key, val in (doc.get("networks") or {}).items():
    if isinstance(val, dict) and val.get("name"):
        violations.append(f"red {key}:{val['name']}")
print("\n".join(violations))
PY
)
if [ -n "$NAMES_BAD" ]; then
  while IFS= read -r line; do
    report "compose: nombre fijo -> $line"
  done <<< "$NAMES_BAD"
fi

# ---------------------------------------------------------------------------
# 3.e) Binds sospechosos: rutas absolutas o docker.sock declaradas en el
# fuente. Docker Compose normaliza los paths relativos a absolutos durante
# `config`, así que este chequeo se hace contra el YAML fuente.
# ---------------------------------------------------------------------------
BIND_BAD=$(python3 - "$COMPOSE_FILE" <<'PY'
import sys, yaml, re
from pathlib import PurePosixPath
src = sys.argv[1]
with open(src) as f:
    doc = yaml.safe_load(f) or {}
bad = []
for svc, conf in (doc.get("services") or {}).items():
    if (conf.get("profiles") or []):
        continue
    for vol in conf.get("volumes") or []:
        if isinstance(vol, str):
            src_path = vol.split(":", 1)[0]
        elif isinstance(vol, dict) and vol.get("type") in (None, "bind"):
            src_path = vol.get("source", "")
        else:
            continue
        if not src_path:
            continue
        if (src_path.startswith("/") or src_path.startswith("~")
                or "docker.sock" in src_path
                or ".." in PurePosixPath(src_path).parts):
            bad.append(f"{svc}:bind fuera del repo -> {src_path}")
print("\n".join(bad))
PY
)
if [ -n "$BIND_BAD" ]; then
  while IFS= read -r line; do
    report "compose: $line"
  done <<< "$BIND_BAD"
fi

# ---------------------------------------------------------------------------
# 3.d) Por cada servicio sin `profiles`, validar el contrato del punto 1.
# Tras `to_entries[]` el flujo expone `{key, value}`; cada campo del servicio
# se accede con `.value.<campo>` para no leer el envoltorio. Se acumulan las
# coincidencias en un array y se emite "servicio:campo1,campo2" si hay alguna.
# ---------------------------------------------------------------------------
SERV_BAD=$(echo "$RENDER" | jq -r '
  .services // {}
  | to_entries[]
  | select((.value.profiles // []) | length == 0)
  | .key as $svc
  | [
      (if .value.ports                       != null then "ports"                       else empty end),
      (if .value.container_name              != null then "container_name"              else empty end),
      (if .value.privileged                  == true then "privileged"                  else empty end),
      (if .value.cap_add                     != null then "cap_add"                     else empty end),
      (if .value.devices                     != null then "devices"                     else empty end),
      (if .value.network_mode                == "host" then "network_mode:host"          else empty end),
      (if .value.pid                         == "host" then "pid:host"                   else empty end),
      (if .value.ipc                         == "host" then "ipc:host"                   else empty end),
      (if (.value.security_opt // []) | any(.[]; test("unconfined")) then "security_opt:unconfined" else empty end)
    ] as $bad
  | select(($bad | length) > 0)
  | "\($svc): \($bad | join(","))"
')
if [ -n "$SERV_BAD" ]; then
  while IFS= read -r line; do
    report "compose: $line"
  done <<< "$SERV_BAD"
fi

if [ $FAIL -ne 0 ]; then
  exit 1
fi

echo "Contrato Coolify OK: $COMPOSE_FILE cumple los puntos 1 y 2"