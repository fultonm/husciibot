import os
import time
import json
import requests

from Huscii import Huscii
# from Huscii import id
from slackclient import SlackClient

# starterbot's ID as an environment variable
# BOT_ID = os.environ.get("BOT_ID")
thing = Huscii()
BOT_ID = thing.id
# BOT_ID = id

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# slack_client = SlackClient("xoxb-129456315235-AXsCMRwIxyKeKzhulWzsbkD2")
slack_client = SlackClient(thing.key)

responses = {"dojo" : "Dojo is at Expedia in Bellevue every Friday 4:30-6:00 pm. The classes we have are Python, CodeCamp, Hour of Code, and Scratch.", \
            "facebook" : "Join us on Facebook @ https://www.facebook.com/groups/UWTProgrammingClub/", \
            "dawgden" : "Join us on Dawgden @ https://dawgden.tacoma.uw.edu/organization/HuSCII"}

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command in responses:
        response = responses[command]
    if command.startswith('catfact'):
        call = requests.get('http://catfacts-api.appspot.com/api/facts?number=1')
        fact = json.loads(call.text)
        response = fact['facts'][0]

    # return the response
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")