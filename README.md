# Requirements
# Install virtualenv using windows/archlinux
py -m pip install virtualenv or sudo pacman -S python-virtualenv
# Create virtualenv using windows/archlinux
py -m virtualenv .venv or sudo python -m venv .venv

# Activate virtualenv using windows/archlinux
.venv/Scripts/activate.bat or source .venv/bin/activate

# Langchain
pip install langchain langchain-openai openai python-dotenv
pip install -qU langchain-openai
pip install langchain-anthropic python-dotenv

# Google API
pip install google-api-python-client
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Debug Requirements
py -m pip install -r requirements.txt
py -m pip freeze > requirements.txt
