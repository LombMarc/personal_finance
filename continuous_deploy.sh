#!/bin/bash

# Path to your PythonAnywhere virtual environment
VIRTUAL_ENV="/.virtualenvs/venv"  # Adjust virtualenv name

# Path to your Flask webapp in the GitHub repository
APP_PATH="home/LombMarc/personal_finance_app"

# Path to the WSGI configuration file
WSGI_CONFIG="/var/www/username_pythonanywhere_com_wsgi.py"

# GitHub repository URL
REPO_URL="https://github.com/LombMarc/personal_finance.git"  # Replace with your GitHub repo URL

cd $APP_PATH
git init
git remote add origin $REPO_URL
git pull origin main

echo "deployment complete"

