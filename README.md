# lunch-slackbot
Coordinate lunches while slacking

## installation instructions
```
    git clone
    pip --version
    easy_install pip
    pip install virtualenv
```

## environment config
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python app.py
```

## testing locally
```
https://ngrok.com/download
./ngrok http 5000
http://127.0.0.1:4040/inspect/http
```

You'll also want to configure environment variables
```
http://api.slack.com/apps/{{yourApp}}/oAuth?
Bot User OAuth Access Token
export BOT_OAUTH='{{token}}'
```