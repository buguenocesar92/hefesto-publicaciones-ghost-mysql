#!/usr/bin/env python3
"""Restauracion de hefesto-publicaciones (Ghost + MySQL) en un destino nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Exige destino vacio, verifica los sha256 del manifiesto y deja
restore-report.json y registro de auditoria.

El preflight completo (volumenes presentes, descifrado, tar valido, destino
vacio) se ejecuta ANTES de tocar la base o los volumenes: un preflight que
falla no deja la base a medias.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (RespaldoError, auditoria_restore, descifrar_con_age, ejecutar,
                               ejecutar_check, escribir_informe, opciones_restore, validar_tar)

SOFTWARE = "hefesto-publicaciones"
VERSION = "6.70.0"
DATABASE = "mysql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)
PROHIBIDOS = ["content.tar.gz", "ghost.sql"]
ESPERADOS = ("env.vars", "ghost.sql.age", "content.tar.gz.age")
EXCLUIBLES = {"dump": "ghost.sql.age", "content": "content.tar.gz.age"}


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    origen = Path(origen).resolve()
    manifiesto = ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE,
                                esperados=ESPERADOS, prohibidos=PROHIBIDOS,
                                requeridos=("env.vars",), excluibles=EXCLUIBLES)
    if modo == "dry-run":
        print("Simulacion: checksums integros; no demuestra descifrado ni recuperacion.")
        return 0
    with auditoria_restore(RAIZ, origen, manifiesto):
        return restaurar(origen)


def restaurar(origen):
    dump_cifrado = origen / "ghost.sql.age"
    if not dump_cifrado.is_file():
        raise RespaldoError("El respaldo no trae ghost.sql.age; no se restaura", 5)
    cifrado = origen / "content.tar.gz.age"
    if not cifrado.is_file():
        raise RespaldoError("El respaldo no trae content.tar.gz.age; no se restaura", 5)
    # Preflight completo antes de cualquier mutacion: descifrar y validar el
    # tar, y comprobar el destino. Ninguna importacion de SQL ocurre antes.
    with tempfile.TemporaryDirectory(prefix="hefesto-restore-") as d:
        dump_plano = Path(d) / "ghost.sql"
        descifrar_con_age(dump_cifrado, dump_plano)
        plano = Path(d) / "content.tar.gz"
        descifrar_con_age(cifrado, plano)
        validar_tar(plano)
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
        encontrado = dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "find",
                        "filetools", "/restore-content", "-mindepth", "1", "-maxdepth", "1",
                        capture_output=True, text=True).stdout.strip()
        if encontrado:
            raise RespaldoError("El volumen content del destino no esta vacio", 5)
        with dump_plano.open("rb") as f:
            dc("exec", "-T", "db", "sh", "-ec",
               'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE"', stdin=f)
        with plano.open("rb") as f:
            dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar", "filetools",
               "-xzf", "-", "-C", "/restore-content", stdin=f)
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="restaurado", destino=str(RAIZ))
    print("Restaurado. Iniciar la aplicacion y ejecutar la aceptacion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
