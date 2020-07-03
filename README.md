# Vk Bot Library

### Example Longpoll bot:
```
from qrlib import Bot

token = "12345asdfgh"
bot = Bot(token=token, group_id=123456789)


@bot.message_handler(text = 'hello!')
async def hello():
    return 'Hello!'


@bot.message_handler(text = 'greet <name>')
async def greet(name):
    return f'Hello, {name}!'


bot.run()
```

### Example Callback bot:
_TODO_
