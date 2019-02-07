from keras.callbacks import Callback


class CallbackBase(Callback):
    def __init__(self, notifier=None, custom_metrics=None):
        super().__init__()

        if custom_metrics is not None:
            self.custom_metrics = custom_metrics

        self.details = {}
        self.starting_time = None
        self.batch_update_freq = None
        self.current_epoch = 1
