# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import config_file
from stragy.grid_trading1 import GridTradingBot

GRIDING_TYPE1 = "griding_trading1"


def createBot(bot_type,is_simulate):
    conf = config_file.getConfigFile("config.json")
    authInfo = {}
    if bot_type ==GRIDING_TYPE1:
        if is_simulate == True:
            authInfo = conf['account']['okex']['simulate'][0]
        else:
            authInfo = conf['account']['okex']['real'][0]
    grid_bot = GridTradingBot("okex", authInfo, is_simulate)
    return grid_bot


def run(bot,setting):
    bot.run(setting)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot = createBot(GRIDING_TYPE1,True)
    bot.run(bot.settings[0])


