from keras.callbacks import Callback


class CallbackBase(Callback):
    def __init__(self, notifier=None, custom_metrics=None):
        super().__init__()

        if notifier is not None:
            self.notifier = notifier

        if custom_metrics is not None:
            self.custom_metrics = custom_metrics
