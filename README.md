# Backend repository for Secret Voldemort

This rest-ful API was developed with [FastAPI](https://fastapi.tiangolo.com/) and using [PonyORM](https://ponyorm.org/) database creation and management.
After starting the server you can view and test all the endpoints in:
`http://127.0.0.1:8000/api/docs`

If this is not enough and you want some *beautiful* (don't jugde us) frontend for this backend we have you covered: [Frontend repository for Secret Voldemort](https://github.com/LMartinezEXEX/sdv-frontend)

## Installation

We encourage you to use a python virtual environment!

1) Download the repository  
`$ git clone https://github.com/LMartinezEXEX/sdv-backend.git`

2) Navigate inside the downloaded repository  
`$ cd sdv-backend/`

3) Initialize python virtual environment  
`$ python3 -m venv venv`

4) Activate/Start up the virtual environment  
`$ source venv/bin/activate`

5) Install all the requirements needed (there are many other you can check in the requirements.txt) for this proyect with:  
`$ pip3 install -r requirements.txt`

Now you're ready to go!

## Start the server

To set up and start the server we use [uvicorn](https://www.uvicorn.org/) :unicorn:, don't worry, it was installed within the requirements!

Just start it with:  
`$ uvicorn main:app`

If you want to make your own changes to the repository, add `--reload`, so the server restarts when you save a modified file within the server files.

## Testing

We've make some tests for you to run if you decide you want to make some enhancement in the current code!

You should run it with [Pytest](https://docs.pytest.org/en/stable/), it was installed within the requirements too:

`python -m pytest API/TestAPI/test_file.py`
