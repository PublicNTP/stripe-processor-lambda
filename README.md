# stripe-processor-lambda

## Overview

### Description

`strip-processor-lambda` is a package that simplifies the process of 
setting up a system to receive payments/donations via Stripe.

### Motivation

When I was undertaking this project, I paused and asked myself, 
"Do I need to write this software? Can I leveraging existing code
on the Internet to do this? 

Sort of.

First, I didn't find any written in Python, which is my preferred
language a the moment.

Second, and more importantly, all the ones I found in my search 
stored the payment key unecrypted, which is not something I'm 
personally comfortable with. 

Thus, I wrote this code to leverage a technique to protect the
secret token which I first encountered when using the 
New York Times Labs' [github-s3-deploy](https://github.com/nytlabs/github-s3-deploy) 
tool:

1. A symmetric key is created using the AWS Key Management System (KMS) 
2. The plaintext secret token is encrypted using the KMS key
3. The encrypted secret token is stored with the Lambda function
4. At runtime, the Lambda function decrypts the secret token during its
execution

This approach means that the secret token is only unencrypted 
durign execution of the Lambda function, thus reducing the 
vulnerability of the secret token to being compromised/leaked.

## Installation

### Create Identity and Access Management (IAM) users/roles

#### Lambda function

The Lambda function executes with the permissions of the IAM user/role
it is configured to execute as. We're creating a dedicated role for this
Lambda function so the function runs with the least permissions possible.

1. Go to the [IAM roles](https://console.aws.amazon.com/iam/home#/roles) page
and click the **Create role** button
2. AWS will ask what service will use this role. Select **Lambda** and then 
click **Next: Permissions**
3. Do not attach any permissions policies (simply click **Next: Review** when 
presented with the list of possible policies)
4. On the **Review** page, enter a role name and description as fits your
needs


#### Secret token encrypter

You'll need to create a IAM user for the developer who will perform the initial
encryption of the Stripe secret token.

1. Go to the [IAM users](https://console.aws.amazon.com/iam/home#/users) page
and click the **Add user** button
2. Set the name for the account, and then select _only_ the "Programmatic access"
checkbox under **Access Type**. Click **Next: Permissions**
3. Do not add any permissions for the account, click **Next: Review**
4. Ignore the warning that AWS (helpfully!) shows about creating a user with zero 
permissions, and click **Create user**
5. Click the option to display the user's _Secret access key_. Record both their
_Access key ID_ and _Secret access key_. Once you've ensured you got both pieces
of data correct, click **Close**


### Create encryption key

The lambda function decrypts the Stripe secret token at runtime. For this to 
work, an encryption key has to be created that will be used to both encrypt
the secret token (done once), and decrypt the encrypted version of the secret
token (performed every time the function executes).

1. Go to the IAM [Encryption keys](https://console.aws.amazon.com/iam/home#/encryptionKeys/)
page
2. Click **Create key**
3. Enter alias and description, click **Next Step**
4. Enter any tags that you feel will help organize/identify the key, then click **Next Step**
5. On the "Key Administrators" page, click **Next Step**
6. On the "Key Usage Permissions" page, select the following:
    * The IAM role for the Lambda function 
    * The encrypter user 
7. Click **Next Step**
8. On the policy review page, click **Create key**
9. Click the newly-created key and record the followign data from the **ARN** (format: 
`arn:aws:kms:[region]:[account_id]:key/[key_id]`
    * `region`
    * `key_id`

### Create working directory/git repository for Lambda function

Now is the point where you should create a directory to work from. 
If you are going to work in `~/projects/sample_organization/stripe-processor` (for example),
run:

```Shell
$ mkdir -p ~/projects/sample_organization
$ cd ~/projects/sample_organization
$ git clone https://github.com/PublicNTP/stripe-processor-lambda stripe-processor
```

### Make sure that the latest Python 3 PIP is installed

On Ubuntu 16.04, this is accomplished by 
```Shell
$ sudo apt-get -y install python3-pip
$ pip3 install --upgrade --user pip
```

### Ensure latest version of AWS CLI is installed

``` Shell
$ pip3 install --upgrade --user awscli
```

### Prepare to encrypt Stripe secret token 

The info you'll need at your fingertips to complete the step following this one:

1. Token Encrypter user credentials (from the **Installation > Create 
Identity and Access Management (IAM) users/roles > Secret token encrypter** step):
    * Access key ID
    * Secret access key
2. The details of the KMS key (from the 
**Installation > Create encryption key** step above):
    * Key Region
    * Key ID
3. Stripe "Live key token"
    * Go to [API Keys](https://dashboard.stripe.com/account/apikeys) section of the Stripe Dashboard
    * Click **Reveal live key token**

### Encrypt Stripe secret token

Run:

``` Shell
~/bin/encryptStripeSecretToken
```

The `encryptStripeSecretToken` script prompts the user for all data listed in the 
previous section. It then accesses the cryptographic key material specified, and uses
it to create the file `stripe_live_key_token.encrypted`

### Remove key usage permissions for encrypter user

### Remove encrypter user account



## Legal

`stripe-processor-lambda` is copyrighted by [PublicNTP](https://publicntp.org), Inc., 
open-sourced under the [MIT License](https://en.wikipedia.org/wiki/MIT_License). 

Refer to the
[LICENSE](https://github.com/PublicNTP/stripe-processor-lambda/blob/master/LICENSE) 
file for more information.
