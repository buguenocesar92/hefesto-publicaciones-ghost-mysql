# Fuentes — 15 octubre 2026
- https://github.com/TryGhost/Ghost/releases/tag/v6.70.0
- https://github.com/docker-library/ghost/blob/master/docker-entrypoint.sh
- https://github.com/docker-library/ghost/blob/master/6/bookworm/Dockerfile
- https://github.com/TryGhost/Ghost/blob/v6.70.0/compose.dev.yaml
- https://github.com/TryGhost/ghost-docker/blob/main/compose.yml
- https://hub.docker.com/_/ghost
- https://ghost.org/docs/config/
- https://ghost.org/changelog/6/
- https://dev.mysql.com/doc/refman/8.4/en/

La imagen Ghost y MySQL se fijan por digest consultado. MySQL 8.4 se elige como rama LTS presente en desarrollo upstream; no se afirma que sea la imagen actual del Compose oficial de producción, que consultado usa 8.0. La compatibilidad operativa de este kit debe validarse antes de entrega.
