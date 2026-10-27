# Politica de tratamiento de datos personales — hefesto-publicaciones (Ghost + MySQL)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit. Este documento describe que datos guarda el kit, por que, cuanto
tiempo los retiene y como se ejercen los derechos del titular (Ley 21.719).

## 1. Que datos guarda este kit

- **Cuentas**: nombre, correo, hash de contrasena, rol y preferencias.
- **Publicaciones**: titulo, cuerpo, estado, etiquetas y autores.
- **Comentarios y reacciones**: texto, autor y fecha.
- **Adjuntos**: imagenes y archivos de las publicaciones (volumen `content`).
- **Boletin y suscripciones**: correo de la lista y estado de la suscripcion.
- **Claves del servicio**: las claves de MySQL y de correo, que viven en el
  `.env` y nunca se copian en claro al respaldo.

- **Copias locales de respaldo**: `backups/<timestamp>/` con el dump de la base
  de datos, los volumenes cifrados (`content.tar.gz.age`), los nombres de las
  variables (`env.vars`) y el `.env` cifrado (`env.age`).

## 2. Que datos NO guarda este kit

- El `.env` **no** se copia en claro al respaldo: solo sus nombres de variable
  (`env.vars`) y, si hay un receptor `age` configurado, el `.env` cifrado
  (`env.age`).
- Los volumenes con material personal **tampoco** viajan en claro: se cifran
  con `age` (`content.tar.gz.age`) o no se incluyen y el manifiesto lo declara. Ver
  `docs/CONTRATO-RESPALDO.md`, reglas 5 y 6.
- El kit no envia datos de personas a servicios de terceros.

## 3. Base legal y deberes

- **Minimizacion**: el kit guarda lo necesario para servir la finalidad
  declarada. No agrega metadatos de seguimiento ni perfila a las personas.
- **Finalidad**: la que declara el titulo del kit. Los datos no se usan para
  otros fines ni se ceden a terceros.
- **Seguridad**: los respaldos se cifran en reposo con `age` hacia el destino
  del operador, la clave privada no esta en este servidor, el `.env` nunca sale
  en claro y la base exige TLS con credenciales de aplicacion.
- **Auditoria**: cada respaldo y cada restauracion dejan registro en
  `logs/restore.log` con origen, sha256 verificado, destino y resultado. Es
  registro de actividades de tratamiento: no guarda valores de secretos.

## 4. Retencion

| Dato | Donde | Retencion por defecto | Quien lo borra |
|---|---|---|---|
| Cuentas y actividad | MySQL | mientras la cuenta exista | el operador |
| Publicaciones, comentarios y adjuntos | MySQL y volumen `content` | 24 meses tras la baja | el operador |
| Suscripciones al boletin | MySQL | mientras la suscripcion siga activa | el operador |


| Respaldos en disco | `backups/<timestamp>/` | **a definir por el operador**; el kit no borra nada por su cuenta | el operador |
| Registro de auditoria | `logs/restore.log` | append-only; se trunca por politica del cliente | el operador |

**El kit no borra respaldos ni datos por su cuenta.** Borrar es una decision del
operador, porque un respaldo borrado no se recupera.

## 5. Derechos del titular (acceso, rectificacion y supresion)

El cliente que opera el kit debe poder atender las solicitudes de sus
titulares:

1. **Acceso**: entregar los datos de una persona al titular que lo solicite.
2. **Rectificacion**: corregir los datos desde la interfaz del kit.
3. **Supresion**: eliminar la cuenta, su actividad y los respaldos que las
   contengan, y dejar constancia en el registro de auditoria.
4. **Revocacion del consentimiento**: si el tratamiento depende del
   consentimiento, eliminar la cuenta y su registro de actividad.

El kit garantiza que los datos son localizables, corregibles y borrables; el
cliente es quien conoce la identidad de los titulares.

## 6. Verificacion

- `bats tests/backup_restore.bats` comprueba, con datos sinteticos, que el
  `.env` ni el material personal quedan en claro, que el manifiesto lleva las
  cinco claves, que un artefacto alterado se rechaza y que un destino no vacio
  aborta la restauracion.
- `gitleaks` corre en CI sobre el repositorio y su historial.
