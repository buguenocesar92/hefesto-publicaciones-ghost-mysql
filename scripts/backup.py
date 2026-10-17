#!/usr/bin/env python3
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];os.chdir(root);os.umask(0o077)
def dc(*a,**kw):return subprocess.run(['docker','compose',*a],check=True,**kw)
p=root/'backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');p.mkdir(parents=True,mode=0o700)
running=bool(dc('ps','--status','running','-q','app',capture_output=True,text=True).stdout.strip())
try:
    dc('stop','app')
    dump='MYSQL_PWD="$MYSQL_PASSWORD" exec mysqldump -u"$MYSQL_USER" --single-transaction --no-tablespaces --set-gtid-purged=OFF --skip-add-drop-table --skip-lock-tables --hex-blob "$MYSQL_DATABASE"'
    with (p/'ghost.sql').open('wb') as f:dc('exec','-T','db','sh','-ec',dump,stdout=f)
    with (p/'content.tar.gz').open('wb') as f:dc('run','--rm','--no-deps','-T','--entrypoint','tar','filetools','-czf','-','-C','/restore-content','.',stdout=f)
    shutil.copy2(root/'.env',p/'.env');shutil.copy2(root/'compose.yaml',p/'compose.yaml')
    hashes={}
    for n in ['ghost.sql','content.tar.gz','.env','compose.yaml']:
        with (p/n).open('rb') as f:hashes[n]=hashlib.file_digest(f,'sha256').hexdigest()
    (p/'manifest.json').write_text(json.dumps({'product':'hefesto-publicaciones','version':'6.70.0','status':'completed','sha256':hashes},indent=2))
    print('Respaldo completo:',p,'Contiene secretos; cifrar antes de transferir.')
finally:
    if running:dc('start','app')
