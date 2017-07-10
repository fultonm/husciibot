"""
Huscii Bot can do many things!
Authors: Beebkips, Michael Fulton
"""

import time
import json
import requests

import HusciiKeys
import HusciiAuth
from slackclient import SlackClient
import shem

BOT_ID = HusciiKeys.ID
API_KEY = HusciiKeys.KEY

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

# instantiate Slack & Twilio clients
SLACK_CLIENT = SlackClient(API_KEY)

RESPONSES = {
    "dojo": "Dojo is at Expedia in Bellevue every Friday 4:30-6:00 pm. The classes we\
              have are Python, CodeCamp, Hour of Code, and Scratch.",
    "facebook": "Join us on Facebook @\
                 https://www.facebook.com/groups/UWTProgrammingClub/",
    "dawgden": "Join us on Dawgden @ https://dawgden.tacoma.uw.edu/organization/HuSCII"}


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.

        command: The full string the user input, including the @HusciiBot tag.
        channel: The channel the input was given (ex. #general, #random)
        user: The 9 character alphanumeric user ID of the user who gave the command.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command in RESPONSES:
        response = RESPONSES[command]
    if command.startswith('catfact'):
        call = requests.get(
            'http://catfacts-api.appspot.com/api/facts?number=1')
        fact = json.loads(call.text)
        response = fact['facts'][0]
    if 'event' in command or 'events' in command:
        # take off the event part, pass only the next args
        response = shem.handle_command(command, user)
    if 'officer' in command:
        response = HusciiAuth.handle_command(command, user)
    # return the response
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.

        slack_rtm_output: The raw output from Slack firehose. More info can be
                          found on api.slack.com
    """
    output_list = slack_rtm_output
    if output_list:
        for output in output_list:
            if 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                    output['channel'], output['user']
    return None, None, None


def init():
    """
        Initalizes HusciiBot by connecting to the Firehose event feed. Each second the
        event feed is checked for new messages and commands.
    """
    if SLACK_CLIENT.rtm_connect():
        print("HusciiBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(
                SLACK_CLIENT.rtm_read())
            if command and channel and user:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


if __name__ == "__main__":
    init()
