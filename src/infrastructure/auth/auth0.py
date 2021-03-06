import json
import os
from urllib.request import urlopen
from urllib.parse import urljoin

from jose import jwt

from exceptions.auth import AuthError


def requires_auth(token, AUTH0_DOMAIN: str = ""):
    """
    ref: https://auth0.com/docs/quickstart/backend/python#create-the-jwt-validation-decorator

    Determines if the Access Token is valid
    """
    AUTH0_DOMAIN = os.environ.get("DAIZU_AUTH0_DOMAIN", "")
    AUTH0_AUDIENCE = os.environ.get("DAIZU_AUTH0_API_AUDIENCE", "")
    AUTH0_ALGORITHMS = ["RS256"]

    print(AUTH0_DOMAIN)
    print(AUTH0_AUDIENCE)
    print(f"https://{AUTH0_DOMAIN}/")

    jwks_url = urljoin("https://" + AUTH0_DOMAIN, "/.well-known/jwks.json")
    body = urlopen(jwks_url).read()
    jwks = json.loads(body)

    unverified_header = jwt.get_unverified_header(token)
    rsa_key = dict()

    for key in jwks.get("keys"):
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
        except jwt.ExpiredSignatureError:
            raise AuthError(detail="token is expired")
        except jwt.JWTClaimsError:
            raise AuthError(
                detail="incorrect claims, please check the audience and issuer"
            )
        except Exception:
            raise AuthError(detail="Unable to parse authentication token.")

    #    _request_ctx_stack.top.current_user = payload
    #    return f(*args, **kwargs)
    # raise AuthError(detail="Unable to find appropriate key")


def requires_scope(required_scope: str, token: str):
    """
    ref: https://auth0.com/docs/quickstart/backend/python#validate-scopes

    Determines if the required scope is present in the Access Token
    """
    unverified_claims = jwt.get_unverified_claims(token)

    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False
