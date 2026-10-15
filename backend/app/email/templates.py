"""Plain-text templates. HTML/branded templates come with the email provider decision (OQ-029)."""

from app.email.sender import Email


def invitation_email(
    *, to: str, organization_name: str, inviter_name: str | None, role: str, accept_url: str
) -> Email:
    inviter = inviter_name or "A colleague"
    return Email(
        to=to,
        subject=f"You're invited to join {organization_name} on AdvoLevel",
        body_text=(
            f"{inviter} invited you to join {organization_name} on AdvoLevel as {role}.\n\n"
            f"Accept the invitation:\n{accept_url}\n\n"
            "The link works once and expires in 7 days. If you did not expect this email, "
            "you can ignore it.\n"
        ),
    )
