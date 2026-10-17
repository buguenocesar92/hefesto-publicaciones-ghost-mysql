#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys,tarfile
from pathlib import Path,PurePosixPath
root=Path(__file__).resolve().parents[1];os.chdir(root)
if len(sys.argv)!=2:raise SystemExit('Uso: python3 scripts/restore.py /ruta/respaldo')
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
if m.get('product')!='hefesto-publicaciones' or m.get('version')!='6.70.0' or m.get('status')!='completed':raise SystemExit('Manifest invalido')
for name in ['ghost.sql','content.tar.gz']:
    with (p/name).open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=m['sha256'][name]:raise SystemExit('Hash incorrecto')
with tarfile.open(p/'content.tar.gz') as tf:
    seen=set()
    for member in tf:
        path=PurePosixPath(member.name)
        if path.is_absolute() or '..' in path.parts or not(member.isfile() or member.isdir()) or str(path) in seen:raise SystemExit('Ruta/tipo no admitido')
        seen.add(str(path))
def dc(*a,**kw):return subprocess.run(['docker','compose',*a],check=True,**kw)
if dc('ps','--status','running','-q','app',capture_output=True,text=True).stdout.strip():raise SystemExit('Detener app antes de restaurar')
count_cmd='MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE" -Nse "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()"'
count=dc('exec','-T','db','sh','-ec',count_cmd,capture_output=True,text=True).stdout.strip()
if count!='0':raise SystemExit('La base no esta vacia; no se sobrescribe')
found=dc('run','--rm','--no-deps','-T','--entrypoint','find','filetools','/restore-content','-mindepth','1','-maxdepth','1',capture_output=True,text=True).stdout.strip()
if found:raise SystemExit('Volumen content no vacio; no se sobrescribe')
with (p/'ghost.sql').open('rb') as f:dc('exec','-T','db','sh','-ec','MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u"$MYSQL_USER" "$MYSQL_DATABASE"',stdin=f)
with (p/'content.tar.gz').open('rb') as f:dc('run','--rm','--no-deps','-T','--entrypoint','tar','filetools','-xzf','-','-C','/restore-content',stdin=f)
print('Base y contenido restaurados. Probar con bootstrap/Mailpit antes de activar correo real.')
