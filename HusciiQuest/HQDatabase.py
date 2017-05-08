import sqlite3
import math
from Huscii import Huscii
from slackclient import SlackClient

keys = Huscii()
BOT_ID = keys.id
slack_client = SlackClient(keys.key)

class UserDB:
    """
        Initialize the HQDatabse on a certain user

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
    def start(user):
        api_call = slack_client.api_call("users.list")
        if api_call.get('ok'):
            # print("api call gucci fam")
            # retrieve all users so we can find our username
            users = api_call.get('members')
            for u in users:
                if 'id' in u and u.get('id') == user.strip():
                    username = u.get('name')
                    # print("Username aquired")

        try:
            # create equip table and fill with none

            # self.cur.execute("CREATE TABLE Equipment(Head TEXT, Hands TEXT, Chest TEXT, Legs TEXT, Feet TEXT, Weapon TEXT, Offhand TEXT)")
            # self.cur.execute("INSERT INTO Equipment VALUES(?, ?, ?, ?, ?, ?, ?)", ("None", "None", "None", "None", "None", "None", "None"))

            self.cur.execute("CREATE TABLE Equipment(Slot TEXT, Item TEXT)")
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Head", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Hands", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Chest", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Legs", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Feet", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Weapon", "None"))
            self.cur.execute("INSERT INTO Equipment VALUES(?, ?)", ("Offhand", "None"))
            print("equips made")

            # create inventory table
            self.cur.execute("CREATE TABLE Inventory(Item TEXT, Slot TEXT, Value INT, Rating INT, Equipped BOOLEAN, ItemLevel INT)")
            # add wooden sword and shield
            self.cur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", ("Wooden Sword", "Weapon", 1, 1, 0, 1))
            self.cur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", ("Wooden Shield", "Offhand", 1, 1, 0, 1))
            print("inventory made")

            # create profile table
            self.cur.execute("CREATE TABLE Profile(UserID TEXT, Username TEXT, ExpCur INT, ExpMax INT, Gold INT, Cr INT, Level INT)")
            # insert default values
            self.cur.execute("INSERT INTO Profile VALUES(?, ?, ?, ?, ?, ?, ?)", (self.user, username, 0, 10, 50, 0, 1))
            print("profile made")

            # commit changes
            self.con.commit()
            self.updateProfile()
            self.updateInventory()
            self.updateEquipment()

            return "Profile made."

        except sqlite3.Error:
            # oh no
            response = "You have a profile already or there was an error"


    """
        Updates the self.profile field to the current data in the profile table.
    """
    def updateProfile(self):
        self.cur.execute('SELECT * FROM Profile')
        self.profile = self.cur.fetchall()[0]

    """
        Updates the self.inventory field to the current data in the inventory table.
    """
    def updateInventory(self):
        self.cur.execute('SELECT * FROM Inventory')
        self.inventory = self.cur.fetchall()

    """
        Updates the self.equipment field to the current data in the equipment table.
    """
    def updateEquipment(self):
        self.cur.execute('SELECT * FROM Equipment')
        self.equipment = self.cur.fetchall()

    def printProfile(self):
        print(self.profile)

    def printInventory(self):
        print(self.inventory)

    def printEquips(self):
        print(self.equipment)

    """
        Return str of the exp as 'ExpCur/ExpMax', '10/20'
    """
    def getExp(self):
        return str(self.profile[2]) + '/' + str(self.profile[3])

    def getUserID(self):
        return self.profile[0]

    def getUsername(self):
        return self.profile[1]

    def getExpCur(self):
        return self.profile[2]

    def getExpMax(self):
        return self.profile[3]

    def getGold(self):
        return self.profile[4]

    def getCR(self):
        return self.profile[5]

    def getLevel(self):
        return self.profile[6]

    """
        Set's the gold of the users to the value.

        ~ gold : The gold value
    """
    def setGold(self, gold):
        self.cur.execute('UPDATE Profile SET Gold = ?', (gold,))
        self.con.commit()
        self.updateProfile()
    """
        Adds exp to the current user if the amount is over the current max exp that the current
        level then it increments till the max exp reaches an amount over the current exp amount.
        Otherwise just adds the exp to the current exp amount.

        ~ exp : Integer amount of exp being added
    """
    def addExp(self, exp):
        # If the current exp would be greater than max
        if self.getExpCur() + exp >= self.getExpMax():
            # Get all the variables for calculating new level
            expCur = self.getExpCur() + exp
            expMax = self.getExpMax()
            level = self.getLevel()
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
            expCur = self.getExpCur() + exp
            self.cur.execute('UPDATE Profile SET ExpCur = ?', (expCur,))

        # Commit changes and update self.profile field
        self.con.commit()
        self.updateProfile()

    """
        Set the combat rating of the user

        ~ cr : Integer combat rating value
    """
    def setCR(self, cr):
        # Update the cr value in the profile table
        self.cur.execute('UPDATE Profile SET Cr = ?', (cr,))

        # Commit changes and update self.profile field
        self.con.commit()
        self.updateProfile()

    """
        Inserts a new item into the user's inventory table

        ~ item : A tuple of all the items properties
            ('item', 'slot', 'value', 'combat rating', 'equipped', 'level')
    """
    def addItem(self, item):
        self.cur.execute('INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)', (item[0], item[1], item[2], item[3], 0, item[5]))

    """
        Removes an item from the user's inventory table

        ~ item : Str of the item's name
    """
    def removeItem(self, item):
        self.cur.execute('DELETE FROM Inventory WHERE Item = ?', (item,))

    """
        Equips an item to the players equipment slots by inserting it into the equipment table, also updates the values
        on the user's profile increasing the combat rating by weapon amount. Updates the equipped boolean in the item's
        inventory field also.

        ~ item : Str of the item's name to be equipped
    """
    def equipItem(self, item):
        # Uses LIKE to try to find a TEXT field in the ITEM column similar to the item str
        self.cur.execute("SELECT * FROM Inventory WHERE Item LIKE ?", ('%' + item[0] + '%',))
        item = self.cur.fetchall()

        # If item is found
        if(len(item) != 0):
            item = item[0]
            # Create a dict of the items field so that dict values can be used to access the different tuple values
            item = {'item' : item[0], 'slot' : item[1], 'value' : item[2], 'rating' : item[3], 'equipped' : item[4], 'level' : item[5]}

            # Check to see that the is not equipped, is an equipment item, and item level is greater than the player level
            if (item['equipped'] and item['slot'] != "Other") or item['level'] > self.getLevel():
                if item['equipped']:
                    response = "Item is already equipped"
                else:
                    response = "You are not high enough level, required level is: " + str(item['level'])
            else:
                # If the item is a two handed weapon equip the item to both the main weapon slot and the offhand slot
                if item['slot'] == 'Twohand':
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item['item'], 'Weapon'))
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item['item'], 'Offhand'))
                
                # Equip the item to the slot listed
                else:
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", (item['item'], item['slot']))
                
                # Update combat rating and set it in the profile
                cr = item['rating'] + self.getCR()
                self.setCR(cr)
                # Update the equipped boolean in the items equipped column in the table
                self.cur.execute("UPDATE Inventory SET Equipped = 1 WHERE Item = ?", (item['item'],))
                response = "You equipped " + item['item']
        else:
            response = "Cannot find item"

        # Commit changes and update the self.profile and the self.inventory fields
        self.con.commit()
        self.updateProfile()
        self.updateInventory()

        # Return the response for bot to send
        return response

    """
        Unequips an item from the user, sets the equipment item columns to 'none', updates the profile cr, and updates
        the items equipped boolean column.

        ~ item : Str of the item name
    """
    def unequipItem(self, item):
        # Uses LIKE to try to find a TEXT field in the ITEM column similar to the item str
        self.cur.execute("SELECT * FROM Inventory WHERE Item LIKE ?", ('%' + item[0] + '%',))
        item = self.cur.fetchall()

        if(len(item) != 0):
            item = item[0]
            # Create a dict of the items field so that dict values can be used to access the different tuple values
            item = {'item' : item[0], 'slot' : item[1], 'value' : item[2], 'rating' : item[3], 'equipped' : item[4], 'level' : item[5]}
            if item['equipped']:
                # If the slot is a two handed weapon set both off weapon and offhand to none
                if item['slot'] == 'Twohand':
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", 'Weapon'))
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", 'Offhand'))
                
                # Unequip the item to the slot listed
                else:
                    self.cur.execute("UPDATE Equipment SET Item = ? WHERE Slot = ?", ("None", item['slot']))

                # Update combat rating and set it in the profile
                cr = self.getCR() - item['rating']
                self.setCR(cr)
                self.cur.execute("UPDATE Inventory SET Equipped = 0 WHERE Item = ?", [command])
                response = "You unequipped " + command
            else:
                response = "Item is not equipped"
        else:
            response = "Cannot find item"

        # Commit changes and update the self.profile and the self.inventory fields
        self.con.commit()
        self.updateProfile()
        self.updateInventory()

        # Return the response for bot to send
        return response
