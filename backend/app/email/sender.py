"""Transactional email behind an interface; the real provider is chosen later (OQ-029)."""

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

import anyio
import structlog

from app.core.config import Settings

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class Email:
    to: str
    subject: str
    body_text: str


class EmailSender(Protocol):
    async def send(self, email: Email) -> None: ...


class ConsoleEmailSender:
    """Local/test only (settings forbid it in staging/production). Never logs the body: it can
    contain single-use links."""

    async def send(self, email: Email) -> None:
        log.info("email_not_sent_console_provider", to=email.to, subject=email.subject)


class SmtpEmailSender:
    def __init__(self, *, host: str, port: int, sender: str) -> None:
        self._host, self._port, self._from = host, port, sender

    async def send(self, email: Email) -> None:
        message = EmailMessage()
        message["From"] = self._from
        message["To"] = email.to
        message["Subject"] = email.subject
        message.set_content(email.body_text)
        await anyio.to_thread.run_sync(self._send_sync, message)

    def _send_sync(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
            smtp.send_message(message)


def build_email_sender(settings: Settings) -> EmailSender:
    if settings.email_provider == "smtp":
        return SmtpEmailSender(
            host=settings.smtp_host, port=settings.smtp_port, sender=settings.email_from
        )
    return ConsoleEmailSender()
