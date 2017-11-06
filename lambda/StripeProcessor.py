from __future__ import print_function
import boto3
import stripe
import logging
import pprint


def process_payment(event, context):

    logger = logging.getLogger()
    logger.setLevel( logging.INFO)

    paymentDetails = _parseLogPaymentDetails(event['body'], logger)

    _setStripeApiKey(logger)

    return { 'status': _submitPaymentRequest(paymentDetails, logger) }



def _parseLogPaymentDetails(paymentRequest, logger):
    logger.info( "New pament processing request received:\n{0}".format(
        pprint.pformat(paymentRequest)) )

    # Need to validate body here, maybe need XSD and have front end pass
    #   XML?
    paymentDetails = paymentRequest['payment_info']['required']

    return paymentDetails



def _setStripeApiKey(logger):
    encryptedTokenFile = 'stripe_encrypted_secret_key_token.dat'

    with open( encryptedTokenFile, 'rb' ) as readHandle:
        encryptedBytes = readHandle.read()

    kmsClient = boto3.client('kms')

    stripe.api_key = kmsClient.decrypt(
        CiphertextBlob=encryptedBytes)['Plaintext'].decode('UTF-8')

    logger.info( "API key set to: {0}".format(stripe.api_key) )


def _submitPaymentRequest(paymentDetails, logger):
    chargeResponse = stripe.Charge.create( 
        amount      = paymentDetails['amount'],
        currency    = paymentDetails['currency'],
        source      = paymentDetails['source'],
        description = paymentDetails['description']
    )

    #pprint.pprint("Charge response:\n{0}".format(chargeResponse))

    return chargeResponse['status'] 
