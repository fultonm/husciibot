"""
                                                                
Authors: Beebkips

"""
import os
import time
import json
import requests
import sqlite3

from Huscii import Huscii
# from Huscii import id
from slackclient import SlackClient

# get the keys off the key chain
keys = Huscii()
BOT_ID = keys.id
slack_client = SlackClient(keys.key)

# connect to database
con = sqlite3.connect("husciidata.db")
cur = con.cursor()

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

responses = {"dojo" : "Dojo is at Expedia in Bellevue every Friday 4:30-6:00 pm. The classes we have are Python, CodeCamp, Hour of Code, and Scratch.", \
            "facebook" : "Join us on Facebook @ https://www.facebook.com/groups/UWTProgrammingClub/", \
            "dawgden" : "Join us on Dawgden @ https://dawgden.tacoma.uw.edu/organization/HuSCII"}

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Something happened" 
    print command
    
    # "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    
    # example command
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    
    # dict commands
    if command in responses:
        response = responses[command]
    
    # catfact
    if command.startswith('catfact'):
        call = requests.get('http://catfacts-api.appspot.com/api/facts?number=1')
        fact = json.loads(call.text)
        response = fact['facts'][0]
    
    #events
    if command.startswith("event"):
        eventCommand = command.split("event")
        commandList = eventCommand[1].split(" ")

        if commandList[1].startswith("add") and len(commandList) >= 4 and commandList[1].isdigit():
            # print commandList[1], commandList[2], commandList[3]
            if len(commandList) > 4:
                for index in range(4, len(commandList)):
                    commandList[3] += " " + commandList[index]
            cur.execute("INSERT INTO Events VALUES(?, ?, ?)", (commandList[1], commandList[2], commandList[3]))
            con.commit()
            response = "Event added"

        
        if commandList[1].startswith("delete"):
            deleteCommand = command.split("delete")[1].strip()
            cur.execute("DELETE FROM Events WHERE Id == ?", deleteCommand)
            response = "Event deleted"
        
        if commandList[1].startswith("list"):
            cur.execute("SELECT * FROM Events")
            event_names = [en[0] for en in cur.description]
            event = cur.fetchall()
            response = "%s %-10s %s" % (event_names[0], event_names[1], event_names[2])

            for row in event:    
                response += "\n%2s %-10s %s" % row

    response = "`"  + response + "`"

    #quest
    if command.startswith("hquest"):
        command = command.split("hquest")[1].strip()
        print command
        response = husciiQuest(command, channel, user)
    
    # return the response
    print user
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

"""
   __ __             _ _ ____               __ 
  / // /_ _____ ____(_|_) __ \__ _____ ___ / /_
 / _  / // (_-</ __/ / / /_/ / // / -_|_-</ __/
/_//_/\_,_/___/\__/_/_/\___\_\_,_/\__/___/\__/ 

"""

