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

Variables de entorno obligatorias para Coolify: `MYSQL_ROOT_PASSWORD`,
`MYSQL_PASSWORD`, `PUBLIC_URL` (HTTPS), `MAIL_FROM`, `SMTP_HOST`,
`SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_READY` y `INITIAL_SETUP_COMPLETE`.
Las nuevas variables opcionales para el contrato MVP son `MAIL_TRANSPORT`
(por defecto `SMTP`), `SMTP_PORT` (465), `SMTP_SECURE` (`true`). Si todavía
no hay SMTP real, deje `SMTP_READY=false`: el arranque desactiva el correo
transaccional en lugar de abortar.

El servicio `app` ya no fija `name:` a nivel de compose ni en volúmenes/redes:
Coolify asigna el nombre de proyecto y los nombres de volúmenes según sus
convenciones. La red `backend` permanece interna para que MySQL no quede
expuesta.
