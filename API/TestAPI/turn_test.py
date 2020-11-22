from API.TestAPI.test_functions import *
from Database.turn_functions import create_first_turn

# -SET-UP-----------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def init_data(request):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    request.addfinalizer(clean_db)


# -TEAR-DOWN--------------------------------------------------------------------



def clean_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()


# TESTS--------------------------------------------------------------------------

'''
Test correct response when trying to take action in a game that hasn't started
'''


def test_action_in_uninitialized_game():
    game_data = game_factory(5, 1, False, 1, False, 0, 0, 0)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 409
    assert response.json() == {"detail": "Game hasn't started"}


'''
Test correct response when trying to take action in a finished game
'''


def test_action_in_finished_game():
    game_data = game_factory(5, 1, False, 3)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 409
    assert response.json() == {"detail": "The game has finished"}


'''
Test correct response when trying to take action in a unexisting game
'''


def test_action_in_unexisting_game():
    response = start_new_turn(game_id=64)

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


'''
Test correct response when asked for next minister candidate
'''


def test_candidate_minister():
    game_data = game_factory(5, 0)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1]+1}


'''
Test correct turn assignment in minister candidate position
'''


def test_ciclic_candidate_minister():
    game_data = game_factory(5, 3)

    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 1}


'''
Test a dead player can't be selected as minister candidate
'''


def test_candidate_minister_when_dead():
    game_data = game_factory(5, 0, True, 1, True, 1)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 2}


'''
Test correct turn assignment in minister candidate when dead players are present
'''


def test_ciclic_candidate_minister_when_dead():
    game_data = game_factory(5, 12, True, 1, True, 2)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1]+1}


'''
Test correct cards obtained from database
'''


@db_session()
def test_get_cards():
    game_data = game_factory(7, 12)
    response = get_3_cards(game_id=game_data[0], player_id=game_data[1])

    cards = select(
        c for c in Card if c.game.id == game_data[0]).order_by(
        Card.order)[:]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}


'''
Test take cards twice in the same turn
'''


@db_session()
def test_get_cards_twice_in_same_turn():
    game_data = game_factory(5, 6)
    get_3_cards(game_id=game_data[0], player_id=game_data[1])

    response = get_3_cards(game_id=game_data[0], player_id=game_data[1])

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Already taken the cards in this turn"}


'''
Test correct response when a player vote
'''


def test_one_vote_count():
    game_data = game_factory(7, 1)
    response = player_vote(
        game_id=game_data[0],
        player_id=game_data[1],
        vote=True)

    assert response.status_code == 200
    assert response.json() == {"votes": 1}


'''
Test correct response when several player vote
'''


def test_several_vote_count():
    game_data = game_factory(5, 0)
    response = None

    votes = [True, False, True, True, False]
    for i in range(5):
        response = player_vote(
            game_id=game_data[0],
            player_id=game_data[1] + i,
            vote=votes[i])

    assert response.status_code == 200
    assert response.json() == {"votes": 5}


'''
Test a player can't vote in a game it is not in
'''


def test_player_vote_in_game_its_not_in():
    game_data = game_factory(7, 5)
    response = player_vote(
        game_id=game_data[0],
        player_id=game_data[1] + 40,
        vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not in this game"}


'''
Assert all players voted before giving the final result
'''


def test_get_result_when_votes_missing():
    game_data = game_factory(5, 1)
    response = client.put('game/{}/result'.format(game_data[0]))

    assert response.status_code == 409
    assert response.json() == {"detail": "Vote's missing"}


'''
Test correct result when all players voted
'''


def test_get_result():
    game_data = game_factory(7, 0)

    votes = [True, True, False, True, True, False, False]
    voted_lumos = [
        game_data[1],
        game_data[1] + 1,
        game_data[1] + 3,
        game_data[1] + 4]

    for i in range(7):
        player_vote(
            game_id=game_data[0],
            player_id=game_data[1] + i,
            vote=votes[i])

    response = client.put('game/{}/result'.format(game_data[0]))

    assert response.status_code == 200
    assert response.json() == {"result": True, "voted_lumos": voted_lumos}


'''
Test candidate promulgate fenix and get right board status
'''


def test_promulgate_fenix():
    game_data = game_factory(7, 1)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=0)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 1,
        "death eater promulgations": 0}


'''
Test candidate promulgate death eater and get right board status
'''


def test_promulgate_death_eater():
    game_data = game_factory(7, 1)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 0,
        "death eater promulgations": 1}


'''
Test a minister can't promulgate twice in the same turn
'''


