# NotifyKer

*Callback notifier and manager bot for Keras ML library*

### Bot for Keras training process monitoring and control

*![ezgif.com-gif-maker](/home/user/Downloads/ezgif.com-gif-maker.gif)*

#### You can:

- Check status of the last epoch
- Get update of metrics per epoch/batch
- Temporarily suspend training (to take the load off the processor, for example)
- Interrupt training
- Set verbose level: 
  - 0 - only finishing message and manual status
  - 1 - just epoch process without metrics
  - 2 - update each batch (like console Keras messages)

##### Simple to use:

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