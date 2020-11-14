from test_functions import *
from pydantic import EmailStr


# --------  SET UP ----------------------------------

@pytest.fixture(scope="session", autouse=True)
def init_data(request):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    request.addfinalizer(clean_db)


# --------  TEAR-DOWN  ------------------------------


def clean_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()


# ---------  TESTS  ---------------------------------


def test_create_game_with_invalid_email():
     game_params = {"email": 'fake_email@gmail.com', "name": 'Fake Name', "min_players": 5, "max_players": 5}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 404
     assert response.json() == {"detail": "User not found"} 



def test_create_game_min_players_less_than_5():
     users = users_factory(amount_users=1)
     game_params = {"email": users[0], "name": users[0], "min_players": 2, "max_players": 10}
     response = start_new_game(game_params)

     assert response.status_code == 409
     assert response.json() == {"detail": "The game must have at least 5 players"}


def test_create_game_max_players_more_than_10():
     users = users_factory(amount_users=1)
     game_params = {"email": users[0], "name": users[0], "min_players": 5, "max_players": 15}
     response = start_new_game(game_params)

     assert response.status_code == 409
     assert response.json() == {"detail": "The game must have less than 10 players"} 

     
def test_incoherent_amount_of_players_to_create_game():
     users = users_factory(amount_users=1)
     game_params = {"email": users[0], "name": users[0], "min_players": 15, "max_players": 6}
     response = start_new_game(game_params)

     assert response.status_code == 409
     assert response.json() == {"detail": "The minimum of players is higher than the maximum"} 


def test_create_game_correctly():
     users = users_factory(amount_users=1)
     game_params = {"email": users[0], "name": users[0], "min_players": 5, "max_players": 10}
     response = start_new_game(game_params)
     game_id = response.json().get("Game_Id")
     player_id = response.json().get("Player_Id")

     assert response.status_code == 201
     assert response.json() == {"Game_Id": game_id, "Player_Id": player_id} 


def test_join_game_with_invalid_email():     
     invalid_user = {"email": "fake_email@gmail.com"}
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     response = join_a_game(game_id=game_data[0], user_email=invalid_user)

     assert response.status_code == 404
     assert response.json() == {"detail": "User not found"}


def test_join_game_with_invalid_game_id():
     user_joining = users_factory(amount_users=1)
     user_email = {"email": user_joining[0]}
     fake_game_id = 10000
     response = join_a_game(game_id=fake_game_id, user_email=user_email)

     assert response.status_code == 404
     assert response.json() == {"detail": "Game not found"}


def test_join_game_with_max_reached():
     game_data = game_factory(players_cuantity=10, turns_cuantity=0, game_state=0)
     users = users_factory(amount_users=1)
     user_email = {"email": users[0]}
     response = join_a_game(game_id=game_data[0], user_email=user_email)

     assert response.status_code == 409
     assert response.json() == {"detail": "The game has reach the maximum amount of players"}


def test_join_game():
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     user = users_factory(amount_users=1)
     user_email = {"email": user[0]}
     response = join_a_game(game_id=game_data[0], user_email=user_email)

     assert response.status_code == 200
     assert is_player_in_game_by_id(game_id=game_data[0], player_id=game_data[1])


def test_init_bad_game_id():
     fake_game_id = 10000
     response = init_the_game(game_id=fake_game_id, player_id=50)
     
     assert response.status_code == 404
     assert response.json() == {"detail": "Game not found"}


def test_init_bad_player_id():
     fake_player_id = 10000
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     response = init_the_game(game_id=game_data[0], player_id=fake_player_id)

     assert response.status_code == 404
     assert response.json() == {"detail": "Player not found"}


def test_init_game_without_minimum_players():
     game_data = game_factory(players_cuantity=4, turns_cuantity=0, game_state=0)
     response = init_the_game(game_id=game_data[0], player_id=game_data[1])

     assert response.status_code == 409
     assert response.json() == {"detail": "The game has not reach the minimum amount of players"}

     
def test_init_game_not_owner():
     users = users_factory(amount_users=5)
     game_params = {"email": users[0], "name": users[0], "min_players": 5, "max_players": 10}
     response_create = start_new_game(game_params)
     game_id = response_create.json().get("Game_Id")
     for i in range(1,4):
          user_email = {"email": users[i]}
          response_join = join_a_game(game_id=game_id, user_email=user_email)
     last_player_id = response_join.json().get("Player_Id")
     response = init_the_game(game_id=game_id, player_id=last_player_id)

     assert response.status_code == 409
     assert response.json() == {"detail": "You cant start the game, you are not the owner!"}


