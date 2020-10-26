#!/bin/bash

# Borrar los archivos que no hacen falta
# (porque no tenemos la opción de eliminar a los usuarios por la interfaz)

rm -rd __pycache__
rm -rd ./API/Model/__pycache__
rm -rd ./API/TestAPI/TestUser/__pycache__
rm -rd ./Database/__pycache__
rm ./Database/*.sqlite