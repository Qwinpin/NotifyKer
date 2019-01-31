from telegram.ext import CommandHandler, Updater

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
        self.chat_id = None

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
        self.chat_id = update.message.chat_id
        update.message.reply_text('Hello, my friend')

    def _help(self, bot, update):
        """
        Method of help command processing
        """
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
        self.flags_batch.append('p')
        self.message('Training suspended. Use /stop or /cont now')

    def cont(self, bot, update):
        """
        Method of continue command processing. Continue the training process
        """
        self.flags_batch.append('c')
        self.message('Training continues')

    def verbose(self, bot, update):
        self.message('Current verbose: {}'.format(self.verbose_value))

    def interrupt(self, bot, update):
        """
        Method of stop (training) command processing
        """
        self.flags_batch.append('s')
        self.message('')

        self.message('Training interrupting...')

    def _close_connect(self):
        self.updater.stop()
        self.active = False
