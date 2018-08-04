import os
import random
import json
from flask import Flask, request, make_response, Response
from slackclient import SlackClient

BOT_OAUTH = os.environ.get("BOT_OAUTH", None)

app = Flask(__name__)
slack_client = SlackClient(BOT_OAUTH)


@app.route("/bot", methods=["POST"])
def slack_post():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
                    {"content_type": "application/json"
        })

    user_check = slack_event["event"].get("user")

    # if request.form["token"] == SLACK_WEBHOOK_SECRET:
    if user_check is not None:
        print slack_event
        channel = slack_event["event"]["channel"]
        username = slack_event["event"]["user"]
        response_message = username + " in " + channel + " says: "

        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    return Response(), 200


@app.route("/lunch", methods=["POST"])
def lunch_create():
    # slack_event = json.loads(request.data)
    print request.data

    text = request.form.get("text").split()
    action = str(text[0]).upper()
    response_message = ''

    channel = request.form.get("channel_id")

    if action == "START":
        response_message = "You want to start a lunch for" + text[1]
        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    elif action == "YUM":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/vote.json") as json_data:
            dialog = json.load(json_data)

        dialog["submit_label"] = "Upvote!"

        # Show the ordering dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're in the process of taking their order
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Taking your order...",
            attachments=[]
        )

    elif action == "YUCK":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/vote.json") as json_data:
            dialog = json.load(json_data)

        dialog["submit_label"] = "Downvote!"

    # Show the ordering dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're in the process of taking their order
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Taking your order...",
            attachments=[]
        )

    elif action == "ADD":
        response_message = 'You want to add an option'
        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    elif action == "BOARD":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/board.json") as json_data:
            dialog = json.load(json_data,)

        # Show the ordering dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're in the process of taking their order
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Boarding...",
            attachments=[]
        )

    elif action == "STATUS":
        response_message = "You want the status of a lunch"
        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    elif action == "REGISTER":
        response_message = "You want to register"
        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    elif action == "HELP":
        response_message = "Available commands:\n" \
                            "start: start a train\n" \
                            "add: add a nom\n"\
                            "board: board a train\n"\
                            "yum: vote for a nom\n"\
                            "yuck: vote against a nom\n"\
                            "status: status of a train\n"\
                            "register: enroll in the lunch train revolution!\n"\
                            "help: displays this list of informative commands\n"

        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    else:
        response_message = "01110101 01101000 00100000 01101111 01101000 00100001\n"\
                           "*Beep boop!* LunchBro does not compute.\n"\
                           "Try /lunch help for a full list of commands"

        res = slack_client.api_call("chat.postMessage", channel=channel,
            text=response_message)

    return Response(), 200


@app.route("/dialog", methods=["POST"])
def dialog_action():
    slack_event = json.loads(request.form["payload"])

    print slack_event

    return Response(), 200


@app.route("/", methods=["GET"])
def test():
    return Response("It works!")


if __name__ == "__main__":
    app.run(debug=True)