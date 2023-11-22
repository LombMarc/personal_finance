#!/bin/bash

# Path to your PythonAnywhere virtual environment
VIRTUAL_ENV="/.virtualenvs/venv"  # Adjust virtualenv name

# Path to your Flask webapp in the GitHub repository
APP_PATH="home/LombMarc/personal_finance"

# GitHub repository URL
REPO_URL="https://github.com/LombMarc/personal_finance.git"  # Replace with your GitHub repo URL

cd $APP_PATH
git init
git pull origin main

echo "deployment complete"

