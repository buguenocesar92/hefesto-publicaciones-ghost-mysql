# Oferta comercial y traspaso
Ofrecer sitio editorial con dominio, instalación, tema configurado, páginas institucionales, capacitación y mantenimiento mensual. Opcionales a cotizar: migración de artículos, calendario editorial, optimización de imágenes y acompañamiento de newsletters con proveedor aparte.

Ghost encaja en publicaciones, blogs de empresas y revistas. Para gestión de productos, pedidos, inventario y facturación, conservar Odoo/WooCommerce. No se incluyen precios inventados ni promesas de audiencia o ingresos.

## Plantilla editorial manual
Páginas sugeridas: Inicio, Acerca de, Contacto y documentos correspondientes al sitio. Etiquetas: Noticias, Guías y Casos. Una entrada debe tener propósito, público, título, resumen, imagen con permiso de uso, cuerpo, autor y revisión. Roles de redacción/publicación deben asignarse al personal adecuado. No hay contenido ficticio precargado por el kit.

## Entrega al cliente
Inventario: dominio/proxy, servidor, imágenes y digests, nombres de volúmenes, DB, propietario Ghost, usuarios de equipo, proveedor SMTP, backups y prueba de restauración. Transferir secretos por gestor y rotar accesos del operador anterior.

Una instalación por cliente; si comparte host use COMPOSE_PROJECT_NAME y VOLUME_PREFIX únicos en cada .env. Mantenga nombres en terminal y Coolify para no crear volúmenes distintos inadvertidamente.

## Migrar a Odoo o WordPress
Es una migración de contenido, no una restauración de SQL dentro de otra aplicación. Exportar desde Ghost, inventariar artículos/páginas/autores/etiquetas, copiar medios y mapear slugs/URLs. Preparar redirecciones, probar formatos y reconciliar conteos. Usuarios, contraseñas y membresías requieren análisis separado; no asumir transferencia directa de suscripciones.

El kit no incluye importador Odoo/WordPress ni sincronización n8n activa. Para cambiar solo de VPS, restaurar DB+content con el mismo dominio evita una migración funcional.

Ghost tiene licencia MIT; conservar avisos aplicables de Ghost, temas y demás dependencias. No se presenta el motor editorial como un desarrollo original de Hefesto.
