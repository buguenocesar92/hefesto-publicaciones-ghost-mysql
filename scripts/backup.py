#!/usr/bin/env python3
"""Respaldo de hefesto-publicaciones (Ghost + MySQL).

Reglas de material sensible:
- El .env nunca se copia en claro: solo env.vars y, si hay receptor age, el
  .env cifrado (env.age).
- El dump de la base (cuentas, correos y hashes de contrasena) y el volumen de
  contenido (adjuntos de las publicaciones) son material personal: viajan
  cifrados con age o no viajan, y el manifiesto declara cada exclusion.
  Los permisos restrictivos no son cifrado: no hay dump en claro en disco.
Ver docs/CONTRATO-RESPALDO.md.
"""
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (RespaldoError, artefactos_presentes, cifrar_con_age,
                               escribir_manifiesto, ejecutar, exportar_env,
                               marcar_fallido, receptor_age)

SOFTWARE = "hefesto-publicaciones"
VERSION = "6.70.0"
DATABASE = "mysql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    if not (RAIZ / ".env").is_file():
        raise RespaldoError("Falta .env: el respaldo necesita el entorno del kit", 5)
    if not dc("ps", "--status", "running", "-q", "app",
              capture_output=True, text=True).stdout.strip():
        raise RespaldoError("app no esta activa en este contexto Compose; "
                            "revisar recurso y proyecto.", 5)
    carpeta = (RAIZ / "backups" /
               datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    carpeta.mkdir(parents=True, mode=0o700)
    meta = {}
    excluidos = []
    try:
        try:
            dc("stop", "app")
            receptor = receptor_age()
            if receptor:
                dump = ('MYSQL_PWD="$MYSQL_PASSWORD" exec mysqldump -u"$MYSQL_USER" '
                        '--single-transaction --no-tablespaces --set-gtid-purged=OFF '
                        '--skip-add-drop-table --skip-lock-tables --hex-blob "$MYSQL_DATABASE"')
                # El dump va del productor a age: nunca toca el disco en claro.
                cifrar_con_age(
                    lambda flujo: dc("exec", "-T", "db", "sh", "-ec", dump, stdout=flujo),
                    carpeta / "ghost.sql.age", receptor)
                meta["dump"] = "ghost.sql.age (cifrado con age)"
            else:
                meta["dump"] = ("excluido: el dump contiene cuentas, correos y hashes de "
                                "contrasena y no hay receptor age configurado")
                excluidos.append("dump")

            if receptor:
                cifrar_con_age(
                    lambda flujo: dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar",
                                     "filetools", "-czf", "-", "-C", "/restore-content", ".",
                                     stdout=flujo),
                    carpeta / "content.tar.gz.age", receptor)
                meta["content"] = "content.tar.gz.age (cifrado con age)"
            else:
                meta["content"] = ("excluido: el volumen de contenido contiene material personal "
                                    "y no hay receptor age configurado")
                excluidos.append("content")

            meta.update(exportar_env(RAIZ, carpeta))
            if (RAIZ / "compose.yaml").is_file():
                shutil.copy2(RAIZ / "compose.yaml", carpeta / "compose.yaml")
        finally:
            dc("start", "app")
        meta["excluidos"] = sorted(excluidos)
        artefactos = artefactos_presentes(carpeta)
        escribir_manifiesto(carpeta, SOFTWARE, VERSION, DATABASE, artefactos, extra=meta)
    except Exception:
        marcar_fallido(carpeta, SOFTWARE, VERSION, DATABASE)
        raise
    print("Respaldo completo:", carpeta)
    if excluidos:
        print("ATENCION: el respaldo NO incluye " + ", ".join(excluidos) +
              ": no es una copia de la base ni de los adjuntos. "
              "Configura AGE_RECIPIENT (o SOPS_AGE_RECIPIENT) para respaldarlos.")
    else:
        print("El .env, el dump y los adjuntos no viajan en claro: todo cifrado con age.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
