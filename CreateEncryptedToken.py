from __future__ import print_function
import pprint
import re
import boto3
import os
import argparse


def _writeEncryptedTokens(userdata):
 
    encryptedTokens = _encryptTokens(userdata)

    for keyType in [ 'test', 'live' ]:
        #pprint.pprint(encryptedTokens[keyType])
        with open( "lambda/stripe_encrypted_{0}_secret_key_token.dat".format(keyType), 'wb') as fileHandle:
            fileHandle.write( encryptedTokens[keyType] )


def _encryptTokens(userdata):

    # Update our running environment with the values that set access key id/secret access key
    os.environ.update( userdata['lambda_role'] )
     
    kmsClient = boto3.client('kms', region_name=userdata['kms_key']['key_region'])

    encryptedTokens = {}

    for keyType in [ 'test', 'live' ]:
        encryptedTokens[keyType] = kmsClient.encrypt(
            KeyId=userdata['kms_key']['key_arn'],
            Plaintext=userdata['stripe']['plaintext_{0}_secret_key_token'.format(keyType)].encode('UTF-8'))['CiphertextBlob']


    #pprint.pprint("\nEncrypt results:\n\n{0}".format(encryptResults) )

    return encryptedTokens


def _parseKeyArn(userdata):

    # Validate that it's a valid key ARN
    arnMatches = re.match( r'arn:aws:kms:(.+?):\d+:key/(\S+)$', userdata['kms_key']['key_arn'] )
    if arnMatches is None:
        raise ValueError("Invalid KMS key ARN: {0}".format(userdata['kms_key']['key_arn']) )

    userdata['kms_key'].update( 
        {
            'key_region'    : arnMatches.group(1),
            'key_id'        : arnMatches.group(2)
        }
    )
   

def _createUserdata():
    argParser = argparse.ArgumentParser(description="Create encrypted token for Stripe processing backend")

    argParser.add_argument("access_key_id", 
        help="AWS Access Key ID used to access encryption key")
    argParser.add_argument("secret_access_key", 
        help="AWS Secret Access Key used to access encryption key")
    argParser.add_argument("kms_key_arn", 
        help="ARN of KMS encryption key")
    argParser.add_argument("plaintext_stripe_test_secret_key_token", 
        help="Plaintext (unencrypted) Stripe test secret key token"),
    argParser.add_argument("plaintext_stripe_live_secret_key_token",
        help="Plaintext (unencrypted) Stripe *LIVE* secret key token")

    parsedArgs = argParser.parse_args()

    userdata = {
        'lambda_role': {
            'AWS_ACCESS_KEY_ID'                 : parsedArgs.access_key_id,
            'AWS_SECRET_ACCESS_KEY'             : parsedArgs.secret_access_key
        },

        'kms_key': {
            'key_arn'                           : parsedArgs.kms_key_arn
        },

        'stripe': {
            'plaintext_test_secret_key_token'   : parsedArgs.plaintext_stripe_test_secret_key_token,
            'plaintext_live_secret_key_token'   : parsedArgs.plaintext_stripe_live_secret_key_token
        }
    }

    _parseKeyArn(userdata)

    return userdata


if __name__ == "__main__":
    userdata = _createUserdata()

    # print( "\n{0}".format(pprint.pformat(userdata)) )

    _writeEncryptedTokens( userdata )

    #_testReadEncrypted()
