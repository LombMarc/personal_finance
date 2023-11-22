#!/bin/bash

# Path to your PythonAnywhere virtual environment
VIRTUAL_ENV="/.virtualenvs/venv"  # Adjust virtualenv name

# Path to your Flask webapp in the GitHub repository
APP_PATH="/home/LombMarc/personal_finance"
SOURCE_CODE="/home/LombMarc/personal_finance"
# Path to the WSGI configuration file
WSGI_CONFIG="/var/www/username_pythonanywhere_com_wsgi.py"


# GitHub repository URL
REPO_URL="https://github.com/LombMarc/personal_finance.git"  # Replace with your GitHub repo URL


cd $APP_PATH
# Update local repository
git init
git pull $REPO_URL main
git remote add origin $REPO_URL

git pull origin main

cd ../.virtualenvs
mkvirtualenv venv --python=/usr/bin/python3.8
source $VIRTUAL_ENV/bin/activate
pip install -r $APP_PATH/requirements.txt
# Restart web webapp on PythonAnywhere
touch $WSGI_CONFIG
# Deactivate virtual environment
deactivate

sqlite3 webapp/tracker.db < sql/users.sql
sqlite3 webapp/tracker.db < sql/transaction.sql
sqlite3 webapp/tracker.db < sql/categories.sql
sqlite3 webapp/tracker.db < sql/users_cagegory.sql


echo "Deployment completed."
