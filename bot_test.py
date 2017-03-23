import sqlite3

con = sqlite3.connect("test.db")
cur = con.cursor()

def makeTable():
    # cur.execute("DROP TABLE IF EXISTS Events")
    try:
        cur.execute("CREATE TABLE Events(Id TEXT, TheDate TEXT, Name TEXT)")
    except sqlite3.Error:
        pass

def handle_command(command):
    if command.startswith("new"):
        newCommand = command.split("new")[1].strip().lower()
        commandList = newCommand.split(" ")
        # print commandList
        if newCommand.startswith("event") and len(commandList) == 4 and commandList[1].isdigit():
            # print commandList[1], commandList[2], commandList[3]
            cur.execute("INSERT INTO Events VALUES(?, ?, ?)", (commandList[1], commandList[2], commandList[3]))
            con.commit()
            #cur.execute("SELECT * FROM Events WHERE Id == 1")
            #event = cur.fetchall()
            #print event
    if command.startswith("delete"):
        deleteCommand = command.split("delete")[1].strip().lower()
        cur.execute("DELETE FROM Events WHERE Id == ?", deleteCommand)
    
    if command.startswith("list"):
        listCommand = command.split("list")[1].strip().lower()
        if listCommand.startswith("events"):
            cur.execute("SELECT * FROM Events")
            event_names = [en[0] for en in cur.description]
            event = cur.fetchall()
            print "%s %-10s %s" % (event_names[0], event_names[1], event_names[2])

            for row in event:    
                print "%2s %-10s %s" % row


def print_table():
    cur.execute("SELECT * FROM Events")
    event = cur.fetchall()
    for e in event:
       print e

if __name__ == "__main__":
    makeTable()
    # handle_command("new event 1 1/1/17 theEvent")
    # handle_command("new event 2 2/2/17 coolEvent")
    # handle_command("new event 3 2/2/17 lameEvent")
    # handle_command("delete 1")
    # handle_command("list events")
    # print_table()