# Hefesto Publicaciones — Ghost + MySQL
Kit nativo para blogs profesionales y revistas digitales: editor de publicaciones, páginas, autores, etiquetas y temas de Ghost 6.70.0.

Incluye Docker Compose para Coolify/VPS, MySQL 8.4, volúmenes persistentes, alta privada del propietario, correo de prueba con Mailpit, copia de base+contenido y restauración. Las tres imágenes están fijadas por digest.

**No utiliza Supabase:** Ghost requiere MySQL para producción; no se ofrece un adaptador PostgreSQL artificial. MySQL 8.4 también aparece en el entorno de desarrollo upstream; el Compose de producción upstream consultado aún usa 8.0. Este kit elige la rama 8.4 y requiere una prueba de aceptación real con la versión fijada.

Empiece por docs/instalacion.md. Requisitos: Docker/Compose v2, Python 3.11+, dominio HTTPS, almacenamiento persistente y proveedor SMTP TLS para operar recuperación/invitaciones.

**Estado:** revisión estática y pruebas locales de scripts; no se ejecutó Ghost, MySQL ni Docker. Pendiente validar instalación y restauración en infraestructura real. No hay sitio publicado ni correos enviados a terceros.

Alcance editorial: no se configura Stripe, newsletter masiva Mailgun, ActivityPub ni analítica Tinybird. Los ejemplos editoriales son plantillas manuales; no son publicaciones ya cargadas.