def husciiQuest(command, channel, user):
    usercon = sqlite3.connect("hquest/" + user + ".db")
    usercur = usercon.cursor()
    response = "hquest"
    if command.startswith("help"):
        response = "add the hquest commands"        

    if command.startswith("new profile"):
        api_call = slack_client.api_call("users.list")
        if api_call.get('ok'):
            print "api call gucci fam"
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for u in users:
                if 'id' in u and u.get('id') == user.strip():
                    username = u.get('name')
                    print "Username aquired"

        try:
            usercur.execute("CREATE TABLE Equipment(Head TEXT, Hands TEXT, Chest TEXT, Legs TEXT, Feet TEXT, Weapon TEXT, Offhand TEXT)")
            usercur.execute("INSERT INTO Equipment VALUES(?, ?, ?, ?, ?, ?, ?)", ("None", "None", "None", "None", "None", "None", "None"))
            print "equips made"

            usercur.execute("CREATE TABLE Inventory(Item TEXT, Slot TEXT, Value INT, Rating INT, Equipped BOOLEAN)")
            usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?)", ("Wooden Sword", "Weapon", 1, 1, 0))
            usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?)", ("Wooden Shield", "Offhand", 1, 1, 0))
            print "inventory made"

            usercur.execute("CREATE TABLE Profile(UserID TEXT, Username TEXT, ExpCur INT, ExpMax INT, Gold INT, Cr INT)")
            usercur.execute("INSERT INTO Profile VALUES(?, ?, ?, ?, ?, ?)", (user, username, 0, 10, 0, 0))
            print "profile made"

            usercon.commit()

            response = "New profile made"
        except sqlite3.Error:
            response = "You have a profile already or there was an error"

    if command.startswith("item"):
        command = command.split("item")[1].strip()
        if command.startswith("equip"):
            command = command.split("equip")[1].strip()
            usercur.execute("SELECT * FROM Inventory WHERE Item = ?", [command])
            item = usercur.fetchall()
            if item[0][4]:
                response = "Item is already equipped"
            else:
                usercur.execute("SELECT * FROM Profile")
                profile = usercur.fetchall()
                print item, command, item[0], item[0][1], item[0][0]
                exe = "UPDATE Equipment SET " + item[0][1] + " = '" + item[0][0] + "'"
                usercur.execute(exe)
                # usercur.execute("UPDATE Equipment SET ? = ?", ((item[0][1],) , (item[0][0],)))
                print profile
                cr = item[0][3] + profile[0][5]
                print type(cr)
                usercur.execute("UPDATE Profile SET Cr = ?", (cr,))
                usercur.execute("UPDATE Inventory SET Equipped = 1 WHERE Item = ?", [command])
                response = "You equipped " + command

            usercon.commit()

    response = "`" + response + "`"

    if command.startswith("equips"):
        usercur.execute("SELECT * FROM Equipment")
        equipSlots = [es[0] for es in usercur.description]
        equips = usercur.fetchall()
        response = ""
    
        for i in range(len(equipSlots)):
            line = " " + equipSlots[i] + ": " + equips[0][i]
            response += "      |%-53s|\n" % line

        response = scrollify(response)

    if command.startswith("inventory"):
        usercur.execute("SELECT * FROM Inventory")
        items = usercur.fetchall()
        response = ""

        response += "      |%-53s|\n" % "     Items"
        i = 1;
        for row in items:
            if row[4]:
                e = "[x]"
            else:
                e = "[ ]"
            response += "      | %3s %-43s %3s |\n" % (i, row[0], e)
            i += 1
        
        response = scrollify(response)

    return response

def scrollify(response):
        scrollTop =  "      _______________________________________________________ \n"
        scrollTop += "     /\                                                      \ \n"
        scrollTop += "(O)===)><><><><><><><><><><><><><><><><><><><><><><><><><><><)==(O) \n"
        scrollTop += "     \/''''''''''''''''''''''''''''''''''''''''''''''''''''''/ \n"
        scrollTop += "      |%-53s|\n" % ""

        scrollBot  = "      |%-53s|\n" % ""
        scrollBot += "     /\\''''''''''''''''''''''''''''''''''''''''''''''''''''''\ \n"
        scrollBot += "(O)===)><><><><><><><><><><><><><><><><><><><><><><><><><><><)==(O) \n"
        scrollBot += "     \/______________________________________________________/"

        response = "```" + scrollTop + response + scrollBot + "```"
        return response    


"""
,.*'`/~=-=~\`'*.,
"""

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    # if(len(output_list) > 0):
    #     print output_list

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                       output['channel'], \
                       output['user']
    return None, None, None

def makeTable():
    # cur.execute("DROP TABLE IF EXISTS Events")
    try:
        cur.execute("CREATE TABLE Events(Id TEXT, TheDate TEXT, Name TEXT)")
        # cur.execute("CREATE TABLE HusciiQuest(UserId TEXT, Username TEXT, TheDate TEXT, Name TEXT)")
    except sqlite3.Error:
        pass

if __name__ == "__main__":
    makeTable()
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
