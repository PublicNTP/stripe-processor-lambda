# stripe-processor-lambda

## Overview

### Description

`strip-processor-lambda` is a package that simplifies the process of 
setting up a system to receive payments/donations via Stripe.

### Don't a lot of other pieces of code do this already?

Yes. Sort of.

The ones I found all store the payment key unecrypted, which is not
something I'm personally comfortable with. So I wrote a version
which leverages AWS Key Managment System (KMS) to decrypt the payment 
token for a fraction of a second during the function's execution, 
thus reducing the vulnerability of the secret token to being 
compromised/leaked.

## Configuration/Setup

### Create Identity and Access Managment (IAM) role

The lambda function executes with the permissions of the IAM user/role
it is configured to execute as. We're creating a dedicated role for this
Lambda function so the function runs with the least permissions possible.

1. Go to the [IAM role](https://console.aws.amazon.com/iam/home#/roles) page
and click the **Create role** button.
2. AWS will ask what service will use this role. Select **Lambda** and then 
click **Next: Permissions**
3. Do not attach any permissions policies (simply click **Next: Review** when 
presented with the list of possible policies)
4. On the **Review** page, enter a role name and description as fits your
needs.

### Create encryption key

The lambda function decrypts the Stripe secret token at runtime. For this to 
work, an encryption key has to be created that will be used to both encrypt
the secret token (done once), and decrypt the encrypted version of the secret
token (performed every time the function executes).


## Legal

`stripe-processor-lambda` is copyrighted by [PublicNTP](https://publicntp.org), Inc., 
open-sourced under the [MIT License](https://en.wikipedia.org/wiki/MIT_License). 

Refer to the
[LICENSE](https://github.com/PublicNTP/stripe-processor-lambda/blob/master/LICENSE) 
file for more information.
