#!/bin/bash

# Borrar los archivos que no hacen falta y testear seguidamente
# (porque no tenemos la opción de eliminar a los usuarios por la interfaz)

echo "Trying to clean for testing user related module"

if [ -d "./__pycache__" ]
then
    rm -rd "./__pycache__"
fi

if [ -d "./API/Model/__pycache__" ]
then
    rm -rd "./API/Model/__pycache__"
fi

if [ -d "./API/TestAPI/TestUser/__pycache__" ]
then
    rm -rd "./API/TestAPI/TestUser/__pycache__"
fi

if [ -d "./Database/__pycache__" ]
then
    rm -rd "./Database/__pycache__"
fi

if [ -e "./Database/*.sqlite" ]
then
    rm "./Database/*.sqlite"
fi

echo "Sleep for 2 seconds..."
sleep 2


echo -e "\e[93m\e[1mTesting many users..."
echo "Running command: python3.8 -m pytest API/TestAPI/TestUser/testUser.py"

python3.8 -m pytest --maxfail=1 API/TestAPI/TestUser/testUser.py

echo "Cleaning for testing user related module"

rm -rd ./__pycache__
rm -rd ./API/Model/__pycache__
rm -rd ./API/TestAPI/TestUser/__pycache__
rm -rd ./Database/__pycache__
rm ./Database/*.sqlite

echo "Sleep for 2 seconds..."
sleep 2

echo -e "\e[93m\e[1mTesting a single user..."
echo "Running command: python3.8 -m pytest -s API/TestAPI/TestUser/testSingleUser.py"

python3.8 -m pytest -s --maxfail=1 API/TestAPI/TestUser/testSingleUser.py

echo "Cleaning..."

rm -rd ./__pycache__
rm -rd ./API/Model/__pycache__
rm -rd ./API/TestAPI/TestUser/__pycache__
rm -rd ./Database/__pycache__
rm ./Database/*.sqlite

echo ""
echo -e "\e[32m\e[1mDone"