def test_promulgate_twice():
    game_data = game_factory(7, 1)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=0)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Director already promulgated in this turn"}


'''
Test a player that is not the current director can not promulgate
'''


def test_promulgate_regular_player():
    game_data = game_factory(10, 3)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[0],
        card_type=1)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not director"}


'''
Test correct game status response
'''


def test_initial_game_check():
    game_data = game_factory(8, 0)

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 0,
                               "current minister id": game_data[1],
                               "current director id": game_data[1],
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": False,
                               "minister consent": 2}


'''
Test correct game status when fenix should win with 5 promulgations
'''


def test_game_check_fenix_five_promulgations():
    game_data = game_factory(8, 0, True, 1, True, 2)

    for i in range(5):
        start_new_turn(game_id=game_data[0])
        response = director_promulgate(
            game_id=game_data[0],
            player_id=game_data[1] + i + 3,
            card_type=0)

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": True,
                               "fenix promulgations": 5,
                               "death eater promulgations": 0,
                               "current minister id": game_data[1] + 7,
                               "current director id": game_data[1] + 7,
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": False,
                               "minister consent": 2}


'''
Test correct game status when death eaters should win with 6 promulgations
'''


def test_game_check_six_death_eater_promulgations():
    game_data = game_factory(10, 0, True, 1, True, 2)

    for i in range(6):
        start_new_turn(game_id=game_data[0])
        director_promulgate(
            game_id=game_data[0],
            player_id=game_data[1] + i + 3,
            card_type=1)
        execute_spell(game_data[0], "Guessing", game_data[1] + i + 3, 1)


    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": True,
                               "fenix promulgations": 0,
                               "death eater promulgations": 6,
                               "current minister id": game_data[1] + 8,
                               "current director id": game_data[1] + 8,
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": False,
                               "minister consent": 2}


'''
Assert a spell cant be executed if the one executing it isn't the minister of
the current turn
'''


def test_spell_with_wrong_minister_id():
    game_data = game_factory(5, 1, True, 1, False, 0, 0, 2)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1] + 20,
        game_data[1] + 2)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


def test_spell_with_no_board_spell_condition():
    game_data = game_factory(5, 1, True, 1, False, 0, 0, 0)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Avada Kedavra",
        game_data[1],
        game_data[1] + 2)

    assert response.status_code == 409
    assert response.json() == {"detail": "The requirements to cast the spell are not met"}


'''
Assert correct response when executing Guessing
'''


@db_session()
def test_guessing():
    game_data = game_factory(5, 1, True, 1, False, 0, 0, 2)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(game_data[0], "Guessing", game_data[1], 1)

    cards = select(
        c for c in Card if c.game.id == game_data[0] and c.order > 0).order_by(
        Card.order)[
            :3]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}


'''
Assert correct response when executing Crucio
'''


def test_crucio():
    game_data = game_factory(7, 0, False, 1, False, 0, 0, 1)

    minister = create_first_turn(game_data[0])

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1],
        game_data[1] + 2)

    assert response.status_code == 200
    assert response.json() == {"Fenix loyalty": False}


'''
Assert imposibility to execute Crucio in a dead player
'''


def test_crucio_in_dead_player():
    game_data = game_factory(7, 1, True, 1, True, 2, 0, 1)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1],
        game_data[1] - 2)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is dead"}


'''
Test correct response when trying to execute crucio in a player who
was already investigated
'''


def test_crucio_twice_in_player():

    game_data = game_factory(7, 1, True, 1, False, 0, 0, 1)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1],
        game_data[1] + 2)

    start_new_turn(game_id=game_data[0])

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1] + 1,
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1] + 1,
        game_data[1] + 2)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Player has been already investigated"}


'''
Assert Crucio can't be executed in a player who isn't in the game
'''


def test_crucio_in_invalid_player():
    game_data = game_factory(7, 1, True, 1, False, 0, 0, 1)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Crucio",
        game_data[1],
        game_data[1] + 20)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not in this game"}


def test_avada_kedavra():
    game_data = game_factory(5, 0, False, 2, False, 0, 3, 3)

    # If we call init game endpoint, it will select randomly the rol's
    minister = create_first_turn(game_data[0])

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    to_kill = 0
    for i in range(9):
        player = get_player_by_id(game_data[1]+i)
        if player.rol != "Voldemort":
            to_kill = game_data[1]+i
            break

    response = execute_spell(
        game_data[0],
        "Avada Kedavra",
        minister,
        to_kill)

    assert response.status_code == 200
    assert response.json() == {"Finished": False}


