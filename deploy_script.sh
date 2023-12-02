#!/bin/bash

echo "Enter your name:"
read userName

APP_PATH="home/$userName/personal_finance"

# Path to your PythonAnywhere virtual environment
VIRTUAL_ENV="/.virtualenvs/venv"
# GitHub repository URL
REPO_URL="https://github.com/LombMarc/personal_finance.git"

function handle_error {
    echo "An error occurred. Exiting."
    exit 1
}

trap'handle_error' ERR

if [ -d "$APP_PATH" ]; then
  cd $APP_PATH
  #exclude the db from fetched data from remote repo
  git fetch origin main
  git checkout origin/main --webapp/tracker.db
  git merge origin main

else
  SOURCE_CODE="/home/$userName/personal_finance"
  # Path to the WSGI configuration file
  WSGI_CONFIG="/var/www/$userName"_"pythonanywhere_com_wsgi.py"

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

fi
echo "Deployment completed succesfully"

trap - ERR