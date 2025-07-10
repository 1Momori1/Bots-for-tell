# 📱 Руководство по запуску в Termux

## 🚀 Быстрый старт

### 1. Подготовка
```bash
# Обновить систему
pkg update && pkg upgrade

# Установить Python
pkg install python python-pip

# Установить зависимости
pip install python-telegram-bot psutil
```

### 2. Запуск системы
```bash
# Перейти в папку проекта
cd /storage/emulated/0/Bots

# Сделать скрипты исполняемыми
chmod +x termux_start.sh termux_stop.sh

# Запустить всех ботов
./termux_start.sh
```

### 3. Проверка работы
```bash
# Проверить процессы
ps aux | grep "main.py"

# Посмотреть логи
tail -f Telescan_bot/telescan.log
tail -f Mather_bots/manager.log
tail -f BotMonitor/bot_monitor.log
```

## 🛑 Остановка

```bash
# Остановить всех ботов
./termux_stop.sh

# Или вручную
pkill -f "main.py"
```

## 📊 Мониторинг

### Bot Monitor
- Отправьте `/start` боту-монитору в Telegram
- Получите статус всех ботов в реальном времени
- Используйте кнопки для управления

### Логи в реальном времени
```bash
# Следить за логами всех ботов
tail -f */telescan.log */mineserv.log */manager.log BotMonitor/bot_monitor.log

# Или по отдельности
tail -f Telescan_bot/telescan.log
tail -f Mather_bots/manager.log
tail -f MineServ_bot/mineserv.log
tail -f BotMonitor/bot_monitor.log
```

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

### Проблемы с правами
```bash
# Дать права на выполнение
chmod +x *.sh
chmod +x */main.py

# Проверить права
ls -la *.sh
ls -la */main.py
```

## 🔄 Автозапуск

### Настройка автозапуска
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

### Отключить автозапуск
```bash
rm ~/.termux/boot/start_bots.sh
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

## ✅ Готово!

Теперь ваша система ботов готова к работе в Termux! 🎉 