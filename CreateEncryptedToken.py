from __future__ import print_function
import pprint
import re
import boto3
import os

_encryptedTokenFile = 'lambda/stripe_encrypted_secret_key_token.dat'

def _testReadEncrypted():
    with open( _encryptedTokenFile, 'rb' ) as readHandle:
        encryptedBytes = readHandle.read()

    kmsClient = boto3.client('kms', region_name=userdata['kms_key']['key_region'])

    print( "Decrypted token: {0}".format(
        kmsClient.decrypt(CiphertextBlob=encryptedBytes)['Plaintext'].decode('UTF-8')) )

                


def _writeEncryptedTokenToDisk(encryptedTokenBytes):
    with open( _encryptedTokenFile, 'wb') as fileHandle:
        fileHandle.write(encryptedTokenBytes)


def _encryptToken(userdata):

    # Update our running environment with the values that set access key id/secret access key
    os.environ.update( userdata['lambda_role'] )
     
    kmsClient = boto3.client('kms', region_name=userdata['kms_key']['key_region'])

    encryptResults = kmsClient.encrypt(
        KeyId=userdata['kms_key']['key_arn'],
        Plaintext=userdata['stripe']['secret_key_token'].encode('UTF-8') )

    #pprint.pprint("\nEncrypt results:\n\n{0}".format(encryptResults) )

    return encryptResults['CiphertextBlob']


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
   

def _getUserdata():
    userdata = {}
    promptData = [
        {
            'user_prompt'       : 'Access Key ID',
            'data_group'        : 'lambda_role',
            'data_key'          : 'AWS_ACCESS_KEY_ID'
        },

        {
            'user_prompt'       : 'Secret Access Key',
            'data_group'        : 'lambda_role',
            'data_key'          : 'AWS_SECRET_ACCESS_KEY'
        },

        {
            'user_prompt'       : 'AWS KMS encryption key for secret token',
            'data_group'        : 'kms_key',
            'data_key'          : 'key_arn'
        },

        {
            'user_prompt'       : 'Stripe Secret Key Token',
            'data_group'        : 'stripe',
            'data_key'          : 'secret_key_token'
        }
    ]

    for currPrompt in promptData:
        if currPrompt['data_group'] not in userdata:
            userdata[currPrompt['data_group']] = {}
        userdata[currPrompt['data_group']][currPrompt['data_key']] = \
            input( "Please input the {0}: ".format( currPrompt['user_prompt']) ).strip()

    _parseKeyArn(userdata)

    return userdata


if __name__ == "__main__":
    userdata = _getUserdata()

    # print( "\n{0}".format(pprint.pformat(userdata)) )

    _writeEncryptedTokenToDisk( _encryptToken(userdata) )

    #_testReadEncrypted()
