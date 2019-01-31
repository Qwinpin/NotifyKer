from telegram.ext import CommandHandler, ConversationHandler, RegexHandler, Updater
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from ..config import TOKEN, PROXY
from .notifier_base import NotifierBase


class NotifierTelegram(NotifierBase):
    """
    Telegram notifier bot
    """
    def __init__(self):
        """
        Create handlers and chat id for message edits
        """
        super().__init__()
        self.active = False
        self.cache_message_id = None
        self.flags_batch = []
        self.flags_epoch = []
        self._status = None
        self.verbose_value = 1
        self._connect()

    def _connect(self):
        if not self.active:
            self.updater = Updater(TOKEN, request_kwargs=PROXY)
    
            self.handlers()
            self.updater.start_polling()

            self.active = True

    def message(self, message, message_id=None, reply_markup=None):
        """
        Telegram specific method of message sending
        """
        if message_id is not None:
            ack = self.updater.bot.edit_message_text(chat_id=self.chat_id, text=message, message_id=message_id)
        else:
            ack = self.updater.bot.send_message(chat_id=self.chat_id, text=message, reply_markup=reply_markup)

        return ack

    def handlers(self):
        """
        Method of activation of telegram bot handlers
        """
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('interrupt', self.interrupt_handler))
        self.updater.dispatcher.add_handler(CommandHandler('help', self._help))
        self.updater.dispatcher.add_handler(CommandHandler('status', self.status))
        self.updater.dispatcher.add_handler(CommandHandler('pause', self.pause))
        self.updater.dispatcher.add_handler(CommandHandler('continue', self.cont))

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
        self.chat_id = update.message.chat_id
        update.message.reply_text('Hello, my friend. /menu')

    def _help(self, bot, update):
        """
        Method of help command processing
        """
        self.chat_id = update.message.chat_id
        message = 'Welcome! \n\
/help - Show available commands\n\
/menu - Activate keyboard menu with following options:\n\
Status - Show current training status - epoch, metrics\n\
Pause - Suspend training process (model still in a memory)\n\
Continue - Continue training process\n\
Interrupt - Interrupt training process ATTENTION: You will not be able to continue by this bot\n'
        self.message(message)

    def pause(self, bot, update):
        """
        Method of pause command processing. Suspend the training process
        """
        self.flags_batch.append('p')
        self.message('Training suspended. Use Interrupt or Continue now')

    def cont(self, bot, update):
        """
        Method of continue command processing. Continue the training process
        """
        self.flags_batch.append('c')
        self.message('Training continues')

    def cancel(self, bot, update):
        self.message('Cancel', reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    def menu(self, bot, update):
        """
        Method of menu command processing. Return the keyboard-menu
        """
        menu_keyboard = [
            [InlineKeyboardButton("Status", callback_data='status')],
            [InlineKeyboardButton("Verbose", callback_data='verbose')],
            [InlineKeyboardButton("Pause", callback_data='pause')],
            [InlineKeyboardButton("Continue", callback_data='Continue')],
            [InlineKeyboardButton("Interrupt", callback_data='interrupt')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]]

        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)

        self.message('Menu activated', reply_markup=reply_markup)

        return 0

    def menu_handler(self, bot, update):
        """
        """
        option = update.message.text

        if option == 'Status':
            self.status()

        elif option == 'Verbose':
            return self.verbose(bot, update)

        elif option == 'Pause':
            return self.pause(bot, update)

        elif option == 'Continue':
            return self.cont(bot, update)

        elif option == 'Interrupt':
            return self.interrupt(bot, update)

        elif option == 'Cancel':
            return ConversationHandler.END

    def verbose(self, bot, update):
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

        menu_keyboard = [
            [InlineKeyboardButton("Status", callback_data='status')],
            [InlineKeyboardButton("Verbose", callback_data='verbose')],
            [InlineKeyboardButton("Pause", callback_data='pause')],
            [InlineKeyboardButton("Continue", callback_data='Continue')],
            [InlineKeyboardButton("Interrupt", callback_data='interrupt')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]]

        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)

        self.message('Verbose: {}'.format(self.verbose_value), reply_markup=reply_markup)

        return 0

    def interrupt(self, bot, update):
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
        menu_keyboard = [
            [InlineKeyboardButton("Status", callback_data='status')],
            [InlineKeyboardButton("Verbose", callback_data='verbose')],
            [InlineKeyboardButton("Pause", callback_data='pause')],
            [InlineKeyboardButton("Continue", callback_data='Continue')],
            [InlineKeyboardButton("Interrupt", callback_data='interrupt')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]]

        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)

        option = update.message.text
        if option == 'Yes':
            self.flags_batch.append('s')
            self.message('Training interrupting...', reply_markup=ReplyKeyboardRemove())
        else:
            self.flags_batch.append('c')
            self.message('Training continue', reply_markup=reply_markup)
 
        return 0

    def _close_connect(self):
        # self.updater.stop()
        self.active = False
