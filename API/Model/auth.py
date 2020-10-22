# For testing this can be generated with "openssl rand -hex 32"
# All this parameters should be move out from project's scope, maybe to env variables
SECRET_KEY = "e2c67a019a432e9c57c9bc2c0b19e2b0ec8b67ea3f70a0dda2d5018d8440b21f"
ALGORITHM = "HS256"
# 24 hours for a token
ACCESS_TOKEN_EXPIRE_MINUTES = 24*60