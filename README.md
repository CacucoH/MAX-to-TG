## MAX to TG bot
Очень сырой (но работающий) бот, который позволяет ретранслировать входящие сообщения из MAX в Telegram
### ![max-to-tg logo](https://i.imgur.com/XQZPxrs.jpeg)

### Установка
1. Создайте бота телеграм через @BotFather и получите токен бота
2. Поменяйте содержимое файла `env.example`
```
tg_bot_token=<TOKEN> # Токен тг бота
max_api_token=<TOKEN> # Можно толучить, зайдя в веб версию MAX. Откройте режим разработчика и найдите токен в localStorage
tg_session_name=<NAME> # Любое слово на англ
tg_userid_chat=<NUMERIC-ID> # Айди ВАШЕГО телеграм акка. Можно узнать написав в @userinfo3bot
```

3. Поменяйте название `env.example -> .env`

4. Запустите через докер:
```
docker comose build
docker compose up -d
```

# Важно
Если сообщения перестают пересылаться, следует перезапустить контейнер
Я настроил перезапуск каждые 2 часа через `cron`, полет нормальный

# Note
Большое спасибо [Sharkow1743](https://github.com/Sharkow1743) за разработку [MAX Userbot API](https://github.com/Sharkow1743/MaxAPI)
