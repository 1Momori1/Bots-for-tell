# 🤖 Система управления ботами для Termux

Полнофункциональная система для управления множественными Telegram ботами через Termux на телефоне.

## 📋 Описание

Система включает 4 специализированных бота:
- **Telescan Bot** - мониторинг системы (CPU, RAM, диск, температура, сеть)
- **MineServ Bot** - управление сервером Minecraft
- **Manager Bot** - централизованное управление всеми ботами
- **Bot Monitor** - независимый монитор статуса всех ботов

## 🚀 Быстрый старт

### 1. Установка в Termux
```bash
# Обновить систему
pkg update && pkg upgrade

# Установить Python
pkg install python python-pip

# Клонировать репозиторий
git clone https://github.com/your-username/bots-system.git
cd bots-system

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка конфигурации
```bash
# Скопировать примеры конфигурации
cp config_examples/*_config.json ./

# Настроить токены и ID в каждом config.json
# Заменить YOUR_BOT_TOKEN на реальные токены
# Заменить 123456789 на ваш Telegram ID
```

### 3. Запуск системы
```bash
# Сделать скрипты исполняемыми
chmod +x termux_start.sh termux_stop.sh

# Запустить всех ботов
./termux_start.sh

# Остановить всех ботов
./termux_stop.sh
```

## 📁 Структура проекта

```
Bots/
├── BotMonitor/           # Независимый бот-монитор
│   ├── main.py
│   ├── config.json
│   ├── start_monitor.py
│   ├── stop_monitor.py
│   └── README.md
├── Mather_bots/          # Менеджер ботов
│   ├── main.py
│   ├── config.json
│   └── requirements.txt
├── Telescan_bot/         # Мониторинг системы
│   ├── main.py
│   ├── config.json
│   └── requirements.txt
├── MineServ_bot/         # Управление сервером
│   ├── main.py
│   ├── config.json
│   └── requirements.txt
├── config_examples/      # Примеры конфигурации
├── termux_start.sh       # Скрипт запуска для Termux
├── termux_stop.sh        # Скрипт остановки для Termux
├── start_bots.py         # Запуск основных ботов
├── stop_bots.py          # Остановка основных ботов
├── clean_start.py        # Чистый запуск с очисткой
├── run_tests.py          # Запуск тестов
├── requirements.txt      # Основные зависимости
└── README.md
```

## 🤖 Функции ботов

### 📊 Bot Monitor (Независимый монитор)
- **Реальное время:** Отображение статуса всех ботов
- **Автообновление:** Автоматическое обновление каждые 30 сек
- **Системная информация:** CPU, RAM, диск
- **Независимость:** Работает отдельно от других ботов
- **Простота:** Максимально простой интерфейс

### 🤖 Manager Bot (Менеджер)
- **Управление ботами:** Запуск/остановка/перезапуск всех ботов
- **Мониторинг состояния:** Отслеживание работы ботов
- **Inline кнопки:** Удобное управление через Telegram
- **Автоперезапуск:** Автоматический перезапуск упавших ботов
- **Системная информация:** Просмотр состояния системы

### 📱 Telescan Bot (Мониторинг системы)
- **CPU мониторинг:** Отслеживание загрузки процессора
- **Память:** Мониторинг использования RAM
- **Температура:** Контроль температуры устройства
- **Диск:** Отслеживание свободного места
- **Сеть:** Статистика сетевого трафика
- **Уведомления:** Оповещения при превышении порогов

### ⛏️ MineServ Bot (Управление сервером)
- **Запуск/остановка сервера:** Управление процессом сервера
- **Мониторинг системы:** CPU, RAM, диск
- **Настройки сервера:** Конфигурация параметров
- **Автоперезапуск:** Автоматический перезапуск при сбоях

## 🚀 Запуск в Termux

### Быстрый запуск
```bash
# Сделать скрипты исполняемыми
chmod +x termux_start.sh termux_stop.sh

# Запуск всех ботов
./termux_start.sh

# Остановка всех ботов
./termux_stop.sh
```

### Ручной запуск
```bash
# Остановить старые процессы
pkill -f "main.py"

# Запустить ботов по отдельности
cd Telescan_bot && nohup python main.py > telescan.log 2>&1 &
cd ../MineServ_bot && nohup python main.py > mineserv.log 2>&1 &
cd ../Mather_bots && nohup python main.py > manager.log 2>&1 &
cd ../BotMonitor && nohup python main.py > bot_monitor.log 2>&1 &
```

### Автозапуск в Termux
```bash
# Создать папку для автозапуска
mkdir -p ~/.termux/boot

# Создать скрипт автозапуска
cat > ~/.termux/boot/start_bots.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /storage/emulated/0/Bots
./termux_start.sh
EOF

# Сделать исполняемым
chmod +x ~/.termux/boot/start_bots.sh
```

### Проверка статуса в Termux
```bash
# Проверить процессы
ps aux | grep "main.py"

# Посмотреть логи
tail -f Telescan_bot/telescan.log
tail -f Mather_bots/manager.log
tail -f BotMonitor/bot_monitor.log
```

## 📱 Использование в Telegram

### Manager Bot
- `/start` - главное меню управления
- Кнопки для запуска/остановки/перезапуска ботов

### Telescan Bot
- `/start` - мониторинг системы
- Уведомления о превышении порогов

### MineServ Bot
- `/start` - управление сервером Minecraft

### Bot Monitor
- `/start` - статус всех ботов
- Автообновление каждые 30 секунд

## 🔧 Устранение проблем

### Боты не запускаются
```bash
# Проверить Python
python --version

# Проверить зависимости
pip list | grep telegram

# Очистить старые процессы
pkill -f "main.py"
sleep 2
./termux_start.sh
```

### Боты падают
```bash
# Проверить логи
cat */telescan.log */mineserv.log */manager.log BotMonitor/bot_monitor.log

# Перезапустить с очисткой
./termux_stop.sh
sleep 3
./termux_start.sh
```

## 🧪 Тестирование

### Запуск всех тестов
```bash
python run_tests.py
```

### Запуск тестов конкретного бота
```bash
cd Telescan_bot
python -m unittest discover tests -v
```

## 📝 Команды

### Manager Bot
- `/start` - Главное меню управления

### Telescan Bot
- `/start` - Главное меню мониторинга

### MineServ Bot
- `/start` - Главное меню управления сервером

### Bot Monitor
- `/start` - Показать статус всех ботов

## 🔄 Добавление новых ботов

1. Создайте новую папку в корне проекта
2. Добавьте `main.py`, `config.json` и `requirements.txt`
3. Добавьте бота в конфигурацию менеджера (`Mather_bots/config.json`)
4. Добавьте бота в конфигурацию монитора (`BotMonitor/config.json`)
5. Перезапустите менеджер

## 🎯 Особенности Termux

### Преимущества
- ✅ Стабильная работа asyncio
- ✅ Меньше конфликтов процессов
- ✅ Лучшая производительность
- ✅ Автозапуск при перезагрузке

### Ограничения
- ⚠️ Ограниченные ресурсы
- ⚠️ Может быть убит системой при нехватке памяти
- ⚠️ Нужно держать Termux открытым

### Рекомендации
- 🔋 Используйте автозапуск
- 📊 Регулярно проверяйте логи
- 🛡️ Настройте уведомления о сбоях
- 💾 Следите за свободным местом

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
1. Проверьте раздел "Устранение проблем"
2. Посмотрите логи ботов
3. Создайте Issue в репозитории

---

**⭐ Не забудьте поставить звезду репозиторию!** 