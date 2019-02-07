import time

from chainer.training import extension
from chainer.training import trigger as trigger_module


class ExtensionNotifierReport(extension.Extension):
    """
    Trainer extension to send the results and to control
    the training procces using telegram bot

    Each interval depending on verbose level this extension collect the observation
    of the trainer and send using telegram API.

    There are two triggers to handle: (1, 'iteration') is used to collect status
    information for batches and (1, 'epoch') is used to set the status message

    Args:
        notifier: object of notifier that manage the training and messaging
        custom_metrics: list of functions, which calculate user-specific metrics
    """
    def __init__(self, notifier, custom_metrics=None):
        # TODO: additional metrics calculation inside training loop
        if custom_metrics is not None:
            self.custom_metrics = custom_metrics

        if notifier is not None:
            self.notifier = notifier
        else:
            raise ValueError('Notifier is None')

        # notifier specific attributes
        self.details = None  # dict of availble details: epochs, batch_size, lr, etc
        self.starting_time = None
        self.current_epoch = 1

        # chainer specific attributes
        self._trigger_epoch = trigger_module.get_trigger((1, 'epoch'))
        self._trigger_iteration = trigger_module.get_trigger((1, 'iteration'))

    def __call__(self, trainer):
        # activate the notifier, connect the bot
        if not self.notifier.active:
            self.notifier._connect()

        # add starting information, add details
        if self.details is None:
            self.start_message(trainer)

        if self._trigger_iteration(trainer):
            # check notifier flags to react on commands
            if self.notifier.flags_batch or self.notifier.flags_epoch:
                self.flags_handler(trainer)

            # check the silence mode
            if self.notifier.verbose_value == 0:
                return

            # send current status and store this message as a acknowledgment
            if self.notifier.verbose_value != 0:
                ack = self.status_message(trainer)

        if self._trigger_epoch(trainer):
            # clear cache id to send next epoch status as a new message
            self.notifier.cache_message_id = None
            # set notifier status for /status command
            self.notifier._status = ack
            self.current_epoch += 1

            # close connection at the end of training
            if self.current_epoch > trainer.stop_trigger.period:
                if self.details['epochs'] != trainer.stop_trigger.period:
                    tag = 'forcibly'
                else:
                    tag = 'successfully'

                self.end_time = time.ctime(int(time.time()))

                self.notifier.message('Training completed {} in {}'.format(tag, self.end_time))

                self.notifier._close_connect()

    def status_message(self, trainer):
        """
        Prepare the status message and send to the user
        """
        status = trainer.observation
        # get the current batch (for current epoch)
        batch = trainer.updater.iteration % (self.details['samples'] // self.details['batch_size'])

        # send the updates only 10 times per epoch iteration_update_freq is used for that
        if batch % self.iteration_update_freq == 0:
            message = []

            message.append('Epoch {} / {}'.format(self.current_epoch, self.details['epochs']))

            if self.notifier.verbose_value == 2:
                # create progress bar, like: [+++==========]
                pad_bar = '[{}{}]'.format('++' * (batch // self.iteration_update_freq), '==' * (10 - batch // self.iteration_update_freq))
                message.append('{} / {} {}'.format(batch * self.details['batch_size'], self.details['samples'], pad_bar))

            # add loss and acc (or other metrics) and validation loss and acc (at the end of the epoch)
            for i in status:
                message.append('{:15s}: {:15s}'.format(i, str(status[i])))

            # check the silence mode
            if self.notifier.verbose_value != 0:
                # ack here is a message id of the sent message, to edit the epoch message
                ack = self.notifier.message(' \n'.join(message), self.notifier.cache_message_id)
                self.notifier.cache_message_id = ack.message_id if ack is not None else None

            return ' \n'.join(message)

    def start_message(self, trainer):
        """
        Send first message about starting parameters and collect initial parameters
        """
        # initialize the flags of notifier
        self.notifier.flags_batch = []
        self.notifier.flags_epoch = []

        self.details = {}
        # calculate the batch status updates frequency - only 10 edits per epoch (avoid spam)
        self.iteration_update_freq = max(trainer.updater._iterators['main']._epoch_size //
                                         trainer.updater._iterators['main'].batch_size // 10, 1)
        self.details['epochs'] = trainer.stop_trigger.get_training_length()[0]
        self.details['optimizer'] = trainer.updater.get_all_optimizers()['main'].__repr__().split(' ')[0][1:]
        self.details['lr'] = trainer.updater.get_all_optimizers()['main'].lr
        self.details['samples'] = trainer.updater._iterators['main']._epoch_size
        self.details['batch_size'] = trainer.updater._iterators['main'].batch_size

        message = []
        message.append('\nTraining started in {}\n'.format(self.starting_time))

        message.append('With the following parameters:')
        for i in self.details:
            if isinstance(self.details[i], list):
                value = ', '.join(self.details[i])
            else:
                value = str(self.details[i])

            message.append('{0:25s}: {1:25s}'.format(i, value))

        self.notifier.message(' \n'.join(message))

    def flags_handler(self, trainer):
        """
        Handle notifiers flags in order to control the training loop
        """
        # process pause command
        if 'p' in self.notifier.flags_batch:
            self.notifier.flags_batch.remove('p')
            self.notifier.cache_message_id = None

            self.notifier.message('Training suspended. Use /interrupt or /continue now')
            # wait for interrupt or continue command
            while 'c' not in self.notifier.flags_batch and 's' not in self.notifier.flags_batch:
                time.sleep(10)

        # process interrupt command
        if 's' in self.notifier.flags_batch:
            self.notifier.flags_batch.remove('s')
            # some hacking to break the training loop, have no idea how to handle with this better
            trainer.stop_trigger.period = (trainer.updater.epoch - 1) or 1

        # process continue command
        if 'c' in self.notifier.flags_batch:
            self.notifier.flags_batch.remove('c')
            self.notifier.message('Training continues')
