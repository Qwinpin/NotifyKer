# NotifyKer

*Callback notifier and manager bot for Keras ML library*

##### Simple to use:

![bot](bot.gif)

```python
from notifyker import NotifierTelegramMenu, CallbackSimple


nfk = NotifierTelegramMenu()
callback = CallbackSimple(notifier=nfk)

model.fit(...
	callbacks=[callback])
```

**OR**

Set TOKEN and PROXY while creating the instance of NotifierTelegramMenu

```python
from notifyker import NotifierTelegramMenu, CallbackSimple

TOKEN = 'xxxx:yyy'
PROXY = '...'

nfk = NotifierTelegramMenu(TOKEN=TOKEN, PROXY=PROXY)
callback = CallbackSimple(notifier=nfk)

model.fit(...
	callbacks=[callback])
```

Set PROXY = None if not required

**THEN**

Enter */start* command to your telegram bot