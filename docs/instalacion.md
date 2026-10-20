# Instalación y Coolify
1. Ejecute `python3 scripts/configure.py`. Crea .env 0600 con claves distintas de MySQL root y aplicación. Configure PUBLIC_URL y VOLUME_PREFIX. No comparta .env ni salida de Compose con secretos.
2. `docker compose -f compose.yaml -f compose.bootstrap.yaml config --quiet`
3. `docker compose -f compose.yaml -f compose.bootstrap.yaml up -d app`. MySQL inicializa ghost y ghost_app en un volumen nuevo; preflight espera conexión. Ghost ejecuta sus migraciones al arrancar.
4. Desde su equipo: `ssh -L 8099:127.0.0.1:8099 -L 8027:127.0.0.1:8027 usuario@servidor`.
5. Abra http://localhost:8099/ghost y complete el alta del propietario con un correo bajo su control. Si recibe verificación/recuperación, léala en http://localhost:8027 (Mailpit). Los mensajes no salen a Internet por este servicio.
6. Configure título, idioma disponible, autores, tema y páginas. Verifique guardar/publicar una entrada de ensayo y subir una imagen. Confirme que la cuenta propietaria está activa.
7. Configure PUBLIC_URL HTTPS, MAIL_FROM, SMTP_HOST, SMTP_USERNAME y SMTP_PASSWORD con un proveedor real de puerto 465/TLS implícito. Marque SMTP_READY=true e INITIAL_SETUP_COMPLETE=true una vez configurados. Los flags no verifican entrega por sí solos.
8. `docker compose up -d --force-recreate app` SIN override. Asigne HTTPS en Coolify al servicio app, puerto interno 2368. Pruebe acceso y recuperación de contraseña antes de entregar.
9. Retire Mailpit con `docker compose -f compose.yaml -f compose.bootstrap.yaml rm -sf mailpit`. Sus mensajes de prueba se eliminan. Confirme que puertos 8099 y 8027 ya no estén publicados.

## Coolify
Importe el directorio completo desde repositorio privado o servidor, monte ops y conserve variables y nombres de volumen (`VOLUME_PREFIX`). Si re-despliega con un `VOLUME_PREFIX` distinto, Compose creará volúmenes con otro nombre y los datos previos quedarán huérfanos. Use el mismo nombre Compose (o `-p <proyecto>` igual al de Coolify) en bootstrap y producción. Mantenga backend interno para MySQL y conecte el proxy a frontend de app. No publique 3306. El proxy debe enviar X-Forwarded-Proto=https y preservar Host/X-Forwarded-Host.

MySQL y Ghost hablan por red privada Docker del mismo servidor; este kit no configura TLS entre contenedores ni una base remota. Para separar servidores, diseñar TLS y control de red antes de trasladar la DB.

## Secretos y persistencia
Las variables MYSQL_* inicializan una base VACÍA. Cambiarlas en .env con un volumen existente no cambia contraseñas dentro de MySQL: debe coordinar ALTER USER y recreación de servicios. No borre el volumen para cambiar una contraseña.

El entrypoint oficial prepara /var/lib/ghost/content y ajusta propietario al usuario node. Se conserva esa lógica al arrancar. El volumen contiene imágenes, archivos, temas y rutas; no lo sustituya por un directorio vacío durante actualizaciones.

La comprobación previa exige una cuenta activa y confirmación del operador para producción, no verifica todos sus permisos editoriales. No exponga el alta inicial públicamente. Los permisos y estado de miembros se gestionan desde Ghost.
