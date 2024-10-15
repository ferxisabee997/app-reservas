import streamlit as st
from streamlit_option_menu import option_menu
from send_email import send
from google_sheets import GoogleSheets
import re
import uuid
from google_calendar import GoogleCalendar
import numpy as np
import datetime as dt
import stripe
import os

# Configuración de la página
page_title = 'Reservas Hanami Psicología'
page_icon = 'assets/logo.png'
layout = 'centered'
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

# Función para cargar el CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css(os.path.join('static', 'estilo.css'))  # Asegúrate de que la ruta sea correcta

# CSS para el botón
st.markdown("""
    <style>
        .btn-pagar {
            display: inline-block; 
            padding: 10px 20px; 
            background-color: #FF8D87; 
            color: white; 
            border-radius: 5px; 
            text-decoration: none; 
            font-weight: bold; 
            text-align: center; 
            transition: background-color 0.3s; /* Transición suave */
            border: none; /* Elimina el borde */
        }

        .btn-pagar:hover {
            background-color: #ffa19c; /* Color de fondo al pasar el cursor */
        }

        /* Asegurarse de que no haya estilos por defecto para los enlaces */
        a.btn-pagar {
            color: white; /* Color del texto */
            cursor: pointer; /* Cambia el cursor al pasar sobre el botón */
        }

        a.btn-pagar:visited, a.btn-pagar:focus {
            color: white; /* Color del texto para enlaces visitados */
            text-decoration: none; /* Elimina el subrayado */
        }
    </style>
""", unsafe_allow_html=True)

horas = ["09:00", "10:00", "11:00", "12:00", "13:00",
         "15:00", "16:00", "17:00", "18:00", "19:00"]

document = "Reservas"
sheet = "reservas1"
credentials = st.secrets["google"]["credential_google"]
stripe.api_key = st.secrets["stripe"]["secret_key"]
precio_reserva = 6000
idcalendar = 'ferxisabee@gmail.com'
time_zone = "Europe/Madrid"

# Funciones
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def generate_uid():
    return str(uuid.uuid4())

