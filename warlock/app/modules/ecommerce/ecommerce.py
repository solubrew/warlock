
app.route('/checkout', methods=['POST'])
def checkout():
	''' Create new Checkout Session for the order
		Other optional params include:
		[billing_address_collection] - to display billing address details on
										the page
		[customer] - if you have an existing Stripe Customer ID
		[payment_intent_data] - lets capture the payment later
		[customer_email] - lets you prefill the email input in the form
		For full details see https:#stripe.com/docs/api/checkout/sessions/create
		?session_id={CHECKOUT_SESSION_ID} means the redirect will have the
											session ID set as a query param '''
	domain_url = self.config.session['domain_url']
	stripe.api_key = stripe_keys['secret_key']
	kwargs = {'sucess_url': '{0}success?session_id={CHECKOUT_SESSION_ID}'.format(domain_url),
				'cancel_url': '{0}cancelled'.format(domain_url),
				'payment_method_types': ['card'], 'mode': 'payment',
				'line_items': []}
	for item in items:
		kwargs['line_items'].append({'name': item['name'],
												'quantity': item['qty'],
												'currency': item['currency'],
												'amount': item['amount']})
	try:
		session = stripe.checkout.Session.create(**kwargs)
		return jsonify({'sessionId': checkout_sesion['id']})
	except Exception as e:
		return jsonify(errors=str(e)), 403

@app.route('/webhook', methods=['POST'])#										||
def stripe_webhook():#															||
	'''Webhook callback for completion of payment '''
	payload = request.get_data(as_text=True)#									||
	sig_header = request.headers.get('Stripe-Signature')#						||
	key = stripe_keys['endpoint_secret']#										||
	try:#																		||
		event = stripe.Webhook.construct_event(payload, sig_header, key)#		||
	except ValueError as e:#													||Invalid payload
		return "Invalid payload", 400#											||
	except stripe.error.SignatureVerificationError as e:#						||Invalid signature
		return "Invalid signature", 400#										||
	if event["type"] == "checkout.session.completed":#							||Handle the checkout.session.completed event
		print("Payment was successful.")
		# TODO: run some custom code here...initate delivery workflow for product
	return "Success", 200
