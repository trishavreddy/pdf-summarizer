from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.config import get_settings

settings = get_settings()


async def send_summary_email(to_email: str, filename: str, summary_content: str) -> bool:
    """
    Send summary email using SendGrid.

    Args:
        to_email: Recipient email address
        filename: Original PDF filename
        summary_content: The generated summary

    Returns:
        True if email sent successfully, False otherwise
    """
    if not settings.sendgrid_api_key:
        print("SendGrid API key not configured, skipping email")
        return False

    try:
        subject = f"Your PDF Summary: {filename}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .summary {{ background-color: white; padding: 20px; border-radius: 8px; margin-top: 15px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">PDF Summary Ready</h1>
                </div>
                <div class="content">
                    <p>Your summary for <strong>{filename}</strong> has been generated successfully.</p>
                    <div class="summary">
                        <h3>Summary</h3>
                        <p>{summary_content.replace(chr(10), '<br>')}</p>
                    </div>
                    <p style="margin-top: 20px;">
                        <a href="{settings.frontend_url}/dashboard" style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            View in Dashboard
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>This email was sent by PDF Summarizer. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
PDF Summary Ready

Your summary for "{filename}" has been generated successfully.

SUMMARY:
{summary_content}

View your summary in the dashboard: {settings.frontend_url}/dashboard

This email was sent by PDF Summarizer.
        """

        message = Mail(
            from_email=Email(settings.from_email, "PDF Summarizer"),
            to_emails=To(to_email),
            subject=subject,
        )
        message.content = [
            Content("text/plain", plain_content),
            Content("text/html", html_content),
        ]

        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        return response.status_code in [200, 201, 202]

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def send_summary_email_sync(to_email: str, filename: str, summary_content: str) -> bool:
    """
    Synchronous version of send_summary_email for use in Celery tasks.
    """
    if not settings.sendgrid_api_key:
        print("SendGrid API key not configured, skipping email")
        return False

    try:
        subject = f"Your PDF Summary: {filename}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .summary {{ background-color: white; padding: 20px; border-radius: 8px; margin-top: 15px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">PDF Summary Ready</h1>
                </div>
                <div class="content">
                    <p>Your summary for <strong>{filename}</strong> has been generated successfully.</p>
                    <div class="summary">
                        <h3>Summary</h3>
                        <p>{summary_content.replace(chr(10), '<br>')}</p>
                    </div>
                    <p style="margin-top: 20px;">
                        <a href="{settings.frontend_url}/dashboard" style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            View in Dashboard
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>This email was sent by PDF Summarizer. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
PDF Summary Ready

Your summary for "{filename}" has been generated successfully.

SUMMARY:
{summary_content}

View your summary in the dashboard: {settings.frontend_url}/dashboard

This email was sent by PDF Summarizer.
        """

        message = Mail(
            from_email=Email(settings.from_email, "PDF Summarizer"),
            to_emails=To(to_email),
            subject=subject,
        )
        message.content = [
            Content("text/plain", plain_content),
            Content("text/html", html_content),
        ]

        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        return response.status_code in [200, 201, 202]

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
