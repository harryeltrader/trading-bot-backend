# app/utils/email.py

import os
from typing import Optional
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

logger = logging.getLogger(__name__)

# Configuración de email desde variables de entorno
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Trading Bot Backend")

# ============================================================================
# EMAIL SENDER
# ============================================================================

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None
) -> bool:
    """
    Enviar un email usando SMTP.
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        html_content: Contenido HTML del email
        plain_content: Contenido en texto plano (opcional)
        
    Returns:
        True si se envió correctamente, False si hubo error
    """
    try:
        # Crear mensaje
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        # Agregar contenido
        if plain_content:
            part1 = MIMEText(plain_content, "plain")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Enviar email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, message.as_string())
        
        logger.info(f"Email enviado exitosamente a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email a {to_email}: {str(e)}")
        return False

# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

def send_verification_email(email: str, code: str) -> bool:
    """
    Enviar email de verificación con código.
    
    Args:
        email: Email del destinatario
        code: Código de verificación de 6 dígitos
        
    Returns:
        True si se envió correctamente
    """
    subject = "Verifica tu email - Trading Bot Backend"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code {{ background: #667eea; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 8px; letter-spacing: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Verifica tu Email</h1>
            </div>
            <div class="content">
                <p>Hola,</p>
                <p>Gracias por registrarte en <strong>Trading Bot Backend</strong>.</p>
                <p>Para completar tu registro, por favor usa el siguiente código de verificación:</p>
                <div class="code">{code}</div>
                <p>Este código expirará en <strong>15 minutos</strong>.</p>
                <p>Si no solicitaste este código, puedes ignorar este email.</p>
                <p>Saludos,<br>El equipo de Trading Bot Backend</p>
            </div>
            <div class="footer">
                <p>Este es un email automático, por favor no respondas.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
    Verifica tu Email - Trading Bot Backend
    
    Hola,
    
    Gracias por registrarte en Trading Bot Backend.
    
    Tu código de verificación es: {code}
    
    Este código expirará en 15 minutos.
    
    Si no solicitaste este código, puedes ignorar este email.
    
    Saludos,
    El equipo de Trading Bot Backend
    """
    
    return send_email(email, subject, html_content, plain_content)

def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Enviar email con link de reset de password.
    
    Args:
        email: Email del destinatario
        reset_token: Token de reset
        
    Returns:
        True si se envió correctamente
    """
    # URL base del frontend (configurar en .env)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    subject = "Restablece tu contraseña - Trading Bot Backend"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Restablece tu Contraseña</h1>
            </div>
            <div class="content">
                <p>Hola,</p>
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en <strong>Trading Bot Backend</strong>.</p>
                <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Restablecer Contraseña</a>
                </p>
                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="background: #fff; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_link}</p>
                <p>Este enlace expirará en <strong>1 hora</strong>.</p>
                <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este email.</p>
                <p>Saludos,<br>El equipo de Trading Bot Backend</p>
            </div>
            <div class="footer">
                <p>Este es un email automático, por favor no respondas.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
    Restablece tu Contraseña - Trading Bot Backend
    
    Hola,
    
    Recibimos una solicitud para restablecer la contraseña de tu cuenta.
    
    Haz clic en el siguiente enlace para crear una nueva contraseña:
    {reset_link}
    
    Este enlace expirará en 1 hora.
    
    Si no solicitaste restablecer tu contraseña, puedes ignorar este email.
    
    Saludos,
    El equipo de Trading Bot Backend
    """
    
    return send_email(email, subject, html_content, plain_content)

def send_welcome_email(email: str, name: str) -> bool:
    """
    Enviar email de bienvenida después de verificar el email.
    
    Args:
        email: Email del destinatario
        name: Nombre del usuario
        
    Returns:
        True si se envió correctamente
    """
    subject = "¡Bienvenido a Trading Bot Backend! 🎉"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 ¡Bienvenido!</h1>
            </div>
            <div class="content">
                <p>Hola {name},</p>
                <p>¡Tu cuenta ha sido verificada exitosamente!</p>
                <p>Ya puedes comenzar a usar <strong>Trading Bot Backend</strong> para analizar tus operaciones de trading.</p>
                <p><strong>Características disponibles:</strong></p>
                <ul>
                    <li>📊 Análisis avanzado de operaciones</li>
                    <li>📈 Curvas de capital en tiempo real</li>
                    <li>🎯 KPIs profesionales</li>
                    <li>📉 Análisis de drawdown</li>
                    <li>🔥 Heatmaps de rendimiento</li>
                </ul>
                <p>¡Comienza a optimizar tu trading ahora!</p>
                <p>Saludos,<br>El equipo de Trading Bot Backend</p>
            </div>
            <div class="footer">
                <p>Este es un email automático, por favor no respondas.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
    ¡Bienvenido a Trading Bot Backend!
    
    Hola {name},
    
    ¡Tu cuenta ha sido verificada exitosamente!
    
    Ya puedes comenzar a usar Trading Bot Backend para analizar tus operaciones de trading.
    
    Saludos,
    El equipo de Trading Bot Backend
    """
    
    return send_email(email, subject, html_content, plain_content)
