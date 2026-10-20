import hashlib

from flask import Response, request

CACHE_MAX_AGE_IMAGENES = 60 * 60 * 24  # 1 dia


def respuesta_imagen(datos, mime):
    """Respuesta HTTP para una imagen guardada como BLOB en la BD.

    El ETag sale del contenido: si se vuelve a subir la imagen el hash
    cambia solo y el navegador la pide de nuevo; si no cambio, responde
    304 sin reenviar los bytes. Sin esto, cada <img> (producto,
    categoria, avatar) se vuelve a descargar completa en cada visita.
    """
    respuesta = Response(datos, mimetype=mime or "image/jpeg")
    respuesta.set_etag(hashlib.md5(datos).hexdigest())
    respuesta.cache_control.public = True
    respuesta.cache_control.max_age = CACHE_MAX_AGE_IMAGENES
    return respuesta.make_conditional(request)