def add_fifty_minutes(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    new_time = (dt.datetime.combine(dt.date.today(), parsed_time) + dt.timedelta(minutes=50)).time()
    return new_time.strftime("%H:%M")

def es_dia_habil(fecha):
    return fecha.weekday() < 5  # Retorna True si es un día de lunes a viernes

st.image("assets/logo.png")
st.title("Reserva tu cita")
st.text("C. Gregorio Pérez de María 'El Cainejo', 6")

selected = option_menu(menu_title=None, options=["Reservar", "Detalles"],
                       icons=["calendar2-plus", "book-half"],
                       orientation="horizontal")

if selected == "Detalles":
    st.subheader("Ubicación")
    st.markdown("""<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d2936.399482850926!2d-5.593789!3d42.610483!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xd379a57fd14d211%3A0x22844f3eed5f9ad3!2sC.%20Gregorio%20Perez%20de%20Mar%C3%ADa%20%22El%20Cainejo%22%2C%206%2C%2024010%20Le%C3%B3n%2C%20Espa%C3%B1a!5e0!3m2!1ses!2sus!4v1718728768086!5m2!1ses!2sus" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>""", unsafe_allow_html=True)

    st.subheader("Horario")
    dia, hora = st.columns(2)

    dia.text("De Lunes a Jueves")
    hora.text("De 09:00 a 19:00")
    dia.text("Viernes")
    hora.text("De 09:00 a 14:00")

    st.subheader("Contacto")
    st.text("📞 644957350")

    st.subheader("Conócenos")
    st.markdown('[Hanami Psicología](https://hanamipsicologia.es/)')

if selected == "Reservar":
    st.subheader("Reservar")

    c1, c2 = st.columns(2)
    nombre = c1.text_input("Tu nombre*")
    apellidos = c2.text_input("Tus apellidos*")
    email = c1.text_input("Tu email*")
    telefono = c2.text_input("Teléfono*")
    fecha = c1.date_input("Fecha", min_value=dt.date.today() + dt.timedelta(days=1))  # Aumentar en un día

    if not es_dia_habil(fecha):
        st.error("Por favor selecciona un día de lunes a viernes.")
        Enviar = st.button("Reservar", disabled=True)  # Botón deshabilitado
    else:
        # Obtener horas bloqueadas solo si es un día hábil
        calendar = GoogleCalendar(credentials, idcalendar)
        hours_blocked = calendar.get_events_start_time(str(fecha))
        result_hours = np.setdiff1d(horas, hours_blocked)
        hora = c2.selectbox("Hora", result_hours if len(result_hours) > 0 else horas)

        notas = c1.text_area("Notas")
        Enviar = st.button("Reservar")  # Botón habilitado

    # Proceso de pago solo si el día es hábil y el botón está habilitado
    if Enviar:
        with st.spinner("Cargando..."):
            if not all([nombre, apellidos, telefono, email]):
                st.warning("Por favor completa todos los campos.")
            elif not validate_email(email):
                st.warning("El email no es válido.")
            else:
                # Crear un cliente de Stripe
                try:
                    customer = stripe.Customer.create(
                        email=email,
                        name=f"{nombre} {apellidos}",
                        phone=telefono,
                    )

                    # Crear una sesión de pago en Stripe
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        customer=customer.id,
                        line_items=[{
                            'price_data': {
                                'currency': 'eur',
                                'product_data': {
                                    'name': 'Reserva de Cita',
                                },
                                'unit_amount': precio_reserva,  # Precio en centavos
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=f'https://app-reservas-vkv2wzmmgqkriylvwn7akc.streamlit.app/?session_id={{CHECKOUT_SESSION_ID}}&nombre={nombre}&apellidos={apellidos}&email={email}&telefono={telefono}&fecha={fecha}&hora={hora}&notas={notas}',
                        cancel_url='https://tu-web.com/cancel',  # Cambia esto a tu URL de cancelación
                    )

                    # Redirigir al usuario a la página de pago
                    if session.url:
                        st.markdown(f"""
                        <div style="padding: 10px; text-align: center;">
                            <p>Para completar tu reserva, haz clic en el siguiente botón para pagar:</p>
                            <a href="{session.url}" class="btn-pagar">
                                Pagar ahora
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                        st.success("Por favor completa el pago para finalizar la reserva.")
                    else:
                        st.error("Hubo un problema al crear la sesión de pago. Intenta nuevamente.")
                except Exception as e:
                    st.error(f"Error durante la creación de cliente o sesión en Stripe: {e}")

# Lógica para verificar el pago y crear la cita
# Lógica para verificar el pago y crear la cita
if 'session_id' in st.query_params:
    session_id = st.query_params['session_id']
    nombre = st.query_params.get('nombre', 'Cliente')
    apellidos = st.query_params.get('apellidos', '')
    email = st.query_params.get('email', '')
    telefono = st.query_params.get('telefono', '')
    fecha_str = st.query_params.get('fecha', '')
    hora = st.query_params.get('hora', '09:00')
    notas = st.query_params.get('notas', '')

    # Convertir fecha de cadena a objeto de fecha
    try:
        fecha = dt.datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        st.error("Error en la fecha proporcionada.")
        st.stop()

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == "paid":
            # Crear evento en Google Calendar
            parsed_time = dt.datetime.strptime(hora, "%H:%M").time()
            start_time = dt.datetime.combine(fecha, parsed_time).strftime('%Y-%m-%dT%H:%M:%S')
            end_time_str = add_fifty_minutes(hora)
            end_time = dt.datetime.combine(fecha, dt.datetime.strptime(end_time_str, "%H:%M").time()).strftime('%Y-%m-%dT%H:%M:%S')

            # Lógica para enviar correo electrónico
            uid = generate_uid()
            data = [[nombre, apellidos, email, telefono, str(fecha), hora, notas, uid]]
            
            # Crear el evento
            calendar = GoogleCalendar(credentials, idcalendar)
            try:
                calendar.create_event(
                    name_event=f'Cita con {nombre} {apellidos}',
                    start_time=start_time,
                    end_time=end_time,
                    timezone=time_zone,
                    attendes=[email]  # Aquí puedes agregar más correos electrónicos si es necesario
                )

                # Enviar correo de confirmación
                send(email, nombre, apellidos, fecha, hora, telefono)
                
                # Mostrar mensaje de éxito
                st.markdown(f"""
                    <div class="container">
                        <header>
                            <img src="https://hanamipsicologia.es/wp-content/uploads/2023/12/pSICOLOGIA-22.png" alt="Logo" class="logo">
                            <h1>¡Cita reservada con éxito!</h1>
                        </header>
                        <div class="thank-you">Gracias {nombre} {apellidos} nos vemos en la proxima cita</div>
                        <div class="message">Tu cita ha sido confirmada para el {fecha} a las {hora}.</div>
                        <a href="https://hanamipsicologia.es/" class="button">Volver al inicio</a>

                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error al crear la cita en Google Calendar o enviar el correo: {e}")

        else:
            st.error("El pago no fue exitoso. Por favor intenta nuevamente.")
    except Exception as e:
        st.error(f"Error al verificar el pago: {e}")
