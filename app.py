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

    return Response(), 200


@app.route('/lunch', methods=['POST'])
def lunch_create():
    # slack_event = json.loads(request)

    text = request.form.get('text').split()
    action = str(text[0]).upper()
    response_message = ''

    print action
    print text[1]

    channel = request.form.get('channel_id')

    if action == 'START':
        response_message = 'You want to start lunch at ' + text[1]
    elif action == 'ADD':
        response_message = 'You want to add '+text[1]+' to the list of options'
    elif action == 'VOTE':
        response_message = 'You want to vote on an option'
    elif action == 'STATUS':
        response_message = 'You want the status of a lunch'

    res = slack_client.api_call("chat.postMessage", channel=channel,
                                text=response_message)

    return Response(), 200


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == '__main__':
    app.run(debug=True)