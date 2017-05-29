"""
   __ ______    ___       __       __                
  / // / __ \  / _ \___ _/ /____ _/ /  ___ ____ ___  
 / _  / /_/ / / // / _ `/ __/ _ `/ _ \/ _ `(_-</ -_) 
/_//_/\___\_\/____/\_,_/\__/\_,_/_.__/\_,_/___/\__/  


"""

import sqlite3
import math
from Huscii import Huscii
from slackclient import SlackClient

keys = Huscii()
BOT_ID = keys.id
slack_client = SlackClient(keys.key)

class UtilDB:

    @staticmethod
    def item_dict(item):
        item = {'item' : item[0], 'slot' : item[1], 'value' : item[2], 'rating' : item[3], 'equipped' : item[4], 'level' : item[5]}
        return item

    @staticmethod
    def scrollify(response, i):
            scrollTop =  '      _' + '_' * i + '_ \n'
            scrollTop += '     /\ ' + ' ' * i + '\ \n'
            scrollTop += '(O)===)>' + '<>' * (int)(i/2) + '<)==(O) \n'
            scrollTop += '     \/"' + '"' * i + '/ \n'
            scrollTop += '      |' + ' ' * i + '|\n'

            scrollBot  = '      |' + ' ' * i + '|\n'
            scrollBot += '     /\\"' + '"' * i + '\ \n'
            scrollBot += '(O)===)>' + '<>' * (int)(i/2) + '<)==(O) \n'
            scrollBot += '     \/_' + '_' * i + '/'

            response = '```' + scrollTop + response + scrollBot + '```'
            return response


