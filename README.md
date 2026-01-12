## MAX to TG bot
Очень сырой (но работающий) бот, который позволяет ретранслировать входящие сообщения из MAX в Telegram

### Установка
1. Поменяйте содержимое файла `env.example`
```
tg_bot_token=<TOKEN> # Токен тг бота
max_api_token=<TOKEN> # Можно толучить через веб версию макса в localStorage
tg_session_name=<NAME> # Любое имя на англ
tg_userid_chat=<NUMERIC-ID> # Айди телеграма можно узнать в @userinfo3bot
```

2. Поменяйте название `env.example -> .env`

3. Запустите через докер `docker compose up -d`

# Note
Большое спасибо [Sharkow1743](https://github.com/Sharkow1743) за разработку [MAX Userbot API](https://github.com/Sharkow1743/MaxAPI)