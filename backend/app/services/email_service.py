"""Email notification service for Pricey."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


def send_price_drop_email(
    to_email: str,
    product_title: str,
    store_name: str,
    old_price: float,
    new_price: float,
    delta_percent: float,
    product_url: str,
) -> bool:
    """
    Sends an email notification when a price drop occurs.
    If SMTP settings are not configured in environment, falls back to logging.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    emails_from = os.getenv("EMAILS_FROM", "noreply@pricey.local")

    subject = f"🏷️ Calo di prezzo del {delta_percent:.1f}% su {product_title}!"

    body_html = f"""
    <html>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #2563eb, #3b82f6); padding: 20px; border-radius: 12px; color: white; text-align: center;">
          <h1 style="margin: 0; font-size: 24px;">Pricey Alert 🏷️</h1>
          <p style="margin: 5px 0 0; opacity: 0.9;">Il prezzo è sceso oltre la tua soglia desiderata!</p>
        </div>

        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-top: 20px;">
          <span style="background: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">
            {store_name}
          </span>
          <h2 style="font-size: 18px; margin: 12px 0; color: #0f172a;">{product_title}</h2>

          <div style="display: flex; align-items: baseline; gap: 15px; margin: 15px 0; background: #ecfdf5; padding: 15px; border-radius: 8px;">
            <span style="font-size: 26px; font-weight: 800; color: #059669;">{new_price:.2f} €</span>
            <span style="font-size: 16px; text-decoration: line-through; color: #94a3b8;">{old_price:.2f} €</span>
            <span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 6px; font-size: 13px; font-weight: bold;">
              -{delta_percent:.1f}%
            </span>
          </div>

          <div style="text-align: center; margin-top: 25px;">
            <a href="{product_url}" style="background: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
              Vai all'offerta su {store_name} →
            </a>
          </div>
        </div>

        <p style="text-align: center; font-size: 12px; color: #94a3b8; margin-top: 20px;">
          Ricevi questa email perché hai impostato un avviso di prezzo su Pricey.
        </p>
      </body>
    </html>
    """

    # If no SMTP username/password configured, mock/log it safely
    if not smtp_user or not smtp_password:
        print(
            f"[EMAIL SERVICE (MOCK/LOCAL)] Sent alert for '{product_title}' to <{to_email}>: "
            f"{old_price:.2f}€ -> {new_price:.2f}€ (-{delta_percent:.1f}%)"
        )
        return True

    # Real SMTP delivery
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = emails_from
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(emails_from, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE ERROR] Failed to send email via SMTP: {e}")
        return False
