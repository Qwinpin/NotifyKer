from telegram.ext import CommandHandler, ConversationHandler, RegexHandler, Updater
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from ..config import PROXY_DEF, TOKEN_DEF
from .notifier_telegram import NotifierTelegram


class NotifierTelegramMenu(NotifierTelegram):
    """
    Telegram notifier bot
    """
    def __init__(self, TOKEN=None, PROXY=None, chat_id=None):
        """
        Create handlers and chat id for message edits
        """
        super().__init__()
        menu_keyboard = [
            [InlineKeyboardButton("Status", callback_data='status')],
            [InlineKeyboardButton("Verbose", callback_data='verbose')],
            [InlineKeyboardButton("Pause", callback_data='pause')],
            [InlineKeyboardButton("Continue", callback_data='Continue')],
            [InlineKeyboardButton("Interrupt", callback_data='interrupt')]]

        self.default_reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)

    def handlers(self):
        """
        Method of activation of telegram bot handlers
        """
        super().handlers()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('menu', self.menu)],
            states={
                0: [RegexHandler('^(Status|Verbose|Pause|Continue|Interrupt)$', self.menu_handler)],
                1: [RegexHandler('^(Unchanged|0|1|2)$', self.verbose_handler)],
                2: [RegexHandler('^(Yes|No)$', self.interrupt_handler)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)])

        self.updater.dispatcher.add_handler(conv_handler)

    def start(self, bot, update):
        """
        Method of start message processing required to obtain chat_id
        """
        if self.chat_id is None:
            self.chat_id = update.message.chat_id

        update.message.reply_text('Hello, my friend. /menu')

    def _help(self, bot, update):
        """
        Method of help command processing
        """
        if self.chat_id is None:
            self.chat_id = update.message.chat_id

        message = 'Welcome! \n\
/help - Show available commands\n\
/menu - Activate keyboard menu with following options:\n\
Status - Show current training status - epoch, metrics\n\
Pause - Suspend training process (model still in a memory)\n\
Continue - Continue training process\n\
Interrupt - Interrupt training process ATTENTION: You will not be able to continue by this bot\n'
        self.message(message)

    def cancel(self, bot, update):
        self.message('Cancel', reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    def menu(self, bot, update):
        """
        Method of menu command processing. Return the keyboard-menu
        """
        self.message('Menu activated', reply_markup=self.default_reply_markup)

        return 0

    def menu_handler(self, bot, update):
        """
        Process menu choice
        """
        option = update.message.text

        if option == 'Status':
            self.status()

        elif option == 'Verbose':
            return self.verbose_menu(bot, update)

        elif option == 'Pause':
            return self.pause(bot, update)

        elif option == 'Continue':
            return self.cont(bot, update)

        elif option == 'Interrupt':
            return self.interrupt_menu(bot, update)

        elif option == 'Cancel':
            return ConversationHandler.END

    def verbose_menu(self, bot, update):
        verbose_list = [i for i in range(3) if i != self.verbose_value]
        verbose_keyboard = [
            [InlineKeyboardButton("Unchanged", callback_data='none')]
        ]

        for item in verbose_list:
            verbose_keyboard.append(
                [InlineKeyboardButton("{}".format(item), callback_data='verbose_{}'.format(item))])

        reply_markup = ReplyKeyboardMarkup(verbose_keyboard)
        self.message('Current verbose: {}. Set to: '.format(self.verbose_value), reply_markup=reply_markup)

        return 1

    def verbose_handler(self, bot, update):
        option = update.message.text
        if option != 'Unchanged':
            self.verbose_value = int(option)

        self.message('Verbose: {}'.format(self.verbose_value), reply_markup=self.default_reply_markup)
        self.cache_message_id = None
        return 0

    def interrupt_menu(self, bot, update):
        """
        Method of stop (training) command processing
        """
        menu_keyboard = [
            [InlineKeyboardButton("No", callback_data='y')],
            [InlineKeyboardButton("Yes", callback_data='n')]]

        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)

        self.message('Are you sure you want to interrupt?', reply_markup=reply_markup)

        return 2

    def interrupt_handler(self, bot, update):
        option = update.message.text
        if option == 'Yes':
            self.flags_batch.append('s')
            self.message('Training interrupting...', reply_markup=ReplyKeyboardRemove())
        else:
            self.flags_batch.append('c')
            self.message('Training continue', reply_markup=self.default_reply_markup)

        return 0

    def _close_connect(self):
        # self.updater.stop()
        self.active = False
