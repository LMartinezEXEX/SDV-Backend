# Imports
from datetime import datetime, timedelta
from typing   import Optional
from pydantic import EmailStr
from fastapi  import FastAPI, Depends, Body, File, UploadFile, HTTPException, status
from API.Model.gameModel import *
#from Database.game_functions import join_game_with_ids, init_game_with_ids

# Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from API.Model.auth   import ACCESS_TOKEN_EXPIRE_MINUTES

# User Model
from API.Model.userModel import UserRegisterIn, UserRegisterOut, UserLoginData, Token, TokenData,\
     oauth2_scheme, get_user_by_email, register, authenticate, new_access_token, get_user_if_active, change_username, change_password, change_icon

app = FastAPI()

# Root
@app.get("/")
async def get_root():
    return "Secret Voldemort API"

# Get by email
@app.get("/user/{email}")
async def get_user(email: EmailStr):
    return get_user_by_email(email)

# Register
@app.post(
    "/user/register/",
    response_model = UserRegisterOut,
    status_code = status.HTTP_201_CREATED
    )
async def user_register(new_user: UserRegisterIn):
    dict_register = register(new_user)
    if dict_register["created"]:
        return UserRegisterOut(
            username = new_user.username,
            operation_result = "Ok"
        )
    else:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = dict_register["message"]
        )

# Login
@app.post(
    "/user/login/",
    response_model = Token,
    status_code = status.HTTP_302_FOUND
)
async def user_login(email: EmailStr = Body(...), password: str = Body(...)):
    user = None
    # Spec requires the field username, but there we store the email
    user = authenticate(email, password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = new_access_token(
        data = { "sub": email }, expires_delta = access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Logout

# Profile
@app.get(
    "/user/profile/",
    response_model = UserLoginData
    )
async def profile(user: UserLoginData = Depends(get_user_if_active)):
    return user

# Update username
@app.put(
    "/user/update/",
    status_code = status.HTTP_200_OK
    )
async def user_update(email: EmailStr = Body(...), new_username: str = Body(...)):
    if change_username(email, new_username):
        return { "success": True }
    else:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            success = False,
            detail = "Failed to update"
        )

# Update password
#@app.put(
#    "/user/update/",
#    status_code = status.HTTP_200_OK
#    )
#async def user_update(email: EmailStr = Body(...), old_password: str = Body(...), new_password: str = Body(...)):
#    if change_password(email, old_password, new_password):
#        return { "success": True }
#    else:
#        raise HTTPException(
#            status_code = status.HTTP_400_BAD_REQUEST,
#            success = False,
#            detail = "Failed to update"
#        )

# Update icon
#@app.put(
#    "/user/update/",
#    status_code = status.HTTP_200_OK
#    )
#async def user_update(email: EmailStr, new_icon: UploadFile = File(...) ):
#    if change_icon(email, new_icon):
#        return { "success": True }
#    else:
#        raise HTTPException(
#            status_code = status.HTTP_400_BAD_REQUEST,
#            success = False,
#            detail = "Failed to update"
#        )


# Create Game
@app.post("/game/create/",
          status_code = status.HTTP_200_OK)
async def create_game(params: GameParams):
    new_game_id = create_new_game(game_params=params)
    if not new_game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cant create game"
        )
    return new_game_id

# Join Game
@app.put("/game/join/{id}",
         status_code = status.HTTP_200_OK)
async def join_game(keys: JoinModel):
    res = join_game_with_keys(keys=keys)
    if not res.op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.message
        )
    return {"message": res.message}


# Init Game
@app.put("/game/init/", status_code = status.HTTP_200_OK)
async def init_game(ids: InitGameIds):
    res = init_game_with_ids(ids)
    if not res.op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.message
        )
    return {"message": res.message}
