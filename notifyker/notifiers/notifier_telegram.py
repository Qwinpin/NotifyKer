from telegram.ext import CommandHandler, Updater

from .notifier_base import NotifierBase


class NotifierTelegram(NotifierBase):
    """
    Telegram notifier bot
    """
    def __init__(self, TOKEN=None, PROXY=None, chat_id=None):
        """
        Create handlers and chat id for message edits
        """
        super().__init__()
        self.active = False

        self.chat_id = chat_id
        self.__TOKEN = TOKEN
        self.__PROXY = PROXY

        self._connect()

    def _connect(self):
        if not self.active:
            self.updater = Updater(self.__TOKEN, request_kwargs=self.__PROXY)

            self.handlers()
            self.updater.start_polling()

            self.active = True

    def message(self, message, message_id=None, reply_markup=None):
        """
        Telegram specific method of message sending
        """
        try:
            if message_id is not None:
                ack = self.updater.bot.edit_message_text(chat_id=self.chat_id, text=message, message_id=message_id)
            else:
                ack = self.updater.bot.send_message(chat_id=self.chat_id, text=message, reply_markup=reply_markup)
        except Exception as e:
            print('Chat is not active. {}'.format(e))
            return None

        else:
            return ack

    def handlers(self):
        """
        Method of activation of telegram bot handlers
        """
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('interrupt', self.interrupt))
        self.updater.dispatcher.add_handler(CommandHandler('help', self._help))
        self.updater.dispatcher.add_handler(CommandHandler('status', self.status))
        self.updater.dispatcher.add_handler(CommandHandler('pause', self.pause))
        self.updater.dispatcher.add_handler(CommandHandler('verbose', self.verbose))
        self.updater.dispatcher.add_handler(CommandHandler('continue', self.cont))

    def start(self, bot, update):
        """
        Method of start message processing required to obtain chat_id
        """
        # set chat_id to send messages
        if self.chat_id is None:
            self.chat_id = update.message.chat_id

        update.message.reply_text('Hello, my friend')

    def _help(self, bot, update):
        """
        Method of help command processing
        """
        if self.chat_id is None:
            self.chat_id = update.message.chat_id

        message = 'Welcome! Enter /start to add your chat_id before you start training\n\
/help - Show available commands\n\
/status - Show current training status - epoch, metrics\n\
/pause - Suspend training process (model still in a memory)\n\
/continue - Continue training process\n\
/interrupt - Interrupt training process ATTENTION: You will not be able to continue by this bot\n'
        self.message(message)

    def pause(self, bot, update):
        """
        Method of pause command processing. Suspend the training process
        """
        # add 'p' flag to suspend the training in the end of the current batch
        self.flags_batch.append('p')

    def cont(self, bot, update):
        """
        Method of continue command processing. Continue the training process
        """
        self.flags_batch.append('c')
        self.message('Training continue in less than 10s')

    def verbose(self, bot, update):
        """
        Get current verbose level
        0 - only the last message about the end of training
        1 - status of each epoch end
        2 - update of each batch result
        """
        self.message('Current verbose: {}'.format(self.verbose_value))

    def interrupt(self, bot, update):
        """
        Method of stop (training) command processing
        """
        self.flags_batch.append('s')

        self.message('Training interrupting...')

    def _close_connect(self):
        self.updater.stop()
        self.active = False
