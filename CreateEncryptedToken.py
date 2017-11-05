import pprint
import re


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
            'data_key'          : 'access_key_id'
        },

        {
            'user_prompt'       : 'Secret Access Key',
            'data_group'        : 'lambda_role',
            'data_key'          : 'secret_access_key',
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


def main():
    userdata = _getUserdata()

    print( "\n{0}".format(pprint.pformat(userdata)) )

     
if __name__ == "__main__":
    main()
