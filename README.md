# NotifyKer

*Callback notifier and manager bot for Keras ML library*

##### Simple to use:

Set your TOKEN and PROXY settings in **notifyker/config_default.py** and rename to **notifyker/config.py**

```python
from notifyker import NotifierTelegram, CallbackSimple


nfk = NotifierTelegram()
callback = CallbackSimple(notifier=nfk)

model.fit(...
	callbacks=[callback])
```