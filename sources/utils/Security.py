"""
    Utility functions related to security.
"""
import hashlib
import hmac
from flask import current_app


def validate_github_webhook_signature(payload, secret):
    """
        Verification of the Github Webhook signature.
        From https://gist.github.com/andrewfraley/0229f59a11d76373f11b5d9d8c6809bc
    """

    # Get the signature from the payload
    signature_header = payload.headers['X-Hub-Signature-256']
    sha_name, github_signature = signature_header.split('=')
    if sha_name != 'sha256':
        current_app.logger.error('ERROR: X-Hub-Signature-256 in payload headers was not sha256=****')
        return False

    # Create our own signature
    body = payload.data
    local_signature = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)

    # See if they match
    return hmac.compare_digest(local_signature.hexdigest(), github_signature)
