from numpy import *
from API.Model.gameExceptions import inconsistent_amount_of_players_exception


five_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Death Eater", "Voldemort"]

six_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order", "Death Eater",
                  "Voldemort"]

seven_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order","Death Eater",
                  "Death Eater", "Voldemort"]

eight_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order","Fenix Order",
                  "Death Eater", "Death Eater", "Voldemort"]

nine_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order",
                  "Death Eater", "Death Eater", "Death Eater", "Voldemort"]

ten_roles = ["Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order", "Fenix Order",
                   "Fenix Order", "Death Eater", "Death Eater", "Death Eater", "Voldemort"]


def select_roles_for_game(players: int):
    if players == 5:
        return five_roles
    elif players == 6:
        return six_roles
    elif players == 7:
        return seven_roles
    elif players == 8:
        return eight_roles
    elif players == 9:
        return nine_roles
    elif players == 10:
        return ten_roles
    else:
        raise inconsistent_amount_of_players_exception

def get_loyalty(rol: str):
    if rol == "Voldemort":
        return "Death Eater"
    else:
        return rol