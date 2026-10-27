#!/usr/bin/env python3
"""Respaldo de hefesto-publicaciones (Ghost + MySQL).

Reglas de material sensible:
- El .env nunca se copia en claro: solo env.vars y, si hay receptor age, el
  .env cifrado (env.age).
- El volumen de contenido (adjuntos de las publicaciones) es material personal: viaja cifrado con age o no viaja y el manifiesto lo declara.
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
    try:
        dc("stop", "app")
        dump = ('MYSQL_PWD="$MYSQL_PASSWORD" exec mysqldump -u"$MYSQL_USER" '
                '--single-transaction --no-tablespaces --set-gtid-purged=OFF '
                '--skip-add-drop-table --skip-lock-tables --hex-blob "$MYSQL_DATABASE"')
        with (carpeta / "ghost.sql").open("wb") as out:
            dc("exec", "-T", "db", "sh", "-ec", dump, stdout=out)

        receptor = receptor_age()
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

        meta.update(exportar_env(RAIZ, carpeta))
        if (RAIZ / "compose.yaml").is_file():
            shutil.copy2(RAIZ / "compose.yaml", carpeta / "compose.yaml")

        artefactos = artefactos_presentes(carpeta)
        escribir_manifiesto(carpeta, SOFTWARE, VERSION, DATABASE, artefactos, extra=meta)
    except Exception:
        marcar_fallido(carpeta, SOFTWARE, VERSION, DATABASE)
        raise
    finally:
        dc("start", "app")
    print("Respaldo completo:", carpeta)
    print("El .env no viaja en claro: solo cifrado con age o fuera del respaldo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
