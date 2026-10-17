# Correo, membresías y alcance
Correo transaccional SMTP: invitaciones de equipo, recuperación de acceso y mensajes de acceso de miembros según el flujo nativo. El kit usa mail__transport=SMTP y TLS implícito en puerto 465. Requiere remitente y dominio verificados con su proveedor. Para un proveedor solo STARTTLS 587, adaptar y probar explícitamente antes de entregar.

El envío masivo de newsletters es una configuración separada dentro de Ghost, con Mailgun según la documentación consultada. Configurar SMTP no significa que los boletines masivos estén funcionando. Este ZIP no incluye claves Mailgun ni campañas programadas.

Stripe y membresías de pago tampoco están configurados. No se promete cobro con Flow/Webpay ni emisión tributaria por instalar Ghost. Para e-commerce y logística, usar WooCommerce u Odoo; Ghost está enfocado en publicación y audiencia.

Este despliegue editorial no activa servicios de ActivityPub ni Tinybird del stack ampliado Ghost. No debe presentarse como una réplica completa de Ghost(Pro). Si se añaden servicios, ampliar recursos, secretos, monitoreo y respaldo.

No se habilitan integraciones externas ni carga automática de artículos. Antes de entrega revise las opciones de miembros, privacidad y cookies según el uso real del sitio; no se afirma cumplimiento legal automático.
