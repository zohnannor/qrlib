# Vk Bot Library

### Example Longpoll bot:
```python
from qrlib import Bot

token = "12345asdfgh"
bot = Bot(token=token, group_id=123456789, prefix='/')


@bot.message_handler(text = 'hello!')
async def hello():
    return 'Hello!'


@bot.message_handler(text = 'greet <name>')
async def greet(name: str):
    return f'Hello, {name}!'


@bot.message_handler(text = '<command>')
async def unknown_command(command: str):
    return f'Unknown command `{command}`'


bot.run()
```

### Example Callback bot:
_TODO_
