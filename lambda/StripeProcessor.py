from __future__ import print_function
import boto3
import stripe
import logging
import pprint
import json


def process_payment(event, context):

    logger = logging.getLogger()
    logger.setLevel( logging.INFO)

    paymentDetails = _parseLogPaymentDetails(event, logger)

    return _submitPaymentRequest(paymentDetails, logger)



def _parseLogPaymentDetails(paymentRequest, logger):
    logger.info( "New payment processing request received:\n{0}".format(
        pprint.pformat(paymentRequest)) )

    # Need to validate body here, maybe need XSD and have front end pass
    #   XML?
    paymentDetails = paymentRequest['payment_info']

    return paymentDetails



def _setStripeApiKey(stripeKeyType, logger):
    encryptedTokenFile = 'stripe_encrypted_{0}_secret_key_token.dat'.format(stripeKeyType)

    with open( encryptedTokenFile, 'rb' ) as readHandle:
        encryptedBytes = readHandle.read()

    kmsClient = boto3.client('kms')

    stripe.api_key = kmsClient.decrypt(
        CiphertextBlob=encryptedBytes)['Plaintext'].decode('UTF-8')

    logger.info( "API key set to: {0}".format(stripe.api_key) )


def _submitPaymentRequest(paymentDetails, logger):
    resultsLog = {
        'payment_details': paymentDetails 
    }

    stripeKeyType = paymentDetails['stripe_key']
    del paymentDetails['stripe_key']

    _setStripeApiKey(stripeKeyType, logger)

    try:
        chargeResponse = stripe.Charge.create( 
            amount          = paymentDetails['amount'],
            currency        = paymentDetails['currency'],
            source          = paymentDetails['source'],
            description     = paymentDetails['description'],
            receipt_email   = paymentDetails['receipt_email']
        )
    except stripe.error.CardError as e:
        body = e.json_body
        err = body.get('error', {})

        errorDetails = {
            'status'        : "error",
            'type'          : err.get('type'),
            'code'          : err.get('code'),
            'message'       : err.get('message')
        }
        resultsLog['stripe_response'] = errorDetails

        return errorDetails

    else:
        # No exception thrown -- happy case!
        resultsLog['stripe_response'] = chargeResponse

        return { 'status': chargeResponse['status'] }
