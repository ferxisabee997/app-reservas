import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from email.mime.image import MIMEImage

def send(email, nombre, apellidos, fecha, hora, telefono):
    # Credenciales
    user = st.secrets["emails"]["smtp_user"]
    password = st.secrets["emails"]["smtp_password"]

    sender_email = "Hanami Psicología"  # Reemplaza con tu email

    # Configuración del servidor
    msg = MIMEMultipart()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Parámetros del mensaje
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Reserva Cita"

    # Cuerpo del mensaje
    message = f"""
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
        <table width="100%" style="border-collapse: collapse; background-color: #f4f4f4; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td style="padding: 20px; text-align: center;">
                                <img src="https://hanamipsicologia.es/wp-content/uploads/2023/12/pSICOLOGIA-22.png" alt="Logo Hanami Psicología" style="width: 150px; height: auto;"/>
                                <h2 style="color: #D8A7B1;">Hola {nombre} {apellidos},</h2>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px;">
                                <p style="font-size: 16px; line-height: 1.5;">
                                    Su reserva ha sido realizada con éxito.
                                </p>
                                <p><strong>Fecha:</strong> {fecha}</p>
                                <p><strong>Hora:</strong> {hora}</p>
                                <p><strong>Teléfono:</strong> {telefono}</p>
                                <p style="margin-top: 20px;">
                                    Gracias por su confianza.<br>Un saludo.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; text-align: center; background-color: #f9f9f9;">
                                <p style="font-size: 12px; color: gray;">
                                    Si tiene alguna pregunta, no dude en contactarnos.<br>
                                    <small>Hanami Psicología | Tel: 644957350</small>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # Adjuntar el cuerpo HTML
    msg.attach(MIMEText(message, 'html'))

    # Ruta de la imagen (logo)
    image_path = 'assets/logo.png'  # Cambia esta ruta por la correcta

    # Abrir la imagen en modo binario
    with open(image_path, 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<Logo>')  # Content-ID para incrustarla en el HTML
        msg.attach(image)

    # Conexión al servidor
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(user, password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        st.success("Correo de confirmación enviado con éxito.")
    except smtplib.SMTPException as e:
        st.exception("Error al enviar el email: " + str(e))
