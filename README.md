# Backend repository for Secret Voldemort

## Main Requirements

* [FastAPI](https://fastapi.tiangolo.com/)
* [PonyORM](https://ponyorm.org/)

## Optional (Testing purposes)

* [Pytest](https://docs.pytest.org/en/stable/)

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
`$ pip3 install requirements.txt`

Now you're ready to go!

## Start the server

To set up and start the server we use [uvicorn](https://www.uvicorn.org/) :unicorn:, don't worry, it was installed within the requirements!

Just start it with:  
`$ uvicorn main:app`

If you want to make your own changes to the repository, add `--reload`, so the server restarts when you save a modified file within the server files.
