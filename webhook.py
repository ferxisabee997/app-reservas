import json
import stripe
from flask import Flask, jsonify, request, render_template

# La clave secreta de tu cuenta de Stripe.
stripe.api_key = "sk_test_51MmaSMCQR2tBXUrAFBn2wyEXhy8f92KexvMc3NwEM1kNOBZEaBgPPBpsXf3PImBeSDSNmoqPQJMmXTzo17osicrY00kOTvABWh"  # Reemplaza con tu clave secreta real

# Este es tu secreto del webhook de Stripe para probar tu endpoint localmente.
endpoint_secret = 'whsec_c5d2e76eaf9ff74a7368b1d3dbe929a155e8d668f64a5d549307f854e1f2666e'

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['Stripe-Signature']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': str(e)}), 400

    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Aquí puedes extraer los datos necesarios para crear la reserva
        customer_email = session.get('customer_email')
        
        # Lógica para crear el evento en Google Calendar y guardar en Google Sheets
        print(f"Reserva creada para: {customer_email}")

    else:
        print('Tipo de evento no manejado {}'.format(event['type']))

    return jsonify(success=True)

@app.route('/success')
def success():
    session_id = request.args.get('session_id')

    try:
        # Recuperar la sesión de pago de Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == "paid":
            # Extraer información del cliente de la sesión
            customer_email = checkout_session.customer_email
            
            # Aquí puedes agregar la lógica para crear la reserva
            print(f"Reserva confirmada para: {customer_email}")

            # Retorna una respuesta al cliente usando la plantilla HTML
            return render_template('success.html', customer_email=customer_email)  # Renderiza la plantilla HTML

        else:
            return "El pago no se completó. Por favor, intente nuevamente."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=4242)
