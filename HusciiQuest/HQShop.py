import sqlite3

con = sqlite3.connect("hquest/shop.db")
cur = con.cursor()

class HQShop():

    @staticmethod
    def start():
        cur.execute("CREATE TABLE Shop(Item TEXT, Slot TEXT, Rating INT, Cost INT)")
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Cloth Hat", "Head", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Cloth Hat", "Hands", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Cloth Hat", "Chest", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Cloth Hat", "Legs", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Cloth Hat", "Feet", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Rusted Sword", "Weapon", 5, 10))
        cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", ("Rusted Buckler", "Offhand", 5, 10))
        print("Shop made")

        con.commit()
    
    @staticmethod
    def shop(command, channel, user, ucon, ucur):
        response = ""

        # usercon = sqlite3.connect("hquest/" + user + ".db")
        # usercur = usercon.cursor()
        usercon = ucon
        usercur = ucur

        if command.startswith("list"):
            cur.execute("SELECT * FROM Shop");
            shop = cur.fetchall();

            response += "      | %-32s %8s %4s %4s |\n" % ("Item", "Slot", "CR", "GP")
            for i in range(0, len(shop)):
                response += "      | %-32s %8s %4d %4d |\n" % (shop[i][0], shop[i][1], shop[i][2], shop[i][3])

        if command.startswith("buy"):
            command = command.split("buy")[1].strip()

            cur.execute("SELECT * FROM Shop WHERE Item = ?", [command])
            item = cur.fetchall()
            usercur.execute("SELECT * FROM Profile")
            profile = usercur.fetchall()[0]
            print(profile, item)

            if(len(item) != 0):
                item = item[0]
                if  profile[4] >= item[3]:
                    gold = profile[4] - item[3]
                    print(type(gold))
                    usercur.execute("UPDATE Profile SET Gold = ?", [gold])
                    usercur.execute("INSERT INTO Inventory VALUES(?, ?, ?, ?, ?)", (item[0], item[1], item[3], item[2], 0)) 
                    response = "You bought a " + command
                else:
                    response = "You don't have enough gold"
            else:
                response = "Can't find item"
            
            response = "`" + response + "`"
            con.commit()
            usercon.commit()

        return response