def test_init_game_already_initialized():
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=1)
     response = init_the_game(game_id=game_data[0], player_id=game_data[1])

     assert response.status_code == 409
     assert response.json() == {"detail": "The game has started"}


def test_init_game_finalized():
     game_data = game_factory(players_cuantity=5, turns_cuantity=1, game_state=2)
     response = init_the_game(game_id=game_data[0], player_id=game_data[1])

     assert response.status_code == 409
     assert response.json() == {"detail": "The game has finished"}


def test_init_game_correctly():
     game_data = game_factory(players_cuantity=5, turns_cuantity=1, game_state=0)
     response = init_the_game(game_id=game_data[0], player_id=game_data[1])

     assert response.status_code == 200


def test_check_loyalty_5_players():
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_check_loyalty_6_players():
     game_data = game_factory(players_cuantity=6, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_check_loyalty_7_players():
     game_data = game_factory(players_cuantity=7, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_check_loyalty_8_players():
     game_data = game_factory(players_cuantity=8, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_check_loyalty_9_players():
     game_data = game_factory(players_cuantity=9, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_check_loyalty_10_players():
     game_data = game_factory(players_cuantity=10, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     result = check_players_loyalty(game_data[0])
     
     assert result == 1


def test_count_roles_with_5_players():
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 3
     assert death_eaters == 1
     assert voldemort == 1


def test_count_roles_with_6_players():
     game_data = game_factory(players_cuantity=6, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 4
     assert death_eaters == 1
     assert voldemort == 1


def test_count_roles_with_7_players():
     game_data = game_factory(players_cuantity=7, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 4
     assert death_eaters == 2
     assert voldemort == 1


def test_count_roles_with_8_players():
     game_data = game_factory(players_cuantity=8, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 5
     assert death_eaters == 2
     assert voldemort == 1


def test_count_roles_with_9_players():
     game_data = game_factory(players_cuantity=9, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 5
     assert death_eaters == 3
     assert voldemort == 1


def test_count_roles_with_10_players():
     game_data = game_factory(players_cuantity=10, turns_cuantity=0, game_state=0)
     init_the_game(game_id=game_data[0], player_id=game_data[1])
     fenixes = count_roles_from_game(game_id=game_data[0], rol="Fenix Order")
     death_eaters = count_roles_from_game(game_id=game_data[0], rol="Death Eater")
     voldemort = count_roles_from_game(game_id=game_data[0], rol="Voldemort")

     assert fenixes == 6
     assert death_eaters == 3
     assert voldemort == 1


def test_minister_discard():
     game_data = game_factory(players_cuantity=5, turns_cuantity=1)
     cards = get_3_cards(game_id=game_data[0])
     to_discard = cards.json().get("cards")
     discard_data = {"player_id": game_data[1], "to_discard": to_discard[0]}
     response = card_discard(game_id=game_data[0], discard_data=discard_data)

     assert response.status_code == 200


def test_discard_not_minister():
     fake_player_id = 5000
     game_data = game_factory(players_cuantity=5, turns_cuantity=1)
     cards = get_3_cards(game_id=game_data[0])
     to_discard = cards.json().get("cards")
     discard_data = {"player_id": fake_player_id, "to_discard": to_discard[0]}
     response = card_discard(game_id=game_data[0], discard_data=discard_data)

     assert response.status_code == 409
     assert response.json() == {"detail": "Player is not minister"}


def test_get_not_discarded_cards():
     game_data = game_factory(players_cuantity=5, turns_cuantity=1)
     cards = get_3_cards(game_id=game_data[0])
     to_discard = cards.json().get("cards")
     discard_data = {"player_id": game_data[1], "to_discard": to_discard[0]} 
     card_discard(game_id=game_data[0], discard_data=discard_data)
     not_dis_cards = {"cards": [to_discard[1], to_discard[2]]}
     response = get_not_discarded_cards(game_id=game_data[0], player_id=game_data[1])

     assert response.status_code == 200
     assert response.json() == not_dis_cards
     

def test_get_vote_formula_dir_not_selected():
     game_data = game_factory(players_cuantity=5, turns_cuantity=1)
     response = get_vote_formula(game_id=game_data[0])
     minister_id = response.json().get("minister_id")
     director_id = response.json().get("director_id")

     assert response.status_code == 200
     assert minister_id == director_id


def test_game_state_not_initialized():
     game_data = game_factory(players_cuantity=5, turns_cuantity=0, game_state=0)
     response = game_state_in_pregame(game_id=game_data[0], player_id=game_data[1])
     users = response.json().get("users")

     assert response.status_code == 200
     assert len(users) == 5