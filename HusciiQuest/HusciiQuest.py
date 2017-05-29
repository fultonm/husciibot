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
from HQFight import HQFight
from HQDatabase import UserDB, ShopDB, TradeDB
from slackclient import SlackClient

keys = Huscii()
BOT_ID = keys.id
slack_client = SlackClient(keys.key)

class HusciiQuest:

    @staticmethod
    def husciiQuest(command, channel, user):
        # connect to user database
        # usercon = sqlite3.connect("hquest/" + user + ".db")
        # usercur = usercon.cursor()
        response = "Something went wrong with [hquest] type help for commands"

        # create a new profile
        if command.startswith("new profile"):
            response = UserDB.start(user)

        try:
            userData = UserDB(user)
        except Exception:
            return '`You Must create a profile, use [new profile]`'

        shopData = ShopDB(userData)
        trade = TradeDB(userData)

        # handle commands with items
        if command.startswith("item"):
            command = command.split("item")[1].strip()

            # equip an item
            if command.startswith("equip"):
                command = command.split("equip")[1].strip()
                return userData.equip(command)


            # unequip item
            if command.startswith("unequip"):
                command = command.split("unequip")[1].strip()
                return userData.unequip(command)

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
            return userData.equips()

        # print inventory
        if command.startswith("inventory"):
            return userData.inven()

        # print out profile
        if command.startswith("profile"):
            # get all from profile
            return userData.prof()

        # handle commands with shop
        if command.startswith("shop"):
            command = command.split("shop")[1].strip()
            # shopData.start()
            response = HQShop.shop(command, channel, shopData)

        if command.startswith("fight"):
            # HQFight.start()
            response = ''
            response = HQFight.fight(command, channel, userData)

        if command.startswith("drop"):
            print('test gen')
            gen = HusciiQuest.genItem()
            response = gen[0]
            response = '`' + response + '`'
            item = (gen[1], gen[2], gen[4])
            print(response, item)

        if command.startswith("trade"):
            # TradeDB.start()
            # @husciibot husciiquest trade open partner
            command = command.split('trade')[1].strip()
            if command.startswith('open'):
                command = command.split('open')[1].strip()
                if len(command):
                    response = TradeDB.open(userData, command)
                    # response = 'You opened a trade with ' + command
                else:
                    response = 'You must enter a trade partner'

            elif command.startswith('list'):
                response = trade.display()

            elif command.startswith('offer'):
                command = command.split('offer')[1].strip()
                # print(command)
                partner = command.split(' ')[0]
                # print(partner)
                command = command.split(partner)
                # print(command)
                if len(command) == 2:
                    response = trade.offer(partner, command[1].strip())
                else:
                    response = '`Couldn\'t offer item.`'

            elif command.startswith('accept'):
                command = command.split('accept')[1].strip()
                response = trade.accept(command)

            elif command.startswith('reject'):
                command = command.split('reject')[1].strip()
                response = trade.reject(command)

            elif command.startswith('stop'):
                command = command.split('stop')[1].strip()
                response = trade.stop(command)


        userData.close_con()
        shopData.close_con()
        trade.close_con()
        return response

"""
     End HusciiQuest
    ,.*'`/~=-=~\`'*.,
"""
