# Hefesto Publicaciones — Ghost + MySQL

Kit nativo para blogs profesionales y revistas digitales: editor de publicaciones, páginas, autores, etiquetas y temas de Ghost 6.70.0.

Incluye Docker Compose para Coolify/VPS, MySQL 8.4, volúmenes persistentes, alta privada del propietario, correo de prueba con Mailpit, copia de base+contenido y restauración. Las tres imágenes están fijadas por digest.

**No utiliza Supabase:** Ghost requiere MySQL para producción; no se ofrece un adaptador PostgreSQL artificial. MySQL 8.4 también aparece en el entorno de desarrollo upstream; el Compose de producción upstream consultado aún usa 8.0. Este kit elige la rama 8.4 y requiere una prueba de aceptación real con la versión fijada.

Empiece por docs/instalacion.md. Requisitos: Docker/Compose v2, Python 3.11+, dominio HTTPS, almacenamiento persistente y proveedor SMTP TLS para operar recuperación/invitaciones.

**Estado:** revisión estática y pruebas locales de scripts; no se ejecutó Ghost, MySQL ni Docker. Pendiente validar instalación y restauración en infraestructura real. No hay sitio publicado ni correos enviados a terceros.

Alcance editorial: no se configura Stripe, newsletter masiva Mailgun, ActivityPub ni analítica Tinybird. Los ejemplos editoriales son plantillas manuales; no son publicaciones ya cargadas.

## Despliegue en Coolify (MVP Hefesto)

Importe el repositorio en Coolify con build pack **Docker Compose**, apunte al
`compose.yaml` de la raíz y exponga el servicio `app` en el puerto interno
`2368`. Coolify/Traefik se encargan de TLS y del dominio; no use `ports:` en
el compose ni agregue Caddy/nginx propios.

### Variables de entorno

Siempre obligatorias (sin ellas el kit no arranca):

- `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`: claves de MySQL. Genérelas con
  `python3 scripts/configure.py`; nunca las reuse.
- `PUBLIC_URL`: URL HTTPS pública del blog (Traefik la reenvía al servicio
  `app`).
- `INITIAL_SETUP_COMPLETE`: queda en `false` durante el primer despliegue.

Solo obligatorias cuando `SMTP_READY=true`:

- `MAIL_FROM`, `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`.

Si todavía no hay SMTP real, deje `SMTP_READY=false`: el arranque desactiva
el correo transaccional (transporte `stub` que acepta el envío en `null://`
sin entregar nada) en lugar de abortar. `MAIL_FROM` puede dejarse vacío en
ese modo.

### Flujo operativo del primer despliegue

El primer arranque con `INITIAL_SETUP_COMPLETE=false` se detiene en
`ops/preflight.sh` a la espera de una cuenta activa en `users`. Por eso el
despliegue inicial se hace en dos pasadas, sin nombres fijos (Coolify pone
el nombre del proyecto):

1. En Coolify, cree el recurso con `INITIAL_SETUP_COMPLETE=false`. El
   `preflight` fallará; eso es esperado.
2. Levante una sesión de bootstrap contra los mismos volúmenes que Coolify.
   Use el nombre de proyecto que Coolify asignó al recurso (visible en la
   lista de stacks, o ejecutando `docker compose ls` en el host):
   ```
   docker compose -p <nombre-de-proyecto-de-coolify> \
     -f compose.yaml -f compose.bootstrap.yaml up -d app
   ```
   `compose.bootstrap.yaml` añade Mailpit y deja MySQL expuesta al host.
   Complete el alta privada del propietario vía SSH tal como dice
   `docs/instalacion.md`.
3. Una vez que la cuenta del propietario esté activa, marque
   `INITIAL_SETUP_COMPLETE=true` en Coolify y vuelva a desplegar `app` con
   el compose «limpio» (sin `compose.bootstrap.yaml`). El `preflight` pasa
   y Ghost sirve.

Importante: ejecute el bootstrap con `-p <nombre-de-proyecto-de-coolify>`
para que comparta los volúmenes de Coolify. Si lo hace en otro proyecto,
Compose crea volúmenes nuevos (`<otro-proyecto>_mysql`,
`<otro-proyecto>_content`) y pierde los datos.

### Volúmenes

Los volúmenes del compose llevan `name: ${VOLUME_PREFIX:-hefesto-publicaciones}-{mysql,content}`.
Eso fija su nombre estable mientras Coolify compone el resto, así que un
segundo despliegue con el mismo `VOLUME_PREFIX` reusa los datos. Si su
instalación anterior usaba nombres generados por Compose sin prefijo (por
ejemplo, después de un despliegue con el compose anterior), los volúmenes
nuevos se nombrarán `<prefijo>-mysql` y `<prefijo>-content` y aparecerán
vacíos: copie los datos desde los antiguos antes del primer arranque o use
`VOLUME_PREFIX=<nombre-directorio-coolify>` para conservar nombres
existentes como `<directorio-coolify>-mysql`.

### Redes

El servicio `db` solo está en la red `backend` (interna) y `app` une
`frontend` y `backend`. Después del primer arranque, verifique con
`docker inspect <db>` que `db` solo pertenezca a la red `backend`; si
Coolify le agregó su red de destino, desconéctela manualmente o desactive
*Connect to Predefined Network* en el recurso, porque MySQL quedaría
accesible desde el resto de stacks de Coolify.
