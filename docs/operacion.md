# Respaldo y restauración
`python3 scripts/backup.py` detiene Ghost, exporta solo la DB ghost y archiva el volumen content; guarda .env, Compose y hashes. Reinicia app si estaba activa. Evite cargas, CLI, otras réplicas y escrituras externas durante la copia. La pausa hace que el sitio quede temporalmente indisponible.

El respaldo conserva imágenes y temas; el exportador JSON de Ghost por sí solo no es equivalente. Cifre la copia antes de trasladarla: contiene secretos, cuentas y contenido. Guarde copias fuera del VPS. Solo manifest completed señala un respaldo completo; hashes detectan daños, no autenticidad. Programe/supervise copias y retención en su servidor: el ZIP no crea tareas programadas.

## Restaurar en destino vacío
1. Prepare directorio/servidor destino con este kit y mismas imágenes. Genere .env con claves NUEVAS de DB, VOLUME_PREFIX nuevo y SMTP_READY=false. App debe permanecer detenida.
2. `docker compose up -d db`; espere estado healthy. No inicie app, porque poblaría DB y content.
3. `python3 scripts/restore.py /ruta/respaldo`. Comprueba hashes, rutas del archivo y que DB y content estén vacíos. No usa root para importar.
4. `docker compose -f compose.yaml -f compose.bootstrap.yaml up -d app`. Pruebe por túnel con las cuentas restauradas, usando Mailpit para correos de ensayo.
5. Revise cualquier configuración de newsletter/Stripe/integraciones guardada en la DB antes de habilitar acceso externo. El override SMTP solo redirige correo transaccional; no neutraliza proveedores de campañas configurados anteriormente.
6. Verifique artículos, páginas, autores, imágenes, temas, permisos y URLs. Configure dominio y correo; pase a producción como indica instalación. Cambie DNS solo tras aceptar el resultado.

No borra ni fusiona destinos. Si falla parcialmente, investigar y preparar otro destino vacío antes de reintentar. No elimine la instalación original. El script acepta archivos y directorios normales, rechaza enlaces simbólicos y tipos especiales; audite temas/adaptadores añadidos antes de respaldar.

Las claves y configuración de integraciones en DB se restauran junto con ella. Conserve también ZIP, dominio/proxy/DNS y cualquier secreto externo fuera del alcance de este kit.

## Actualizaciones
Respaldar, clonar, leer notas upstream y probar migraciones y tema antes de cambiar imágenes. No actualizar mayores de MySQL sobre el volumen original sin plan de migración probado. Revertir imagen Ghost no revierte esquema: recuperar DB+content juntos en destino nuevo.

Supervisar HTTPS, acceso administrativo, espacio de ambos volúmenes, conexiones MySQL y entrega de correo. No se instala monitoreo externo ni se promete alta disponibilidad. Use una réplica hasta diseñar almacenamiento compartido y concurrencia.
