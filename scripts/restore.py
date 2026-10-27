#!/usr/bin/env python3
"""Restauracion de hefesto-publicaciones (Ghost + MySQL) en un destino nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Exige destino vacio, verifica los sha256 del manifiesto y deja
restore-report.json y registro de auditoria.
"""
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (RespaldoError, auditar, descifrar_con_age, ejecutar,
                               ejecutar_check, escribir_informe, opciones_restore)

SOFTWARE = "hefesto-publicaciones"
VERSION = "6.70.0"
DATABASE = "mysql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)
PROHIBIDOS = ["content.tar.gz"]
VOLUMENES = [
    {
        "nombre": "content",
        "artefacto": "content.tar.gz",
        "ruta": "/restore-content"
    }
]


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    origen = Path(origen).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE, prohibidos=PROHIBIDOS)
    if modo == "dry-run":
        print("Simulacion: el respaldo es integro y no se escribio nada.")
        print("Para restaurar de verdad: --confirmar CONFIRMAR_RESTAURACION")
        return 0
    if dc("ps", "--status", "running", "-q", "app",
          capture_output=True, text=True).stdout.strip():
        raise RespaldoError("app esta activa en el destino; detenerla antes de restaurar", 5)
    if not (RAIZ / ".env").is_file():
        raise RespaldoError("Preparar el .env del destino: no viaja en el respaldo", 5)
    count = dc("exec", "-T", "db", "sh", "-ec",
               'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE" '
               '-Nse "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()"',
               capture_output=True, text=True).stdout.strip()
    if count != "0":
        raise RespaldoError("La base del destino no esta vacia; no se sobrescribe", 5)
    for vol in VOLUMENES:
        encontrado = dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "find",
                        "filetools", vol["ruta"], "-mindepth", "1", "-maxdepth", "1",
                        capture_output=True, text=True).stdout.strip()
        if encontrado:
            raise RespaldoError("El volumen " + vol["nombre"] +
                                " del destino no esta vacio; usar destino nuevo", 5)

    with (origen / "ghost.sql").open("rb") as f:
        dc("exec", "-T", "db", "sh", "-ec",
           'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE"', stdin=f)
    for vol in VOLUMENES:
        cifrado = origen / (vol["artefacto"] + ".age")
        if not cifrado.is_file():
            raise RespaldoError("El respaldo no trae " + vol["artefacto"] +
                                " cifrado: hace falta el receptor age", 5)
        with tempfile.TemporaryDirectory(prefix="hefesto-restore-") as d:
            plano = Path(d) / vol["artefacto"]
            descifrar_con_age(cifrado, plano)
            with tarfile.open(plano) as tf:
                for member in tf:
                    ruta = PurePosixPath(member.name)
                    if (ruta.is_absolute() or ".." in ruta.parts
                            or not (member.isfile() or member.isdir())):
                        raise RespaldoError("Ruta o tipo no admitido: " + member.name, 5)
            with plano.open("rb") as f:
                dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar", "filetools",
                   "-xzf", "-", "-C", vol["ruta"], stdin=f)

    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="restaurado", destino=str(RAIZ))
    auditar(RAIZ, operacion="restore", kit=SOFTWARE, origen=str(origen), destino=str(RAIZ),
            resultado="restaurado")
    print("Restaurado. Iniciar la aplicacion y ejecutar la aceptacion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
