import secrets
def generate_api_key():
    generated_key = "KV_" + secrets.token_urlsafe(32)
    return generated_key