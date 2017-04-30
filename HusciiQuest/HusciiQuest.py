"""
   __ __             _ _ ____               __ 
  / // /_ _____ ____(_|_) __ \__ _____ ___ / /_
 / _  / // (_-</ __/ / / /_/ / // / -_|_-</ __/
/_//_/\_,_/___/\__/_/_/\___\_\_,_/\__/___/\__/ 

"""

import sqlite3
import json
import requests
import random
from Huscii import Huscii
from HQShop import HQShop
from slackclient import SlackClient

keys = Huscii()
BOT_ID = keys.id
slack_client = SlackClient(keys.key)

# HQShop = HQShop()   

class HusciiQuest():

    """
    Add the scroll effect to the player information responses and turn into
    multiline block comment
    """
    def genItem():
        # with open('randgen/items.json') as data_file:    
        #     data = json.load(data_file)
        #     if(bool(random.getrandbits(1))):
        #         item = data['weapon']
        #     else:
        #         item = data['armour']
        #     weapon = item[random.randrange(0, len(item) - 1)]
        #     prefix = data['prefix'][random.randrange(0, len(data['prefix']) - 1)]
        #     suffix = data['suffix'][random.randrange(0, len(data['suffix']) - 1)]
        #     print(prefix + " " + weapon + " " + suffix)

        level = 25
        prefix = ''
        suffix = ''
        with open('randgen/items2.json') as data_file:    
            data = json.load(data_file)
            if(bool(random.getrandbits(1))):
                item = data['weapon']
            else:
                item = data['armour']
            item = random.choice(item)
            slot = list(item)[0]
            item = item[slot]
            item = random.choice(item)
            cr = item[list(item)[0]]
            randnum = random.uniform(-0.5, 1.0)
            cr = (int)(level + (cr * (level/100) * randnum)) + 3
            if slot == 'twohand':
                cr = (int)((level * 2) + (2 * (cr * (level/100) * randnum))) + 6
            else:
                cr = (int)(level + (cr * (level/100) * randnum)) + 3
            itemlevel = (int)(level + round(randnum * 4))
            item = list(item)[0]
            
            chance = random.randrange(1, 100)
            # print(chance)
            if chance >= (100 - level/2):
                prefix = random.choice(data['prefix']) + ' '
                cr += (int)(random.uniform(0.25, 0.5) * level)
                itemlevel += 1
            chance = random.randrange(1, 100)
            # print(chance)
            if chance >= (100 - level/2):
                suffix = ' ' + random.choice(data['suffix'])
                cr += (int)(random.uniform(0.25, 0.5) * level)
                itemlevel += 1
            if itemlevel > 100:
                itemlevel = 100
            elif itemlevel < 1:
                itemlevel = 1
            value = (int)(itemlevel * 10 + itemlevel * 2.5 * randnum)
            print(value)
            item = prefix + item + suffix
            return 'You found a ' + item, item, slot, itemlevel, cr, value


    @staticmethod
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


    @staticmethod
    def husciiQuest(command, channel, user):
        # connect to user database
        usercon = sqlite3.connect("hquest/" + user + ".db")
        usercur = usercon.cursor()
        response = "Something went wrong with [hquest] type help for commands"

        # create a new profile
        if command.startswith("new profile"):
            # get user list
            api_call = slack_client.api_call("users.list")
            if api_call.get('ok'):
                print("api call gucci fam")
                # retrieve all users so we can find our username
                users = api_call.get('members')
                for u in users:
                    if 'id' in u and u.get('id') == user.strip():
                        username = u.get('name')
                        print("Username aquired")

            try:
                # create equip table and fill with none
                # usercur.execute("CREATE TABLE Equipment(Head TEXT, Hands TEXT, Chest TEXT, Legs TEXT, Feet TEXT, Weapon TEXT, Offhand TEXT)")
                # usercur.execute("INSERT INTO Equipment VALUES(?, ?, ?, ?, ?, ?, ?)", ("None", "None", "None", "None", "None", "None", "None"))
                usercur.execute("CREATE TABLE Equipment(Slot TEXT, Item TEXT)")
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Head", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Hands", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Chest", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Legs", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Feet", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Weapon", "None"))
                usercur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Offhand", "None"))
                print("equips made")

                # create inventory table
                usercur.execute("CREATE TABLE Inventory(Item TEXT, Slot TEXT, Value INT, Rating INT, Equipped BOOLEAN, ItemLevel INT)")
                # add wooden sword and shield
                usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", ("Wooden Sword", "Weapon", 1, 1, 0, 1))
                usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", ("Wooden Shield", "Offhand", 1, 1, 0, 1))
                print("inventory made")

                # create profile table
                usercur.execute("CREATE TABLE Profile(UserID TEXT, Username TEXT, ExpCur INT, ExpMax INT, Level INT, Gold INT, Cr INT)")
                # insert default values
                usercur.execute("INSERT INTO Profile VALUES(?, ?, ?, ?, ?, ?)", (user, username, 0, 10, 1, 50, 0))
                print("profile made")

                # commit changes
                usercon.commit()

                response = "New profile made"

            except sqlite3.Error:
                # oh no
                response = "You have a profile already or there was an error"

        # handle commands with items
        if command.startswith("item"):
            command = command.split("item")[1].strip()

            # equip an item
            if command.startswith("equip"):
                command = command.split("equip")[1].strip()
                # fetch table row for the item
                usercur.execute("SELECT * FROM Inventory WHERE Item = ?", [command])
                item = usercur.fetchall()
                if(len(item) != 0):
                    item = item[0]
                    if item[4] and item[1] != "Other":
                        response = "Item is already equipped"
                    else:
                        # fetch profile
                        usercur.execute("SELECT * FROM Profile")
                        profile = usercur.fetchall()[0]
                        if item[1] == 'Twohand':
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item[0], 'Weapon'))
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item[0], 'Offhand'))
                        else:
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item[0], item[1]))
                        print(profile)
                        # update combat rating
                        cr = item[3] + profile[5]
                        usercur.execute("UPDATE Profile SET Cr = ?", (cr,))
                        usercur.execute("UPDATE Inventory SET Equipped = 1 WHERE Item = ?", [command])
                        response = "You equipped " + command
                else:
                    response = "Cannot find item"

            # unequip item
            if command.startswith("unequip"):
                command = command.split("unequip")[1].strip()
                # fetch table row for the item
                usercur.execute("SELECT * FROM Inventory WHERE Item = ?", [command])
                item = usercur.fetchall()
                if(len(item) != 0):
                    item = item[0]
                    if item[4]:
                        # fetch profile
                        usercur.execute("SELECT * FROM Profile")
                        profile = usercur.fetchall()[0]
                        # update the "equipped" value in table
                        if item[1] == 'Twohand':
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", 'Weapon'))
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", 'Offhand'))
                        else:
                            usercur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", item[1]))
                        # update combat rating
                        cr = profile[5] - item[3]
                        usercur.execute("UPDATE Profile SET Cr = ?", (cr,))
                        usercur.execute("UPDATE Inventory SET Equipped = 0 WHERE Item = ?", [command])
                        response = "You unequipped " + command
                    else:
                        response = "Item is not equipped"
                else:
                    response = "Cannot find item"

            # commit changes
            usercon.commit()

        # turn into code line response
        response = "`" + response + "`"

        # add help commands
        if command.startswith("help"):
            response = "HELP COMMANDS\n"
            response += "profile .. prints out users profile\n"
            response += "inventory .. prints out inventory\n"
            response += "equips .. prints out all equipment\n"
            response += "new profile .. creates new profile\n"
            response += "item equip [item] .. equips item\n"
            response += "item unequip [item] .. unequips item\n"

            response = "```" + response + "```"

        # print equipment
        if command.startswith("equips"):
            # select all equipment coloumns
            usercur.execute("SELECT * FROM Equipment")
            equips = usercur.fetchall()
            response = ""
            
            # Print out each equip
            for i in range(len(equips)):
                line = " " + equips[i][0] + ": " + equips[i][1]
                response += "      |%-53s|\n" % line

            response = HusciiQuest.scrollify(response)

        # print inventory
        if command.startswith("inventory"):
            # select all items in inventory
            usercur.execute("SELECT * FROM Inventory")
            items = usercur.fetchall()
            usercur.execute("SELECT * FROM Profile")
            gold = usercur.fetchall()[0]
            response = ""

            # print out item label
            response += "      |%-42s %s     |\n" % ("     Items", "Value")
            i = 1;

            # print out every item in a row
            for row in items:
                # check if item is equipped
                if row[4]:
                    # equipped
                    e = "[x]"
                else:
                    e = "[ ]"
                response += "      | %3s %-38s %4d %3s |\n" % (i, row[0], row[2], e)
                i += 1
                response += "      |       Level: %-3s CR: %-3s Slot: %-21s|\n" % (row[5], row[3], row[1])

            response += "      |%-53s|\n" % ""
            response += "      |     %-48s|\n" % ("Gold: " + str(gold[4]))
            
            response = HusciiQuest.scrollify(response)

        # print out profile
        if command.startswith("profile"):
            # get all from profile
            usercur.execute("SELECT * FROM Profile")
            profile = usercur.fetchall()[0]
            response = ""

            # print out the different columns
            response += "      | %-52s|\n" % profile[1]
            response += "      | %-52s|\n" % ("Exp: " + str(profile[2]) + "/" + str(profile[3]))
            response += "      | %-52s|\n" % ("Combat Rating: " + str(profile[5]))

            response = HusciiQuest.scrollify(response)

        # handle commands with shop
        if command.startswith("shop"):
            command = command.split("shop")[1].strip()
            # hqs.start()
            response = HQShop.shop(command, channel, user, usercon, usercur)

            if not response.startswith("`"):
                response = HusciiQuest.scrollify(response)

        if command.startswith("fight"):
            print('''
         xXXX  XXXXXXXX
         XX::XX........Xx
          XX""""OO..OOXX
          XX""""""""....XX
        xX..""""""""""""XX
       XX....""xxMM^^MM..
      xX..""""""""xxMM
      XX""""""""mm""mm
      xx""""xxxx..""..XX
      XXxx""""""xx""""XX
      XXxxxx""""xx""XXXX
``**--==XXMMMM""..MMMM..
            ''')
            response = "You encountered a rat."
            response += "\nYou killed a rat.\n"
            drop = HusciiQuest.genItem()
            response += drop[0]
            if drop[2] == 'onehand':
                slot = 'Weapon'
            else:
                slot = drop[2].title()
            usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", (drop[1], slot, drop[5], drop[4], 0, drop[3]))
            usercon.commit()

        if command.startswith("drop"):
            print('test gen')
            gen = HusciiQuest.genItem()
            response = gen[0]
            response = '`' + response + '`'
            item = (gen[1], gen[2], gen[4])
            print(response, item)

        return response
    """
         End HusciiQuest
        ,.*'`/~=-=~\`'*.,
    """
