"""
    Utility functions related to security.
"""
import hashlib
import hmac


def validate_github_webhook_signature(payload, secret):
    """
        Verification of the Github Webhook signature.
        From https://gist.github.com/andrewfraley/0229f59a11d76373f11b5d9d8c6809bc
    """

    # Get the signature from the payload
    signature_header = payload.headers['X-Hub-Signature']
    sha_name, github_signature = signature_header.split('=')
    if sha_name != 'sha1':
        print('ERROR: X-Hub-Signature in payload headers was not sha1=****')
        return False

    # Create our own signature
    body = payload.data
    local_signature = hmac.new(secret.encode('utf-8'), msg=body, digestmod=hashlib.sha1)

    # See if they match
    return hmac.compare_digest(local_signature.hexdigest(), github_signature)