class UserDB:
    """
        Initialize the HQDatabse on a certain users

        ~ self.user : The userID being passed in through constructor
        ~ self.con : Sqlite3 connection to the user's database.
        ~ self.cur : The Sqlite3 cursor connection to the user's database.
        ~ self.profile : Tuple of the users profile data.
        ~ self.inventory : Array of tuples of the users inventory database.
        ~ self.equipment : Array of tuples of he users equipment database.
    """
    def __init__(self, userID):
        self.user = userID;
        self.con = sqlite3.connect('hquest/' + userID + '.db')
        self.cur = self.con.cursor()
        self.cur.execute('SELECT * FROM Profile')
        self.profile = self.cur.fetchall()[0]
        self.cur.execute('SELECT * FROM Inventory')
        self.inventory = self.cur.fetchall()
        self.cur.execute('SELECT * FROM Equipment')
        self.equipment = self.cur.fetchall()

    """
        Initialize all tables.
    """
    @staticmethod
    def start(userID):
        user = userID;
        con = sqlite3.connect('hquest/' + userID + '.db')
        cur = con.cursor()
        response = ''

        api_call = slack_client.api_call('users.list')
        if api_call.get('ok'):
            # print('api call gucci fam')
            # retrieve all users so we can find our username
            users = api_call.get('members')
            for u in users:
                if 'id' in u and u.get('id') == user.strip():
                    username = u.get('name')
                    # print('Username aquired')

        try:
            # create equip table and fill with none

            # self.cur.execute('CREATE TABLE Equipment(Head TEXT, Hands TEXT, Chest TEXT, Legs TEXT, Feet TEXT, Weapon TEXT, Offhand TEXT)')
            # self.cur.execute('INSERT INTO Equipment VALUES(?, ?, ?, ?, ?, ?, ?)', ('None', 'None', 'None', 'None', 'None', 'None', 'None'))

            cur.execute('CREATE TABLE Equipment(Slot TEXT, Item TEXT)')
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Head', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Hands', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Chest', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Legs', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Feet', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Weapon', 'None'))
            cur.execute('INSERT INTO Equipment VALUES(?, ?)', ('Offhand', 'None'))
            print('equips made')

            # create inventory table
            cur.execute('CREATE TABLE Inventory(Item TEXT, Slot TEXT, Value INT, Rating INT, Equipped BOOLEAN, ItemLevel INT)')
            # add wooden sword and shield
            cur.execute('INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)', ('Wooden Sword', 'Weapon', 1, 1, 0, 1))
            cur.execute('INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)', ('Wooden Shield', 'Offhand', 1, 1, 0, 1))
            print('inventory made')

            # create profile table
            cur.execute('CREATE TABLE Profile(UserID TEXT, Username TEXT, ExpCur INT, ExpMax INT, Gold INT, Cr INT, Level INT)')
            # insert default values
            cur.execute('INSERT INTO Profile VALUES(?, ?, ?, ?, ?, ?, ?)', (user, username, 0, 10, 50, 0, 1))
            print('profile made')

            # commit changes
            con.commit()
            con.close()

            return 'Profile made.'

        except sqlite3.Error:
            # oh no
            return 'You have a profile already or there was an error'


    """
        Updates the self.profile field to the current data in the profile table.
    """
    def update_profile(self):
        self.cur.execute('SELECT * FROM Profile')
        self.profile = self.cur.fetchall()[0]

    """
        Updates the self.inventory field to the current data in the inventory table.
    """
    def update_inventory(self):
        self.cur.execute('SELECT * FROM Inventory')
        self.inventory = self.cur.fetchall()

    """
        Updates the self.equipment field to the current data in the equipment table.
    """
    def update_equipment(self):
        self.cur.execute('SELECT * FROM Equipment')
        self.equipment = self.cur.fetchall()

    def print_profile(self):
        self.update_profile()
        print(self.profile)

    def print_inventory(self):
        self.update_inventory()
        print(self.inventory)

    def print_equips(self):
        self.update_equipment()
        print(self.equipment)

    def prof(self):
        self.update_profile()
        profile = self.profile
        response = ''

        # print out the different columns
        response += '      | %-39s|\n' % self.get_username()
        response += '      | %-39s|\n' % ("Level: " + str(self.get_level()))
        response += '      | %-39s|\n' % ("Exp: " + str(self.get_exp_cur()) + "/" + str(self.get_exp_max()))
        response += '      | %-39s|\n' % ("Combat Rating: " + str(self.get_cr()))

        response = UtilDB.scrollify(response, 40)

        return response

    def inven(self):
        self.update_inventory()
        # select all items in inventory
        # self.cur.execute('SELECT * FROM Inventory')
        # items = self.cur.fetchall()
        items = self.inventory
        response = ''

        # print out item label
        response += '      |%-51s %4s %4s %8s %4s     |\n' % ('     Items', 'CR', 'Lvl', 'Slot', 'GP')
        i = 1;

        # print out every item in a row
        for row in items:
            item = UtilDB.item_dict(row)
            # check if item is equipped
            if item['equipped']:
                # equipped
                e = '[x]'
            else:
                e = '[ ]'
            response += '      | %3s %-46s %4s %4s %8s %4s %3s |\n' % (i, item['item'], item['rating'], item['level'], item['slot'], item['value'], e)
            i += 1

        response += '      |%-80s|\n' % ''
        response += '      |     %-75s|\n' % ('Gold: ' + str(self.get_gold()))
        
        response = UtilDB.scrollify(response, 80)

        return response

    def equips(self):
        self.update_equipment()
        self.cur.execute('SELECT * FROM Equipment')
        equips = self.cur.fetchall()
        response = ''
        
        # Print out each equip
        for i in range(len(equips)):
            line = ' ' + equips[i][0] + ': ' + equips[i][1]
            response += '      |%-60s|\n' % line

        response = UtilDB.scrollify(response, 60)

        return response

    """
        Return str of the exp as 'ExpCur/ExpMax', '10/20'
    """
    def get_exp(self):
        return str(self.profile[2]) + '/' + str(self.profile[3])

    """
        Return the various values in the profile table of the user.
    """
    # UserID
    def get_user_id(self):
        return self.profile[0]

    # Username
    def get_username(self):
        return self.profile[1]

    # Current experience
    def get_exp_cur(self):
        return self.profile[2]

    # Max experience
    def get_exp_max(self):
        return self.profile[3]

    # Gold
    def get_gold(self):
        return self.profile[4]

    # Combat rating
    def get_cr(self):
        return self.profile[5]

    # Level
    def get_level(self):
        return self.profile[6]

    """
        Set's the gold of the users to the value.

        ~ gold : The gold value
    """
    def set_gold(self, gold):
        self.cur.execute('UPDATE Profile SET Gold = ?', (gold,))
        self.con.commit()

    """
        Adds exp to the current user if the amount is over the current max exp that the current
        level then it increments till the max exp reaches an amount over the current exp amount.
        Otherwise just adds the exp to the current exp amount.

        ~ exp : Integer amount of exp being added
    """
    def add_exp(self, exp):
        # If the current exp would be greater than max
        if self.get_exp_cur() + exp >= self.get_exp_max():
            # Get all the variables for calculating new level
            expCur = self.get_exp_cur() + exp
            expMax = self.get_exp_max()
            level = self.get_level()
            # Increase max experience while its less than current experience
            while expCur >= expMax:
                # Exp addition calculation
                expMax = (int) (expMax + (10 * level * math.log10(expMax)))
                level += 1;

            # Set the new values to the profile table
            self.cur.execute('UPDATE Profile SET ExpMax = ?', (expMax,))   
            self.cur.execute('UPDATE Profile SET ExpCur = ?', (expCur,))
            self.cur.execute('UPDATE Profile SET Level = ?', (level,))
        else:
            # Add the exp to the current experience amount.
            expCur = self.get_exp_cur() + exp
            self.cur.execute('UPDATE Profile SET ExpCur = ?', (expCur,))

        # Commit changes and update self.profile field
        self.con.commit()

    """
        Set the combat rating of the user

        ~ cr : Integer combat rating value
    """
    def set_cr(self, cr):
        # Update the cr value in the profile table
        self.cur.execute('UPDATE Profile SET Cr = ?', (cr,))

        # Commit changes and update self.profile field
        self.con.commit()

    """
        Inserts a new item into the user's inventory table

        ~ item : A tuple of all the items properties
            ('item', 'slot', 'value', 'combat rating', 'equipped', 'level')
    """
    def add_item(self, item):
        self.cur.execute('INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)', (item['item'], item['slot'], item['value'], item['rating'], 0, item['level']))
        self.con.commit()

    """
        Removes an item from the user's inventory table

        ~ item : Str of the item's name
    """
    def remove_item(self, item):
        self.cur.execute('DELETE FROM Inventory WHERE Item = ?', (item,))
        self.con.commit()

    def get_item(self, item):
        print(type(item))
        try:
            item = int(item)
            self.cur.execute('SELECT * FROM Inventory LIMIT 1 OFFSET ?', (item - 1,))
            item = self.cur.fetchall()
            if len(item):
                return UtilDB.item_dict(item[0])
            else:
                return 'Couldn\'t find row'
        except ValueError:
            self.cur.execute('SELECT * FROM Inventory WHERE Item LIKE ?', ('%' + item + '%',))
            item = self.cur.fetchall()
            if len(item) == 1:
                return UtilDB.item_dict(item[0])
            else:
                print(item)
                response = "Found " + str(len(item)) + " please refine search"
                if len(item) > 0:
                    response += '\n'
                    for row in item:
                        response += '  ' + row[0] + '\n'
                return '```' + response + '```'


    """
        Equips an item to the players equipment slots by inserting it into the equipment table, also updates the values
        on the user's profile increasing the combat rating by weapon amount. Updates the equipped boolean in the item's
        inventory field also.

        ~ item : Str of the item's name to be equipped
    """
    def equip_item(self, item):
        # Uses LIKE to try to find a TEXT field in the ITEM column similar to the item str
        self.cur.execute('SELECT * FROM Inventory WHERE Item LIKE ?', ('%' + item + '%',))
        item = self.cur.fetchall()

        # If item is found
        if(len(item) != 0):
            item = item[0]
            # Create a dict of the items field so that dict values can be used to access the different tuple values
            item = {'item' : item[0], 'slot' : item[1], 'value' : item[2], 'rating' : item[3], 'equipped' : item[4], 'level' : item[5]}

            # Check to see that the is not equipped, is an equipment item, and item level is greater than the player level
            if (item['equipped'] and item['slot'] != 'Other') or item['level'] > self.get_level():
                if item['equipped']:
                    response = 'Item is already equipped'
                else:
                    response = 'You are not high enough level, required level is: ' + str(item['level'])
            else:
                # If the item is a two handed weapon equip the item to both the main weapon slot and the offhand slot
                if item['slot'] == 'Twohand':
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', (item['item'], 'Weapon'))
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', (item['item'], 'Offhand'))
                
                # Equip the item to the slot listed
                else:
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', (item['item'], item['slot']))
                
                # Update combat rating and set it in the profile
                cr = item['rating'] + self.get_cr()
                self.set_cr(cr)
                # Update the equipped boolean in the items equipped column in the table
                self.cur.execute('UPDATE Inventory SET Equipped = 1 WHERE Item = ?', (item['item'],))
                response = 'You equipped ' + item['item']
        else:
            response = 'Cannot find item'

        # Commit changes and update the self.profile and the self.inventory fields
        self.con.commit()

        # Return the response for bot to send
        return '`' + response + '`'

    """
        Unequips an item from the user, sets the equipment item columns to 'none', updates the profile cr, and updates
        the items equipped boolean column.

        ~ item : Str of the item name
    """
    def unequip_item(self, item):
        # Uses LIKE to try to find a TEXT field in the ITEM column similar to the item str
        self.cur.execute('SELECT * FROM Inventory WHERE Item LIKE ?', ('%' + item + '%',))
        item = self.cur.fetchall()

        if(len(item) != 0):
            item = item[0]
            # Create a dict of the items field so that dict values can be used to access the different tuple values
            item = {'item' : item[0], 'slot' : item[1], 'value' : item[2], 'rating' : item[3], 'equipped' : item[4], 'level' : item[5]}
            if item['equipped']:
                # If the slot is a two handed weapon set both off weapon and offhand to none
                if item['slot'] == 'Twohand':
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', ('None', 'Weapon'))
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', ('None', 'Offhand'))
                
                # Unequip the item to the slot listed
                else:
                    self.cur.execute('UPDATE Equipment SET Item = ? WHERE Slot = ?', ('None', item['slot']))

                # Update combat rating and set it in the profile
                cr = self.get_cr() - item['rating']
                self.set_cr(cr)
                self.cur.execute('UPDATE Inventory SET Equipped = 0 WHERE Item = ?', [command])
                response = 'You unequipped ' + command
            else:
                response = 'Item is not equipped'
        else:
            response = 'Cannot find item'

        # Commit changes and update the self.profile and the self.inventory fields
        self.con.commit()

        # Return the response for bot to send
        return '`' + response + '`'

    def close_con(self):
        self.con.close()

