#!/usr/bin/env python
# -*- coding: utf-8 -*-

token = "188880249:AAHZusX3-mEcON6PJAptK2oJChDqIkpAI1o"

import telegram
from telegram.ext import Updater, StringCommandHandler, StringRegexHandler, \
    MessageHandler, CommandHandler, RegexHandler, Filters
from telegram.ext.dispatcher import run_async

import logging

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


def log_message(message):
    logger.info("Recieved message; From: %s; chat_id: %d; Text: %s" %
                (message.from_user,
                 message.chat_id,
                 message.text))

class UsersManager():
    def __init__(self):
        self.users = {}


    def add_users(self, user_data):
        logger.info("Adding user: {0}".format(user_data))
        self.users[user_data['id']] = user_data



class TestBot():
    def __init__(self, token, workers=10):
        self.is_active = True

        self.updater = Updater(token, workers=10)
        self.dp = self.updater.dispatcher

        self.users = UsersManager()

        self.set_up_handlers()
        self.counter = 0


    def start(self):
        self.update_queue = self.updater.start_polling(timeout=10)


    def set_up_handlers(self):
        self.dp.addHandler(CommandHandler("register", self.register))
        self.dp.addHandler(CommandHandler("help", self.help))
        self.dp.addHandler(CommandHandler("stop", self.stop))
        self.dp.addHandler(CommandHandler("users_list", self.users_list))
        self.dp.addHandler(CommandHandler("add", self.add))
        self.dp.addErrorHandler(self.error)


    def close(self):
        logger.info("Closing")
        self.updater.stop()


    def stop(self, bot, update):
        logger.info("Stopping")
        bot.sendMessage(update.message.chat_id, text="Ok, zatrzymuje bota.")
        self.is_active = False


    def add(self, bot, update):
        log_message(update.message)
        splited = update.message.text.split(' ')
        try:
            self.counter += int(splited[1])
            logger.info("Counter " + str(self.counter))
            bot.sendMessage(update.message.chat_id, text="Obecna wartosc licznika: " + str(self.counter))
        except:
            bot.sendMessage(update.message.chat_id, text="Podaj liczbe jako argument komendy /add.")


    def users_list(self, bot, update):
        message_text = "Users list:"
        bot.sendMessage(update.message.chat_id, text=message_text.encode('utf-8'))

        for user in self.users.users.values():
            message_text = str(user['id']) + " - " + user['first_name'] + " "+ user['last_name']
            bot.sendMessage(update.message.chat_id, text=message_text.encode('utf-8'))


    def update(self):
        if self.counter > 10:
            self.counter = 0
            for user_id in self.users.users:
                self.updater.bot.sendMessage(chat_id=user_id, text="Przekroczylismy 10 w liczniku! Resetuje!")


    def register(self, bot, update):
        self.users.add_users(update.message.from_user)
        bot.sendMessage(update.message.chat_id, text='Uzytkownik zarejestrowany.')


    def help(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Help!')


    def error(self, bot, update, error):
        logger.warn('Update %s caused error %s' % (update, error))



stop_bot = False
def stop(bot, update):
    global stop_bot
    stop_bot = True


def main():
    test_bot = TestBot(token)
    test_bot.start()

    while True:
        test_bot.update()
        if not test_bot.is_active:
            logger.info("Stopping main loop")
            test_bot.close()
            break


if __name__ == '__main__':
    main()
