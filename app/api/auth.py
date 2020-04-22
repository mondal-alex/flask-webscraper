from flask_httpauth import HTTPBasicAuth
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()

# verify the username/password combo in firebase
@basic_auth.verify_password
def verify_password(username, password):
    return (username == "username") and password == "password"

@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)