class ShopDB:

    def __init__(self, user):
        if isinstance(user, str):
            user = UserDB(user)
        self.user = user
        self.con = sqlite3.connect('hquest/shop.db')
        self.cur = self.con.cursor()
        # self.cur.execute('SELECT * FROM Shop');
        # self.shop = self.cur.fetchall();

    def start(self):
        self.cur.execute('CREATE TABLE Shop(Item TEXT, Slot TEXT, Value INT, Rating INT, Equipped BOOLEAN,Level INT)')
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Cloth Hat', 'Head', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Cloth Gloves', 'Hands', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Cloth Tunic', 'Chest', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Cloth Pants', 'Legs', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Cloth Wraps', 'Feet', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Rusted Sword', 'Weapon', 10, 5, 0, 2))
        self.cur.execute('INSERT INTO Shop VALUES(?, ?, ?, ?, ?, ?)', ('Rusted Buckler', 'Offhand', 10, 5, 0, 2))
        print('Shop made')

        self.con.commit()

    def update_shop(self):
        self.cur.execute('SELECT * FROM Shop');
        self.shop = self.cur.fetchall();            

    def list(self):
        self.cur.execute('SELECT * FROM Shop')
        shop = self.cur.fetchall()
        response = '      | %-25s %8s %4s %4s |\n' % ('Item', 'Slot', 'CR', 'GP')
        for i in range(0, len(shop)):
            response += '      | %-25s %8s %4d %4d |\n' % (shop[i][0], shop[i][1], shop[i][2], shop[i][3])

        return UtilDB.scrollify(response, 46)

    def buy(self, item):
        self.cur.execute('SELECT * FROM Shop WHERE Item = ?', [item])
        item = self.cur.fetchall()

        if(len(item) != 0):
            item = UtilDB.item_dict(item[0])
            if  self.user.get_gold() >= item['value']:
                gold = self.user.get_gold() - item['value']
                print(type(gold))
                # usercur.execute('UPDATE Profile SET Gold = ?', [gold])
                self.user.set_gold(gold)
                # usercur.execute('INSERT INTO Inventory VALUES(?, ?, ?, ?, ?)', (item[0], item[1], item[3], item[2], 0)) 
                self.user.add_item(item)
                response = 'You bought a ' + item['item']
            else:
                response = 'You don\'t have enough gold'
        else:
            response = 'Can\'t find item'
        
        self.con.commit()
        
        return '`' + response + '`'

    def sell(self, item):
        # self.cur.execute("SELECT * FROM Inventory WHERE Item = ?", [item])
        # item = usercur.fetchall()
        item = self.user.get_item(item)
        # print(item)
        if type(item) is dict:
            gold = self.user.get_gold() + item['value']
            self.user.set_gold(gold)
            self.user.remove_item(item['item'])
            return '`You sold a ' + item['item'] + ' for ' + str(item['value']) + ' gold`'
        else:
            return item

    def close_con(self):
        self.con.close()