def test_avada_kedavra_Voldemort():
    game_data = game_factory(9, 0, False, 2, False, 0, 0, 3)

    # If we call init game endpoint, it will select randomly the rol's
    minister = create_first_turn(game_data[0])

    director_promulgate(
        game_id=game_data[0],
        player_id=minister,
        card_type=1)

    to_kill = 0
    for i in range(9):
        player = get_player_by_id(game_data[1]+i)
        if player.rol == "Voldemort":
            to_kill = game_data[1]+i
            break

    response = execute_spell(
        game_data[0],
        "Avada Kedavra",
        minister,
        to_kill)

    assert response.status_code == 200
    assert response.json() == {"Finished": True}


def test_avada_kedavra_in_dead_player():
    game_data = game_factory(9, 0, False, 1, True, 1, 3, 3)

    # If we call init game endpoint, it will select randomly the rol's
    minister = create_first_turn(game_data[0])

    director_promulgate(
        game_id=game_data[0],
        player_id=minister,
        card_type=1)

    response = execute_spell(
        game_data[0],
        "Avada Kedavra",
        minister,
        game_data[1])

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is dead"}


'''
Test correct spells in board with 5 to 6 players
'''


def test_available_spells_board_1():
    game_data = game_factory(5, 1, True, 1, False, 0, 0, 2)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = client.get('/game/{}/spell'.format(game_data[0]))

    assert response.status_code == 200
    assert response.json() == {"Spell": "Guessing"}

    execute_spell(
        game_data[0],
        response.json()["Spell"],
        game_data[1],
        game_data[1])

    for i in range(2):
        start_new_turn(game_id=game_data[0])
        response = director_promulgate(
            game_id=game_data[0],
            player_id=game_data[1] + 1 + i,
            card_type=1)
        response = client.get('/game/{}/spell'.format(game_data[0]))

        assert response.status_code == 200
        assert response.json() == {"Spell": "Avada Kedavra"}

        execute_spell(game_data[0], "Crucio", game_data[1], game_data[1] + i)


'''
Test correct spells in board with 7 to 8 players
'''


def test_available_spells_board_2():
    game_data = game_factory(7, 1, True, 1, False, 0, 0, 1)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = client.get('/game/{}/spell'.format(game_data[0]))

    assert response.status_code == 200
    assert response.json() == {"Spell": "Crucio"}

    execute_spell(
        game_data[0],
        response.json()["Spell"],
        game_data[1],
        game_data[1] + 1)

    spells = ["Imperius", "Avada Kedavra", "Avada Kedavra"]

    for i in range(3):
        start_new_turn(game_id=game_data[0])
        response = director_promulgate(
            game_id=game_data[0],
            player_id=game_data[1] + 1 + i,
            card_type=1)
        response = client.get('/game/{}/spell'.format(game_data[0]))

        assert response.status_code == 200
        assert response.json() == {"Spell": spells[i]}

        # Dont use Imperius because it's not implemented, yet.
        execute_spell(
            game_data[0],
            "Guessing",
            game_data[1] + 1 + i,
            game_data[1] + i)


'''
Test correct spells in board with 9 to 10 players
'''


def test_available_spells_board_3():
    game_data = game_factory(10, 1, True, 1, False, 0, 0, 0)

    director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = client.get('/game/{}/spell'.format(game_data[0]))

    assert response.status_code == 200
    assert response.json() == {"Spell": "Crucio"}

    execute_spell(
        game_data[0],
        response.json()["Spell"],
        game_data[1],
        game_data[1] + 1)

    spells = ["Crucio", "Imperius", "Avada Kedavra", "Avada Kedavra"]

    for i in range(4):

        start_new_turn(game_id=game_data[0])
        director_promulgate(
            game_id=game_data[0],
            player_id=game_data[1] + 1 + i,
            card_type=1)

        response = client.get('/game/{}/spell'.format(game_data[0]))

        assert response.status_code == 200
        assert response.json() == {"Spell": spells[i]}

        # Dont use Imperius because it's not implemented, yet.
        response = execute_spell(
            game_data[0],
            "Guessing",
            game_data[1] + 1 + i,
            game_data[1] + i)

'''
Test endpoint returns all ids (except candidate for minister) when asking
for director candidate ids, because theres no restriction with preivous
selected formula
'''


def test_get_director_candidate_ids_with_no_restriction():
    game_data = game_factory(10, 0)

    response = get_director_candidates(game_data[0])

    candidates = []

    for i in range(9):
        candidates.append(game_data[1] + 1 + i)

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Test correct response when there's a restriction because of a previous
accepted formula in the game
'''


def test_get_director_candidates_ids_with_minister_restriction():
    game_data = game_factory(7, 2)

    response = player_vote(game_id=game_data[0], player_id=game_data[1] - 2, vote=True)
    response = player_vote(game_id=game_data[0], player_id=game_data[1] - 1, vote=True)

    for i in range(5):
        response = player_vote(
            game_id=game_data[0],
            player_id=game_data[1] + i,
            vote=True)



    candidates = [
        game_data[1] - 2,
        game_data[1] - 1,
        game_data[1] + 1,
        game_data[1] + 2,
        game_data[1] + 3,
        game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Assert correct response, we know the valid director candidate ids; it should be
retrived by the endpoint in the real game
'''


def test_set_director_candidate():
    game_data = game_factory(10, 1)

    response = set_director_candidate(
        game_data[0], game_data[1], game_data[1] + 7)

    assert response.status_code == 200
    assert response.json() == {
        "candidate minister id": game_data[1],
        "candidate director id": game_data[1] + 7}


'''
Test correct response when the player who sets the director candidate isn't
the current minister in the current turn
'''


def test_set_director_with_incorret_minister_id():
    game_data = game_factory(10, 1)

    response = set_director_candidate(
        game_data[0], game_data[1] + 20, game_data[1] + 7)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


'''
Assert correct response when trying to set twice director candidate, regardless
of the id
'''


def test_set_director_twice():
    game_data = game_factory(10, 0)

    set_director_candidate(game_data[0], game_data[1], game_data[1] + 7)

    response = set_director_candidate(
        game_data[0], game_data[1], game_data[1] + 10)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Already set director candidate in current turn"}


'''
This test simulates a legislative session (without cards work), to assert
the correct director candidates in different turns
'''


def test_get_director_candidate_after_multiple_selected_director():
    game_data = game_factory(7, 0)

    set_director_candidate(game_data[0], game_data[1], game_data[1] + 1)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1] + 2,
        game_data[1] + 3,
        game_data[1] + 4,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 1, game_data[1] + 2)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1],
        game_data[1] + 3,
        game_data[1] + 4,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1] + 3)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1],
        game_data[1] + 1,
        game_data[1] + 4,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
This test simulates a legislative session (without cards work) with five
alive player to test this elegibility condition in the game
'''


def test_get_director_candidate_ids_with_five_player_restriction():
    game_data = game_factory(5, 0)

    set_director_candidate(game_data[0], game_data[1], game_data[1] + 3)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], True)

    candidates = [game_data[1],
                  game_data[1] + 2,
                  game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 1, game_data[1] + 2)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], False)

    candidates = [game_data[1],
                  game_data[1] + 1,
                  game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1])

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], True)

    candidates = [
        game_data[1] + 1,
        game_data[1] + 2,
        game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Test director candidates elegibility with 5 alive player between 7 players
'''


