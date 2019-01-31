class NotifierBase:
    """
    Abstract class for notifiers
    """

    def __init__(self):
        """
        Initialize mandatory variables of notifier
        """
        self.cache_message_id = None
        self.flags_batch = []
        self.flags_epoch = []
        self._status = None

    def status(self):
        """
        Status message update
        """
        if self._status is None:
            text = 'Status undefined. Probably, first epoch is still performing'
        else:
            text = self._status

        self.message(text)

    def message(self, message, message_id=None):
        """
        Abstract method of message sending
        Method must be redefined with the return variable ack (can be None, used to edit message of batches)
        """
        pass
    
    def _close_connect(self):
        pass
