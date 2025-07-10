# Система управления ботами для Termux

Система для управления множественными Telegram ботами через Termux на телефоне.

## Структура проекта

```
Bots/
├── Mather_bots/        # Главный бот-менеджер
│   ├── main.py         # Основной файл менеджера
│   ├── config.json     # Конфигурация менеджера
│   └── requirements.txt # Зависимости
├── Telescan_bot/       # Бот мониторинга телефона
│   ├── main.py         # Основной файл мониторинга
│   ├── config.json     # Конфигурация мониторинга
│   └── requirements.txt # Зависимости
└── README.md           # Этот файл
```

## Установка в Termux

### 1. Подготовка системы
```bash
pkg update && pkg upgrade
pkg install python python-pip
```

### 2. Установка зависимостей для менеджера
```bash
cd Mather_bots
pip install -r requirements.txt
```

### 3. Установка зависимостей для Telescan
```bash
cd ../Telescan_bot
pip install -r requirements.txt
```

### 4. Настройка конфигурации

#### Mather_bots/config.json:
```json
{
  "bot_token": "YOUR_MANAGER_BOT_TOKEN",
  "admin_ids": [YOUR_TELEGRAM_ID],
  "bots": {
    "telescan": {
      "name": "Telescan Bot",
      "path": "../Telescan_bot/main.py",
      "enabled": true,
      "auto_restart": true
    }
  }
}
```

#### Telescan_bot/config.json:
```json
{
  "bot_token": "YOUR_TELESCAN_BOT_TOKEN",
  "admin_ids": [YOUR_TELEGRAM_ID],
  "monitoring": {
    "check_interval": 60,
    "cpu_threshold": 80,
    "memory_threshold": 85,
    "temperature_threshold": 45,
    "disk_threshold": 90
  }
}
```

### 5. Запуск

#### Запуск менеджера:
```bash
cd Mather_bots
python main.py
```

#### Запуск Telescan напрямую:
```bash
cd Telescan_bot
python main.py
```

## Функции ботов

### 🤖 Mather_bots (Менеджер)
- **Управление ботами:** Запуск/остановка/перезапуск всех ботов
- **Мониторинг состояния:** Отслеживание работы ботов
- **Inline кнопки:** Удобное управление через Telegram
- **Автоперезапуск:** Автоматический перезапуск упавших ботов
- **Системная информация:** Просмотр состояния системы

### 📱 Telescan_bot (Мониторинг телефона)
- **CPU мониторинг:** Отслеживание загрузки процессора
- **Память:** Мониторинг использования RAM
- **Температура:** Контроль температуры устройства
- **Диск:** Отслеживание свободного места
- **Сеть:** Статистика сетевого трафика
- **Уведомления:** Оповещения при превышении порогов

## Команды

### Mather_bots
- `/start` - Главное меню управления

### Telescan_bot
- `/start` - Главное меню мониторинга

## Добавление новых ботов

1. Создайте новую папку в корне проекта
2. Добавьте `main.py`, `config.json` и `requirements.txt`
3. Добавьте бота в конфигурацию менеджера (`Mather_bots/config.json`)
4. Перезапустите менеджер

## Автозапуск в Termux

Для автозапуска при перезагрузке Termux:

1. Создайте файл `~/.termux/boot/start_bots.sh`:
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd /path/to/your/Bots/Mather_bots
python main.py &
```

2. Сделайте файл исполняемым:
```bash
chmod +x ~/.termux/boot/start_bots.sh
```

## Логирование

Все боты создают логи в своих папках:
- `Mather_bots/manager.log`
- `Telescan_bot/telescan.log`

## Безопасность

- Все боты проверяют `admin_ids` в конфигурации
- Используйте разные токены для разных ботов
- Не публикуйте токены в открытом доступе 