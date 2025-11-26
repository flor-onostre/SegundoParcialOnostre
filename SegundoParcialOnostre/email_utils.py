import base64
import os
import logging
from typing import Iterable, Optional

import requests

logger = logging.getLogger(__name__)


def send_brevo_email(
    to_emails: Iterable[str],
    subject: str,
    text: str,
    attachments=None,
    html: Optional[str] = None,
) -> bool:
    """
    Envía correo usando la API v3 de Brevo. Devuelve True si fue exitoso.
    attachments: lista de dicts con claves: name (str), content (bytes), type (MIME).
    html: contenido html opcional.
    """
    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name = os.environ.get("BREVO_SENDER_NAME", "")
    if not api_key or not sender_email:
        logger.warning("Faltan credenciales de Brevo (BREVO_API_KEY o BREVO_SENDER_EMAIL).")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {"accept": "application/json", "api-key": api_key, "content-type": "application/json"}

    payload = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": email} for email in to_emails if email],
        "subject": subject,
        "textContent": text,
    }
    if html:
        payload["htmlContent"] = html

    if attachments:
        payload["attachment"] = []
        for att in attachments:
            content_bytes = att.get("content")
            if content_bytes is None:
                continue
            payload["attachment"].append(
                {
                    "name": att.get("name", "adjunto"),
                    "content": base64.b64encode(content_bytes).decode(),
                    "type": att.get("type", "application/octet-stream"),
                }
            )

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if not response.ok:
            logger.error("Brevo error %s: %s", response.status_code, response.text)
        return response.ok
    except Exception as exc:
        logger.exception("Excepción enviando correo por Brevo: %s", exc)
        return False
