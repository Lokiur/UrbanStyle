# =========================
# ENVIO DE CORREOS (SMTP)
# =========================
# Configuracion por variables de entorno (ver .env.example):
#   MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_SENDER
# Si MAIL_SERVER no esta definido, el correo se imprime en consola
# (modo desarrollo) en lugar de enviarse.

import os
import smtplib
from email.message import EmailMessage


def configurado():
    return bool(os.environ.get("MAIL_SERVER"))


def enviar_correo(destino, asunto, texto, html=None):
    remitente = os.environ.get("MAIL_SENDER") or os.environ.get("MAIL_USERNAME", "")

    if not configurado():
        print("\n========== CORREO (modo desarrollo, no enviado) ==========")
        print(f"Para: {destino}\nAsunto: {asunto}\n\n{texto}")
        print("==========================================================\n")
        return

    mensaje = EmailMessage()
    mensaje["From"] = remitente
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(texto)
    if html:
        mensaje.add_alternative(html, subtype="html")

    servidor = os.environ["MAIL_SERVER"]
    puerto = int(os.environ.get("MAIL_PORT", 587))
    usuario = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_PASSWORD")

    if puerto == 465:
        smtp = smtplib.SMTP_SSL(servidor, puerto, timeout=15)
    else:
        smtp = smtplib.SMTP(servidor, puerto, timeout=15)
        smtp.starttls()

    with smtp:
        if usuario:
            smtp.login(usuario, password)
        smtp.send_message(mensaje)
