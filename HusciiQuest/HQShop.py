"""
   ||                             ||
  {<>}                 _/o>      {<>}
   ||                ,//^/        ||
,_,^^,_________________,",_______,^^,_,
}_\::/__ ______    ______        \::/_}
{    / // / __ \  / __/ /  ___  ___  _{ 
}_  / _  / /_/ / _\ \/ _ \/ _ \/ _ \ <
{  /_//_/\___\_\/___/_//_/\___/ .__/  {
}_____                       /_/   ___}
{__/::\_____,-,________,-^=______/::\_{

"""

class HQShop():
    
    @staticmethod
    def shop(command, channel, shop):
        response = ''

        if command.startswith('list'):
            response = shop.list()

        if command.startswith('buy'):
            command = command.split('buy')[1].strip()
            response = shop.buy(command)
        
        if command.startswith('sell'):
            command = command.split('sell')[1].strip()
            response = shop.sell(command)

        return response