import time

from .callback_base import CallbackBase


class CallbackSimple(CallbackBase):
    def __init__(self, verbose=0, notifier=None, custom_metrics=None):
        super().__init__()

        if notifier is not None:
            self.notifier = notifier
        else:
            raise ValueError

        if custom_metrics is not None:
            self.custom_metrics = custom_metrics

        self.details = {}
        self.starting_time = None
        self.batch_update_freq = None
        self.current_epoch = 1

    def on_train_begin(self, logs=None):
        self.notifier._connect()
        self.notifier.flags_batch = []
        self.notifier.flags_epoch = []

        for i in self.params:
            self.details[i] = self.params[i]

        self.starting_time = time.time()
        self.batch_update_freq = max(self.details['samples'] // self.details['batch_size'] // 10, 1)

        message = []
        message.append('\nTraining started in {}\n'.format(self.starting_time))
            
        if self.notifier.verbose_value == 0:
            self.notifier.message(' \n'.join(message))

            return

        if self.notifier.verbose_value == 2:
            message.append('With the following parameters:')
            for i in self.details:
                if isinstance(self.details[i], list):
                    value = ', '.join(self.details[i])
                else:
                    value = str(self.details[i])

                message.append('{0:25s}: {1:25s}'.format(i, value))

        self.notifier.message(' \n'.join(message))

    def on_train_end(self, logs=None):
        if 's' in self.notifier.flags_batch:
            tag = 'forcibly'
        else:
            tag = 'Successfully'
        self.notifier.message('Training completed {}'.format(tag))
        self.notifier._close_connect()

    def on_batch_end(self, batch, logs=None):
        if self.notifier.flags_batch:
            self.flags_handler()

        if self.notifier.verbose_value == 0:
            return

        if batch % self.batch_update_freq == 0:
            message = []

            message.append('Epoch {} / {}'.format(self.current_epoch, self.details['epochs']))

            pad_bar = '[{}{}]'.format('++' * (batch // self.batch_update_freq), '==' * (10 - batch // self.batch_update_freq))
            message.append('{} / {} {}'.format(2 * logs['batch'], self.details['samples'], pad_bar))

            if self.notifier.verbose_value == 2:
                for i in self.details['metrics']:
                    if 'val_' not in i:
                        message.append('{:15s}: {:15s}'.format(i, str(logs[i])))

            ack = self.notifier.message(' \n'.join(message), self.notifier.cache_message_id)
            self.notifier.cache_message_id = ack.message_id

    def on_epoch_begin(self, epoch, logs=None):
        if self.notifier.flags_epoch:
            self.flags_handler()

        self.notifier.cache_message_id = None

    def on_epoch_end(self, epoch, logs=None):
        if self.notifier.flags_epoch:
            self.flags_handler()

        message = []

        message.append('Epoch {} / {}'.format(self.current_epoch, self.details['epochs']))

        pad_bar = '[{}]'.format('++' * 10)
        message.append('{} / {} {}'.format(self.details['samples'], self.details['samples'], pad_bar))
        for i in logs:
            message.append('{:15s}: {:15s}'.format(i, str(logs[i])))

        self.notifier._status = ' \n'.join(message)

        if self.notifier.verbose_value != 0:
            ack = self.notifier.message(' \n'.join(message), self.notifier.cache_message_id)
            self.notifier.cache_message_id = ack.message_id

        self.current_epoch += 1

    def flags_handler(self):
        if 'p' in self.notifier.flags_batch:
            self.notifier.flags_batch.remove('p')

            while 'c' not in self.notifier.flags_batch and 's' not in self.notifier.flags_batch:
                time.sleep(10)

        if 's' in self.notifier.flags_batch:
            self.model.stop_training = True

        if 'c' in self.notifier.flags_batch:
            self.notifier.flags_batch.remove('c')
