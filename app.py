import os
import json

# hash things to ensure only valid requests
# from slack are processed
import hashlib
import hmac

# all the typical flask things needed
from flask import Flask, request, make_response, Response

# wrapper around slack's API
from slackclient import SlackClient

# auth we use to tell slack who we are
# from https://api.slack.com/apps/{{AppId}}/oauth?
# Bot User OAuth Access Token
BOT_OAUTH = os.environ.get("BOT_OAUTH", None)

# secret that we use to validate requests
# from https://api.slack.com/apps/{{AppId}}/general?
# Signing Secret
SIGNING_SECRET = os.environ.get("SIGNING_SECRET", None)
slack_client = SlackClient(BOT_OAUTH)

app = Flask(__name__)


# any message that starts with /lunch will
# enter in here
@app.route("/lunch", methods=["POST"])
def lunch_create():

    # compare the signature of the request with one we calculate
    # to ensure only requests from slack are processed
    if not valid_request(request.headers, request.get_data()):
        return Response(), 401

    # turn the rest of the user's message into an array
    # to process actions appropriately
    text = request.form.get("text").split()
    action = str(text[0]).upper()

    response_message = ""

    # channel id where the command was run
    channel = request.form.get("channel_id")
    # user id who ran the command
    user_id = request.form.get("user_id")

    # start command
    # user wants to start a new train
    if action == "START":

        # make sure the user passed a lunch time argument
        if len(text) == 2:
            time = text[1]

            # get the user's name
            user_name = request.form.get("user_name")

            # todo: POST route to create a new game

            # post a message back to the channel
            response_message = "@%s is starting a lunch train for %s" %\
                               (user_name, time)
            slack_client.api_call("chat.postMessage", channel=channel,
                text=response_message, link_names=1)

        else:
            # user did not pass in a lunch time
            response_message = "You did not pass in a time to go to lunch!"
            res = slack_client.api_call("chat.postEphemeral",
                channel=channel, text=response_message, user=user_id)

    # user wants to upvote a restaurant choice
    elif action == "YUM":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/vote.json") as json_data:
            dialog = json.load(json_data)

        # overwriting some values
        # since the upvote and downvote (yum and yuck)
        # share the same dialog config
        dialog["submit_label"] = "Upvote!"
        dialog["callback_id"] = "dialog-vote-yum"

        # Show the  dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're waiting for their answer
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Awaiting your choice...",
            attachments=[]
        )

    # user wants to downvote a restaurant choice
    elif action == "YUCK":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/vote.json") as json_data:
            dialog = json.load(json_data)

        # overwriting some values
        # since the upvote and downvote (yum and yuck)
        # share the same dialog config
        dialog["submit_label"] = "Downvote!"
        dialog["callback_id"] = "dialog-vote-yuck"

        # Show the dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're waiting for their answer
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Awaiting your choice...",
            attachments=[]
        )

    # user wants to add a restaurant choice
    # to the train
    elif action == "ADD":
        response_message = "You want to add an option"
        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    # user wants to join a train
    elif action == "BOARD":
        # Add the message_ts to the user's order info
        message_action = request.form

        with open("./dialog-templates/board.json") as json_data:
            dialog = json.load(json_data)

        # Show the dialog to the user
        open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog=dialog
        )

        # Update the message to show that we're waiting for their answer
        slack_client.api_call(
            "chat.update",
            channel=["lunch"],
            ts="in progress message",
            text=":pencil: Boarding...",
            attachments=[]
        )

    # user wants the status of running trains
    elif action == "STATUS":
        response_message = "You want the status of a lunch"
        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    # first time config to associate a user to the app
    elif action == "REGISTER":
        response_message = "You want to register"
        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    # see how many votes a user has available
    elif action == "VOTES":
        response_message = "You have 12,345 votes remaining."
        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    # command printing out all available actions
    elif action == "HELP":
        response_message = "Available commands:\n"\
            "start: start a train\n"\
            "add: add a nom\n"\
            "board: board a train\n"\
            "yum: vote for a nom\n"\
            "yuck: vote against a nom\n"\
            "status: status of a train\n"\
            "register: enroll in the lunch train revolution!\n"\
            "votes: displays your vote balance\n"\
            "help: displays this list of informative commands\n"

        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    # not listed command
    # to print all users to the console
    elif action == "LIST":

        users = slack_client.api_call("users.list")["members"]

        # print users

        wanted_keys = ['id', 'name', 'real_name']
        for thing in users:
            print thing["name"]
            print thing["id"]
            print thing["real_name"]
            print ""

    # catch all error message
    # says "uh oh!" in binary!
    else:
        response_message = "01110101 01101000 00100000 "\
            "01101111 01101000 00100001\n"\
            "*Beep boop!* LunchBro does not compute.\n"\
            "Try /lunch help for a full list of commands"

        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=response_message, user=user_id)

    return Response(), 200


# callback for when a dialog is filled out
# by a user
@app.route("/dialog", methods=["POST"])
def dialog_action():
    slack_event = json.loads(request.form["payload"])

    dialog_callback = slack_event["callback_id"]
    user_id = slack_event["user"].get("id")
    channel = slack_event["channel"].get("id")

    # check if the dialog is to upvote/downvote an option
    if str(dialog_callback).startswith("dialog-vote"):
        restaurant_id = slack_event["submission"].get("restaurant_id")
        vote_count = slack_event["submission"].get("vote_count")

        action = "yum"

        if dialog_callback == "dialog-vote-yuck":
            message = "You have casted %s negative votes!" % vote_count
            vote_count = int(vote_count) * -1
            action = "yuck"

        else:
            message = "You have casted %s votes!" % vote_count

        print "restaurant choice: " + restaurant_id
        print "vote count:" + str(vote_count)

        res = slack_client.api_call("chat.postEphemeral", channel=channel,
            text=message, user=user_id)

    # user has chosen a train to join
    elif str(dialog_callback).startswith("dialog-board-train"):
        train_id = slack_event["submission"].get("train_id")

    return Response(), 200

# route to authenticate the bot for slack
@app.route("/bot", methods=["POST"])
def slack_post():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
            {"content_type": "application/json"
        })

    return Response(), 200

# empty route
@app.route("/", methods=["GET"])
def test():
    return Response("It works!")


# validate the incoming request
# has been sent from slack
def valid_request(headers, body):
    timestamp = str(headers['X-Slack-Request-Timestamp'])
    version_number = "v0"

    # signature provided by slack
    request_signature = str(headers['X-Slack-Signature'])

    # concat the challenge string
    # https://api.slack.com/docs/verifying-requests-from-slack#a_recipe_for_security
    request_string = version_number + ":" + timestamp + ":" + str(body)

    # compute our version of the signature
    server_signature = version_number + '=' + \
        hmac.new(SIGNING_SECRET, request_string, hashlib.sha256)\
        .hexdigest()

    # return the result of comparing the two signatures
    return request_signature == server_signature


if __name__ == "__main__":
    app.run(debug=True)
