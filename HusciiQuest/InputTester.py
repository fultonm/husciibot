"""
Tester file for input
"""

from HusciiQuest import HusciiQuest

hq = HusciiQuest();
user = "U2PM124BG"
channel = "none"

if __name__ == "__main__":
    while(1):
        command = input("~*")
        print("-=System=-")
        response = hq.husciiQuest(command, channel, user);
        print("-=\end=-")
        print(response)
