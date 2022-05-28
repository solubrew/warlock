stripe_keys = {
	'secret_key': '',
	'publishable_key': ''
}




def create_checkout_session():
	'''evalute security options to verify product id and price '''
	domain_url = 'http://localhost:5000'
	stripe.api_key = stripe_keys['secret_key']
	try:
		checkout_session = stripe.checkout.Session.create(
			success_url='{0}success?session_id={CHECKOUT_SESSION_ID}'.format(domain_url),
			cancel_url='{0}cancelled'.format(domain_url),
			payment_method_types=['card'],
			mode='payment',
			line_items=[
				{
					'name': 'T-shirt',
					'quantity': 1,
					'currency': 'usd',
					'amount': '2000',
				}
			]
		)
		return jsonify({'sessionId': checkout_session['id']})
	except Exception as e:
		return jsonify(error=str(e)), 403
