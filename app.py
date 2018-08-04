import os
import random
import json
from flask import Flask, request, make_response, Response
from slackclient import SlackClient

BOT_OAUTH = os.environ.get('BOT_OAUTH', None)

app = Flask(__name__)
slack_client = SlackClient(BOT_OAUTH)

@app.route('/bot', methods=['POST'])
def slack_post():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
                    {"content_type": "application/json"
                })

    user_check = slack_event['event'].get('user')

    # if request.form['token'] == SLACK_WEBHOOK_SECRET:
    if user_check is not None:
        print slack_event
        channel = slack_event['event']['channel']
        username = slack_event['event']['user']
        response_message = username + " in " + channel + " says: "

        res = slack_client.api_call("chat.postMessage", channel=channel,
                              text=response_message)

        print res
    return Response(), 200

@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == '__main__':
    app.run(debug=True)