def test_get_director_candidate_ids_with_five_player_dead_players():
    game_data = game_factory(7, 0, True, 1, True, 2)

    set_director_candidate(game_data[0], game_data[1]+2, game_data[1] + 4)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], True, 2)

    candidates = [
        game_data[1] + 2,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Test correct response when geting players ids (should be in ascending order)
'''


def test_get_players_id():
    game_data = game_factory(10, 0)

    response = client.get('game/{}/players'.format(game_data[0]))

    ids = []
    for i in range(10):
        ids.append(game_data[1]+i)

    assert response.status_code == 200
    assert response.json() == {"Player ids": ids}


'''
Assert correct response when geting players info
'''


def test_get_players_info():
    game_data = game_factory(7, 0, False, 2, False, 0, 0, 0)

    # If we call init game endpoint, it will select randomly the rol's
    minister = create_first_turn(game_data[0])

    response = client.get('game/{}/players_info'.format(game_data[0]))

    info = []
    for i in range(7):
        info.append({"player_id": game_data[1]+i,
                     "username": 'User_{}'.format(game_data[2] - 7 + i),
                     "loyalty": "Fenix Order" if (i + 1) % 2 == 0 else "Death Eater"})

    assert response.status_code == 200
    assert response.json() == {"Players info": info}


'''
Assert correct imperius functionality after one turn
'''


def test_imperius():
    game_data = game_factory(7, 0, True, 1, False, 0, 0, 2)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(game_data[0], "Imperius", game_data[1], game_data[1] + 2)

    assert response.status_code == 200
    assert response.json() == {"candidate minister": game_data[1] + 2}

    response = start_new_turn(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 2}


'''
Assert imperius functionality after several turns
'''


def test_imperius_after_effect_two_turns():
    game_data = game_factory(7, 0, True, 1, False, 0, 0, 2)

    response = director_promulgate(
        game_id=game_data[0],
        player_id=game_data[1],
        card_type=1)

    response = execute_spell(game_data[0], "Imperius", game_data[1], game_data[1] + 5)

    assert response.status_code == 200
    assert response.json() == {"candidate minister": game_data[1] + 5}

    response = start_new_turn(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 5}

    response = start_new_turn(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 1}

    response = start_new_turn(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 2}


'''
Test expelliarmus endpoint with less than five death eater promulgations
'''


def test_expelliarmus_death_eater_promulgations_constraint():
    game_data = game_factory(7, 0, True, 1, False, 0, 0, 4)

    response = start_expelliarmus(game_data[0], game_data[1])

    assert response.status_code == 409
    assert response.json() == {"detail": "Expelliarmus requires 5 death eater promulgations"}


'''
Test regular player executing expelliarmus
'''


def test_expelliarmus_regular_player():
    game_data = game_factory(7, 0, True, 1, False, 0, 0, 5)

    response = start_expelliarmus(game_data[0], game_data[1] + 3)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not director"}


'''
Assert correct response when trying to execute expelliarmus twince in same turn
'''


def test_expelliarmus_twice():
    game_data = game_factory(5, 0, True, 1, False, 0, 0, 5)

    start_expelliarmus(game_data[0], game_data[1])
    response = start_expelliarmus(game_data[0], game_data[1])

    assert response.status_code == 409
    assert response.json() == {"detail": "Expelliarmus was already set in current turn"}


'''
Test correct response in a valid expelliarmus execution
'''


def test_expelliarmus():
    game_data = game_factory(10, 0, True, 1, False, 0, 0, 5)

    response = start_expelliarmus(game_data[0], game_data[1])

    assert response.status_code == 200
    assert response.json() == {"Expelliarmus director": True}

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 5,
                               "current minister id": game_data[1],
                               "current director id": game_data[1],
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": True,
                               "minister consent": 2}


'''
Test consent to expelliarmus when regular player
'''


def test_consent_expelliarmus_regular_player():
    game_data = game_factory(5, 2, True, 1, False, 0, 0, 5)

    get_3_cards(game_id=game_data[0], player_id=game_data[1])

    start_expelliarmus(game_data[0], game_data[1])

    response = consent_expelliarmus(game_data[0], game_data[1] + 2, True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


'''
Test consent expelliarmus when expelliarmus wasn't executed
'''


def test_consent_expelliarmus_not_set():
    game_data = game_factory(5, 3, True, 1, False, 0, 0, 5)

    response = consent_expelliarmus(game_data[0], game_data[1], True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Director didnt propose a Expelliarmus"}


'''
Assert expelliarmus response when trying to give consent twice
'''


def test_consent_expelliarmus_twice():
    game_data = game_factory(9, 0, True, 1, False, 0, 0, 5)

    get_3_cards(game_id=game_data[0], player_id=game_data[1])

    start_expelliarmus(game_data[0], game_data[1])

    consent_expelliarmus(game_data[0], game_data[1], True)
    response = consent_expelliarmus(game_data[0], game_data[1], False)

    assert response.status_code == 409
    assert response.json() == {"detail": "Consent already given"}


'''
Test correct negative consent to expelliarmus response
'''


def test_bad_consent_expelliarmus():
    game_data = game_factory(7, 1, True, 1, False, 0, 0, 5)

    start_expelliarmus(game_data[0], game_data[1])

    response = consent_expelliarmus(game_data[0], game_data[1], False)

    assert response.status_code == 200
    assert response.json() == {"Expelliarmus minister": True}

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 5,
                               "current minister id": game_data[1],
                               "current director id": game_data[1],
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": True,
                               "minister consent": 0}



'''
Test correct positive consent to expelliarmus response
'''


def test_good_consent_expelliarmus():
    game_data = game_factory(10, 1, True, 1, False, 0, 0, 5)

    get_3_cards(game_id=game_data[0], player_id=game_data[1])

    start_expelliarmus(game_data[0], game_data[1])

    response = consent_expelliarmus(game_data[0], game_data[1], True)

    assert response.status_code == 200
    assert response.json() == {"Expelliarmus minister": True}

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 5,
                               "current minister id": game_data[1],
                               "current director id": game_data[1],
                               "vote done": False,
                               "vote started": False,
                               "expelliarmus": True,
                               "minister consent": 1}