class TradeDB:

    @staticmethod
    def start():
        con = sqlite3.connect('hquest/trades.db')
        cur = con.cursor()

        cur.execute('CREATE TABLE Trades(User TEXT, Partner TEXT, UserID TEXT, PartnerID TEXT, Offer CLOB, Ask CLOB, UA BOOLEAN, PA BOOLEAN)')

        con.close()

    @staticmethod
    def open(user, partner):
        partnerid = ''
        api_call = slack_client.api_call('users.list')
        if api_call.get('ok'):
            # print('api call gucci fam')
            # retrieve all users so we can find our username
            users = api_call.get('members')
            for u in users:
                if 'name' in u and u.get('name') == partner.strip():
                    partnerid = u.get('id')

        print(user.get_user_id(), partnerid)

        con = sqlite3.connect('hquest/trades.db')
        cur = con.cursor()

        if len(partnerid):
            cur.execute('SELECT * FROM Trades WHERE (UserID = ? AND PartnerID = ?) OR (UserID = ? and PartnerID = ?)', (user.get_user_id(), partnerid, partnerid, user.get_user_id()))
            trade = cur.fetchall()
            response = ''
            if user.get_user_id() == partnerid:
                response = 'You can\'t open a trade with yourself.'
            elif len(trade) > 0:
                response = 'You already have a trade open with ' + partner
            else:
                cur.execute('INSERT INTO Trades VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (user.get_username(), partner, user.get_user_id(), partnerid, "None", "None", 0, 0))
                response = 'Trade opened with ' + partner
        else:
            response = 'Couldn\'t find partner.'
        
        con.commit()
        con.close()
        return '`' + response + '`'

    def __init__(self, user):
        self.user = user
        self.con = sqlite3.connect('hquest/trades.db')
        self.cur = self.con.cursor()

    def display(self):
        self.cur.execute('SELECT * FROM Trades WHERE UserID = ? OR PartnerID = ?', (self.user.get_user_id(), self.user.get_user_id()))
        trades = self.cur.fetchall()
        response = ''
        if len(trades) == 0:
            response = '`No trades currently open`'
        else:
            for row in trades:
                response += str(row) + '\n'
            response = '```' + response + '```'

        return response        

    def offer(self, partner, item):
        trade = self.get_trade(partner)
        if len(trade):
            if trade[0][6] or trade[0][7]:
                response = 'The trade has been accepted by one party you can\'t modify it now'
            else:
                item = self.user.get_item(item)
                if self.user.get_username() == trade[0][0] and type(item) is dict:
                    print('Here')
                    self.cur.execute('UPDATE Trades SET Offer = ? WHERE User = ? AND Partner = ?', (item['item'], self.user.get_username(), partner))
                    response = 'You offered a ' + item['item'] + ' to ' + partner
                elif type(item) is dict:
                    print('Here2')
                    self.cur.execute('UPDATE Trades SET Ask = ? WHERE Partner = ? AND User = ?', (item['item'], self.user.get_username(), partner))
                    response = 'You offered a ' + item['item'] + ' to ' + partner
                else:
                    response = item
        else:
            response = 'No trade open with ' + partner

        self.con.commit()
        return '`' + response + '`'

    def rm_offer(self, partner, item):
        pass

    def accept(self, partner):
        response = ''
        trade = self.get_trade(partner)
        if len(trade):
            if trade[0][0] == self.user.get_username():
                self.cur.execute('UPDATE Trades SET UA = ? WHERE User = ? and Partner = ?', (1, self.user.get_username(), partner))
                response = 'You accepted trade with ' + partner
            else:
                self.cur.execute('UPDATE Trades SET PA = ? WHERE Partner = ? and User = ?', (1, self.user.get_username(), partner))
                response = 'You accepted trade with ' + partner

            trade = self.get_trade(partner)[0]
            if trade[6] and trade [7]:
                response = self.complete_trade(partner)

        else:
            response = 'Couldn\'t find trade'

        self.con.commit()
        return '`' + response + '`'

    def reject(self, partner):
        response = ''
        trade = self.get_trade(partner)
        if len(trade):
            if trade[0][0] == self.user.get_username():
                self.cur.execute('UPDATE Trades SET UA = ? WHERE User = ? and Partner = ?', (0, self.user.get_username(), partner))
                response = 'You unaccepted trade with ' + partner
            else:
                self.cur.execute('UPDATE Trades SET PA = ? WHERE Partner = ? and User = ?', (0, self.user.get_username(), partner))
                response = 'You unaccepted trade with ' + partner
        else:
            response = 'Couldn\'t find trade'

        self.con.commit()
        return '`' + response + '`'

    def stop(self, partner):
        self.cur.execute('DELETE FROM Trades WHERE (UserID = ? AND Partner = ?) OR (User = ? and PartnerID = ?)', \
            (self.user.get_user_id(), partner, partner, self.user.get_user_id()))
        self.con.commit()
        return '`Trade closed.`'

    def get_trade(self, partner):
        self.cur.execute('SELECT * FROM Trades WHERE UserID = ? AND Partner = ? OR User = ? and PartnerID = ?', \
            (self.user.get_user_id(), partner, partner, self.user.get_user_id()))
        return self.cur.fetchall()

    def complete_trade(self, partner):
        trade = self.get_trade(partner)[0]
        # print(trade)
        if self.user.get_username() == trade[0]:
            # print(trade[3])
            partnerData = UserDB(trade[3])
            item1 = self.user.get_item(trade[4])
            item2 = partnerData.get_item(trade[5])
            print(item1)
            print(item2)
            if (type(item1) is dict and item1['item'] != trade[4]) or (type(item2) is dict and item2['item'] != trade[5]) \
            or (type(item1) is not dict and 'None' != trade[4]) or (type(item2) is not dict and 'None' != trade[5]):
                self.stop(partner)
                return 'Items not found, trade couldn\'t complete'
        else:
            partnerData = UserDB(trade[2])
            item1 = self.user.get_item(trade[5])
            item2 = partnerData.get_item(trade[4])
            print(item1)
            print(item2)
            if (type(item1) is dict and item1['item'] != trade[5]) or (type(item2) is dict and item2['item'] != trade[4]) \
            or (type(item1) is not dict and 'None' != trade[5]) or (type(item2) is not dict and 'None' != trade[4]):
                self.stop(partner)
                return 'Items not found, trade couldn\'t complete'

        if (type(item1) is dict and int(item1['equipped'])) or (type(item2) is dict and int(item2['equipped'])):
            response = 'Items must be unequipped to trade'
            self.reject(partnerData.get_user_id())
        else:

            if type(item1) is dict:
                partnerData.add_item(item1)
                self.user.remove_item(item1['item'])

            if type(item2) is dict:
                self.user.add_item(item2)
                partnerData.remove_item(item2['item'])

            self.stop(partner)
            response = 'Trade completed'

        return response

    def close_con(self):
        self.con.close()

# class FightDB:
