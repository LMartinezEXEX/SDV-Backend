# Metadata tags

user_metadata = [
    {
        "name": "Profile",
        "description": "Return user profile data",
    },
    {
        "name": "User icon",
        "description": "Return user icon",
    },
    {
        "name": "Register",
        "description": "Register user.",
    },
    {
        "name": "Login",
        "description": "Login endpoint: returns token and session data for requests.",
    },
    {
        "name": "Update username",
        "description": "Update username: requires authentication",
    },
    {
        "name": "Update password",
        "description": "Update password: requires authentication",
    },
    {
        "name": "Update icon",
        "description": "Update icon: requires authentication",
    },
]

game_metadata = [
    {
        "name": "List Games",
        "description": "List all available games to join",
    },
    {
        "name": "Create Game",
        "description": "Create a new game",
    },
    {
        "name": "Join Game",
        "description": "Join an existing game not initialized",
    },
    {
        "name": "Leave not initialized game",
        "description": "Leave not initialized game",
    },
    {
        "name": "Init Game",
        "description": "Initialize the game: requires be the owner of the game",
    },
    {
        "name": "Players id",
        "description": "Get all player's in game id",
    },
    {
        "name": "Players info",
        "description": "Get all player's in game info (id, username, and loyalty)",
    },
    {
        "name": "Has the Game started",
        "description": "Check if the game is initialized",
    },
    {
        "name": "Next minister candidate",
        "description": "Start a new turn and return the next candidate minister id",
    },
    {
        "name": "Available director candidates id's",
        "description": "Get a list of player's id available to be selected as director candidate",
    },
    {
        "name": "Set director candidate",
        "description": "Set director in current turn",
    },
    {
        "name": "Get vote formula",
        "description": "Get minister and director candidate's id",
    },
    {
        "name": "Submit a vote",
        "description": "Submit player's vote for current formula, \
                        if all players voted and majority is Lumos \
                        then set candidates to current state",
    },
    {
        "name": "Vote result",
        "description": "Get vote result for current turn",
    },
    {
        "name": "Notify that knows about rejection",
        "description": "Notify player knows the formula was rejected by Nox majority",
    },
    {
        "name": "Take three cards",
        "description": "Take next three cards in the deck and generate \
                        three new cards for next turns",
    },
    {
        "name": "Discard card",
        "description": "Minister discard a selected card",
    },
    {
        "name": "Not discarded cards",
        "description": "Director gets the two cards remaining from the minister. \
                        Requires minister has descarded a card",
    },
    {
        "name": "Start expelliarmus",
        "description": "Director porpose a expelliarmus",
    },
    {
        "name": "Accept/decline expelliarmus",
        "description": "Minister accept or declines expelliarmus. Requires \
                        director has porposed expelliarmus",
    },
    {
        "name": "Promulgate card",
        "description": "Director promulgates a card",
    },
    {
        "name": "Available spell",
        "description": "Get available spell in current turn",
    },
    {
        "name": "Execute spell",
        "description": "Minister execute spell available",
    },
    {
        "name": "Game state",
        "description": "Get current turn state in game",
    },
    {
        "name": "Notify knowledge about ending",
        "description": "Notify player knows the game has finished",
    },
    {
        "name": "Leave Game",
        "description": "Leave initialized game dying in the process. Requires \
                        be in the game",
    }
]
