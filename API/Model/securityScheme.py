from fastapi import Request
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from API.Model.userExceptions import not_authenticated_exception
from API.Model.authData import TOKEN_SEP


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={
                "tokenUrl": tokenUrl,
                "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request):
        cookie_authorization = request.cookies.get("Authorization")

        try:
            authorization_splitted = cookie_authorization.split(TOKEN_SEP)
        except BaseException:
            raise not_authenticated_exception

        if len(authorization_splitted) != 2:
            raise not_authenticated_exception

        bearer = authorization_splitted[0].strip()
        refresh = authorization_splitted[1].strip()

        refresh_splitted = refresh.split(" ")
        if len(refresh_splitted) != 2:
            raise not_authenticated_exception

        refresh_scheme = refresh_splitted[0]
        refresh_token = refresh_splitted[1]

        access_scheme, access_token = get_authorization_scheme_param(
            bearer
        )

        if access_scheme.lower() == "bearer" and refresh_scheme.lower() == "refresh":
            authorization = True
        else:
            authorization = False

        if not authorization or access_scheme.lower(
        ) != "bearer" or refresh_scheme.lower() != "refresh":
            if self.auto_error:
                raise not_authenticated_exception
            else:
                return None

        return access_token, refresh_token
