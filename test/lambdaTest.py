from __future__ import print_function
import logging
import StripeProcessor

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    paymentStatus = StripeProcessor.process_payment(
        { 
            'body': {
                'payment_info': {
                    'required': {
                        'amount'        : 762,
                        'currency'      : 'usd',
                        'source'        : 'tok_visa',
                        'description'   : 'Test donation'
                    },

                    'optional': {
                        'name': {
                            'Last'  : 'Person', 
                            'First' : 'Test' 
                        },

                        'address': {
                            'street_lines'          : [
                                '123 N 7608 E',
                                'Apt 819'
                            ],
                            'city'                  : 'YupACity',
                            'state_province_region' : 'QC',
                            'country'               : 'CA'
                        },

                        'email' : 'test.person@test.email',

                        'phone' : '+44-234233347'
                    }
                }
            }
        },

        None
    )

    print( "Payment processing status: {0}".format(paymentStatus) )
