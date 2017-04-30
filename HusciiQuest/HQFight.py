import sqlite3
import random
import json

con = sqlite3.connect("hquest/monster.db")
cur = con.cursor()

class HQFight():

    @staticmethod
    def start():
        cur.execute("CREATE TABLE Monster(Name TEXT, Art TEXT, Level INT, Cr INT, Experience INT)");
        rat = '''
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
            '''
        cur.execute("INSERT INTO Monster VALUES(?, ?, ?, ?, ?)", ('Rat', rat, 1, 1, 1));
        cur.execute("INSERT INTO Monster VALUES(?, ?, ?, ?, ?)", ("Lucky Rat", rat, 50, 1, 1));

        con.commit()

    @staticmethod
    def fight(command, channel, user, ucon, ucur):
        usercon = ucon
        usercur = ucur

        if command.startswith("fight"):
            cur.execute("SELECT * FROM Monster WHERE Name = ?", ['Lucky Rat'])
            monster = cur.fetchall()[0];
            print(monster)
            print(monster[1])
            response = "You encountered a " + monster[0] + "."
            response += "\nYou killed a " + monster[0] + ".\n"
            drop = HQFight.genItem(monster[2])
            response += drop[0]
            if drop[2] == 'onehand':
                slot = 'Weapon'
            else:
                slot = drop[2].title()
            usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?, ?)", (drop[1], slot, drop[5], drop[4], 0, drop[3]))
            usercon.commit()
        return response

    def genItem(level):
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