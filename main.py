# Imports
from itertools import chain
from datetime import datetime, timedelta
from pydantic import EmailStr, ValidationError
from fastapi import FastAPI, Header, Depends, Form, File, UploadFile, status, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from URLS import *
from API.Model.userAPI import *
from API.Model.gameAPI import *
from API.Model.turnAPI import *
from API.Model.voteAPI import *
from API.Model.cardAPI import *
from API.Model.playerAPI import *
from API.Model.spellAPI import *
from API.Model.boardAPI import *
from API.Model.exceptions import *
from API.Model.metadata import *


# Add metadata tags for each module
tags_metadata = list(
    chain.from_iterable([
                        [{"name": "Root", "description": "Root endpoint", }],
                        user_metadata,
                        game_metadata]
                        )
)

app = FastAPI(
    title="Secret Voldemort API",
    description="Secret Voldemort is a multiplayer game based on Secret Hitler where two teams compete against each other for the control of Hogwarts.",
    version="0.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=tags_metadata,
    debug=True
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    # For deploy test allow all origins, otherwise use `origins` constant
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get(
    "/",
    tags=["Root"]
)
async def get_root():
    '''
    Root backend mainpage
    '''

    return "Secret Voldemort API"


@app.post(
    USER_REGISTER_URL,
    status_code=status.HTTP_201_CREATED,
    tags=["Register"]
)
async def user_register(new_user: UserRegisterIn):
    '''
    Register a new user
    '''

    try:
        await register(new_user)
        return {
            "email": new_user.email,
            "result": "success"
        }
    except ValidationError as ve:
        result = []
        for error in ve.errors():
            result.append({ error["loc"][0]: error["msg"] })

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    except HTTPException as http_e:
        raise http_e
    except:
        raise register_exception


@app.post(
    USER_LOGIN_URL,
    status_code=status.HTTP_200_OK,
    tags=["Login"]
)
async def user_login(email: EmailStr = Form(...), password: str = Form(...)):
    '''
    User log in
    '''

    try:
        user = await get_user_profile_by_email(email)
        return await authenticate(user.email, password)
    except Exception as e:
        raise e


@app.get(
    USER_PROFILE_URL,
    status_code=status.HTTP_200_OK,
    tags=["Profile"]
)
async def get_user_public_profile(email: EmailStr):
    '''
    Get user's profile data
    '''

    return await get_user_profile_by_email(email)


@app.get(
    USER_ICON_URL,
    status_code=status.HTTP_200_OK,
    tags=["User icon"]
)
async def get_user_icon(email: EmailStr):
    '''
    Get user's icon
    '''

    return Response(await get_user_icon_by_email(email))


@app.put(
    USER_UPDATE_USERNAME_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update username"]
)
async def user_update_username(
        update_data: UserUpdateUsername,
        Authorization: str = Header(...), user: UserProfile = Depends(get_this_user)):
    '''
    Update user's username
    '''

    try:
        if update_data.email == user.email:
            if await change_username(update_data):
                return {
                    "email": update_data.email,
                    "result": "success"
                }
            else:
                raise unauthorized_exception
        else:
            raise unauthorized_exception
    except ValidationError as ve:
        result = []
        for error in ve.errors():
            result.append({ error["loc"][0]: error["msg"] })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    except Exception as e:
        raise e


@app.put(
    USER_UPDATE_PASSWORD_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update password"]
)
async def user_update_password(
        update_data: UserUpdatePassword,
        Authorization: str = Header(...), user: UserProfile = Depends(get_this_user)):
    '''
    Update user's password
    '''

    try:
        if update_data.email == user.email:
            if await change_password(update_data):
                return {
                    "email": update_data.email,
                    "result": "success"
                }
            else:
                raise unauthorized_exception
        else:
            raise unauthorized_exception
    except ValidationError as ve:
        result = []
        for error in ve.errors():
            result.append({ error["loc"][0]: error["msg"] })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    except Exception as e:
        raise e


@app.put(
    USER_UPDATE_ICON_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update icon"]
)
async def user_update_icon(
        email: EmailStr = Form(...), password: str = Form(...),
        new_icon: UploadFile = File(...), Authorization: str = Header(...),
        user: UserProfile = Depends(get_this_user)):
    '''
    Update user's icon
    '''

    try:
        update_data = UserUpdateIcon(email=email, password=password)

        if update_data.email == user.email:
            if await change_icon(update_data, new_icon):
                return {
                    "email": user.email,
                    "result": "success"
                }
            else:
                raise unauthorized_exception
        else:
            raise unauthorized_exception
    except ValidationError as ve:
        result = []
        for error in ve.errors():
            result.append({ error["loc"][0]: error["msg"] })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    except Exception as e:
        raise e


@app.get(GAME_LIST_URL,
         status_code=status.HTTP_200_OK,
         tags=["List Games"])
async def list_games():
    '''
    List games
    '''

    return list_available_games()


@app.post(GAME_CREATE_URL,
status_code=status.HTTP_201_CREATED,
tags=["Create Game"])
async def create_game(params: GameParams):
    '''
    Create game
    '''

    return create_new_game(game_params=params)


@app.put(GAME_JOIN_URL,
         status_code=status.HTTP_200_OK,
         tags=["Join Game"])
async def join_game(id: int, user_email: EmailParameter):
    '''
    Join game
    '''

    return join_game_with_keys(game_id=id, user_email=user_email.email)


@app.post(GAME_LEAVE_NOT_INIT_URL,
         status_code=status.HTTP_200_OK,
         tags=["Leave not initialized game"])
async def leave_not_init_game(id: int, user_email: EmailParameter):
    '''
    Leave not initialized game
    '''

    return leave_game_not_initialized(game_id=id, user_email=user_email)


@app.put(GAME_INIT_URL,
         status_code=status.HTTP_200_OK,
         tags=["Init Game"])
async def init_game(id: int, player_id: int):
    '''
    Initialize the game
    '''

    return init_game_with_ids(game_id=id, player_id=player_id)


@app.get(GAME_PLAYERS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Players id"]
         )
async def get_player_ids(id: int):
    '''
    Get list of player ids in the game
    '''

    return check_and_get_player_ids(id)


@app.get(GAME_PLAYERS_INFO_URL,
         status_code=status.HTTP_200_OK,
         tags=["Players info"]
         )
async def get_players_info(id: int):
    '''
    Get list of player ids, username and loyalty in the game
    '''

    return check_and_get_players_info(id)


@app.get(GAME_HAS_STARTED_URL,
         status_code=status.HTTP_200_OK,
         tags=["Has the Game started"])
async def has_the_game_started(id: int, player_id: int):
    '''
    Check if the game has started
    '''

    return check_if_game_started(game_id=id, player_id=player_id)


@app.put(GAME_NEW_MINISTER_URL,
         status_code=status.HTTP_200_OK,
         tags=["Next minister candidate"]
         )
async def select_MM(id: int):
    '''
    Get next player id candidate for minister
    '''

    return get_next_MM(id)


@app.get(GAME_AVAILABLE_DIRECTOR_URL,
         status_code=status.HTTP_200_OK,
         tags=["Available director candidates id's"]
         )
async def get_director_candidates(id: int):
    '''
    Get available director candidates id's
    '''

    return check_and_get_director_candidates(id)


@app.put(GAME_SET_DIRECTOR_URL,
         status_code=status.HTTP_200_OK,
         tags=["Set director candidate"]
         )
async def set_director_candidate(id: int, formula: TurnFormula):
    '''
    Set director candidate in current turn
    '''

    return check_and_set_director_candidate(id, formula.minister_id, formula.director_id)


@app.get(GAME_CANDIDATES_URL,
         status_code=status.HTTP_200_OK,
         tags=["Get vote formula"]
         )
async def get_vote_formula(id: int):
    '''
    Get the minister-director formula
    '''

    return get_vote_candidates(game_id=id)


@app.put(GAME_VOTE_URL,
         status_code=status.HTTP_200_OK,
         tags=["Submit a vote"]
         )
async def vote(id: int, player_vote: PlayerVote = Body(..., description="Player data: id and vote")):
    '''
    Submit a vote
    '''

    return check_and_vote_candidate(id, player_vote.id, player_vote.vote)


@app.put(GAME_RESULT_URL,
         status_code=status.HTTP_200_OK,
         tags=["Vote result"]
         )
async def vote_result(id: int):
    '''
    Get the vote result
    '''

    return check_and_get_vote_result(id)


@app.put(GAME_NOTIFY_REJECTED_URL,
         status_code=status.HTTP_200_OK,
         tags=["Notify that knows about rejection"]
         )
async def reject_notify(id: int, player_id: int):
    '''
    Notify that knows about rejection of candidates
    '''

    return check_and_reject_notify(id, player_id)


@app.get(GAME_GET_3_CARDS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Take three cards"]
         )
async def get_cards(id: int, player_id: int):
    '''
    Get three cards
    '''

    return check_and_get_3_cards(game_id=id, player_id=player_id)


@app.put(GAME_DISCARD_URL,
         status_code=status.HTTP_200_OK,
         tags=["Discard card"])
async def discard(id: int, discard_data: DiscardData):
    '''
    Discard card
    '''

    return discard_selected_card(game_id=id, discard_data=discard_data)


@app.get(GAME_DIRECTOR_CARDS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Not discarded cards"])
async def get_director_cards_to_promulgate(id: int, player_id: int):
    '''
    Get the remaining two cards for the Director to promulgate
    '''

    return get_cards_for_director(game_id=id, player_id=player_id)


@app.put(GAME_SET_EXPELLIARMUS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Start expelliarmus"])
async def expelliarmus(id: int, director_id: int):
    '''
    Director starts expelliarmus
    '''

    return check_and_start_expelliarmus(id, director_id)


@app.put(GAME_CONSENT_EXPELLIARMUS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Accept/decline expelliarmus"])
async def expelliarmus(id: int, minister_data: MinisterExpelliarmusConsent):
    '''
    Minister consent expelliarmus
    '''

    return check_and_consent_expelliarmus(id, minister_data)


@app.put(GAME_PROMULGATE_URL,
         status_code=status.HTTP_200_OK,
         tags=["Promulgate card"]
         )
async def promulgate_card(id: int, promulgate: PlayerPromulgate):
    '''
    Promulgate a card
    '''

    return promulgate_in_game(
        id, promulgate.player_id, promulgate.to_promulgate)


@app.get(GAME_SPELL_URL,
         status_code=status.HTTP_200_OK,
         tags=["Available spell"]
         )
async def get_available_spell(id: int):
    '''
    Get available spell in current turn
    '''

    return check_and_get_available_spell(id)


@app.put(GAME_EXECUTE_SPELL_URL,
         status_code=status.HTTP_200_OK,
         tags=["Execute spell"]
         )
async def execute_spell(id: int, spell: Spell, spell_data: SpellData):
    '''
    Execute a spell
    '''

    if spell == Spell.GUESSING:
        return check_and_execute_guessing(id, spell_data)
    elif spell == Spell.CRUCIO:
        return check_and_execute_crucio(id, spell_data)
    elif spell == Spell.AVADA_KEDAVRA:
        return check_and_execute_avada_kedavra(id, spell_data)
    elif spell == Spell.IMPERIUS:
        return check_and_execute_imperius(id, spell_data)


@app.get(GAME_STATUS_URL,
         status_code=status.HTTP_200_OK,
         tags=["Game state"]
         )
async def get_game_status(id: int):
    '''
    Check the game status
    '''

    return game_status(id)


@app.put(GAME_END_NOTIFY_URL,
         status_code=status.HTTP_200_OK,
         tags=["Notify knowledge about ending"]
         )
async def end_game_notify(id: int, player_id: int):
    '''
    Notify that player knows about ending
    '''

    return check_and_end_game_notify(id, player_id)


@app.post(GAME_LEAVE_URL,
         status_code=status.HTTP_200_OK,
         tags=["Leave Game"])
async def leave_game(id: int, player_id: int):
    '''
    Leave initialized game
    '''

    return leave_game_initialized(game_id=id, player_id=player_id)
