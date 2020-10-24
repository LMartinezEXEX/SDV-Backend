# For testing this can be generated with "openssl rand -hex 32"
# All this parameters should be move out from project's scope, maybe to env variables
SECRET_KEY = "e2c67a019a432e9c57c9bc2c0b19e2b0ec8b67ea3f70a0dda2d5018d8440b21f"
ALGORITHM = "HS256"

# Session related parameters
# Domain for testing purposes, recommended practice. localtest.me resolves to 127.0.0.1
DOMAIN  = "localtest.me"

TOKEN_SEP = "|"

ACCESS_TOKEN_EXPIRES_MINUTES  = 10
REFRESH_TOKEN_EXPIRES_MINUTES = 20

EXPIRES_ACCESS  = ACCESS_TOKEN_EXPIRES_MINUTES  * 60 * 1000
EXPIRES_REFRESH = REFRESH_TOKEN_EXPIRES_MINUTES * 60 * 1000


REFRESH_TOKEN_LENGTH = 32
