from fastapi import Request
from fastapi.security import OAuth2, OAuth2PasswordBearer
from API.Model.exceptions import not_authenticated_exception
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordBearer(OAuth2):
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
        authorization = request.headers.get("Authorization")

        access_scheme, access_token = get_authorization_scheme_param(
            authorization
        )

        if access_scheme.lower() != "bearer":
            if self.auto_error:
                raise not_authenticated_exception
            else:
                return None

        return access_token
