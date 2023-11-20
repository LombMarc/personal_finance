#!/bin/bash

# Path to your PythonAnywhere virtual environment
VIRTUAL_ENV="/.virtualenvs/venv"  # Adjust virtualenv name

# Path to your Flask webapp in the GitHub repository
APP_PATH="home/LombMarc/personal_finance"

# Path to the WSGI configuration file
WSGI_CONFIG="/var/www/username_pythonanywhere_com_wsgi.py"


# GitHub repository URL
REPO_URL="https://github.com/LombMarc/personal_finance.git"  # Replace with your GitHub repo URL


cd $APP_PATH
# Update local repository
git pull $REPO_URL main
git init
git remote add origin $REPO_URL

git pull origin main


mkvirtualenv venv --python=/usr/bin/python3.8
source $APP_PATH/venv/bin/activate
# Restart web webapp on PythonAnywhere
touch $WSGI_CONFIG

# Activate virtual environment (replace 'activate' with 'activate.csh' if using csh)
source $VIRTUAL_ENV/bin/activate

# Install or update dependencies
pip install -r $APP_PATH/requirements.txt

# Deactivate virtual environment
deactivate



sqlite3 webapp/tracker.db < sql/users.sql
sqlite3 webapp/tracker.db < sql/transaction.sql
sqlite3 webapp/tracker.db < sql/categories.sql
sqlite3 webapp/tracker.db < sql/users_cagegory.sql


echo "Deployment completed."
