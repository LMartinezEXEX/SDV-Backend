#!/bin/bash

# Borrar los archivos que no hacen falta y testear seguidamente

echo "Cleaning..."

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

if [ -e "./Database/secretVoldemort.sqlite" ]
then
    rm "./Database/secretVoldemort.sqlite"
fi

echo "Sleep for 2 seconds..."
sleep 2

echo ""
echo -e "\e[32m\e[1mDone"