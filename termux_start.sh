#!/data/data/com.termux/files/usr/bin/bash

# Скрипт запуска ботов для Termux
# Автор: Bot System
# Версия: 1.0

echo "🤖 Запуск системы ботов в Termux..."

# Переходим в папку проекта
cd /storage/emulated/0/Bots 2>/dev/null || cd ~/Bots 2>/dev/null || {
    echo "❌ Папка Bots не найдена!"
    echo "Убедитесь, что проект находится в /storage/emulated/0/Bots или ~/Bots"
    exit 1
}

echo "📁 Рабочая папка: $(pwd)"

# Проверяем наличие Python
if ! command -v python &> /dev/null; then
    echo "❌ Python не найден! Установите: pkg install python"
    exit 1
fi

# Останавливаем старые процессы
echo "🧹 Очистка старых процессов..."
pkill -f "main.py" 2>/dev/null || true
sleep 2

# Функция запуска бота
start_bot() {
    local bot_name="$1"
    local bot_path="$2"
    
    if [ ! -d "$bot_path" ]; then
        echo "⚠️ Папка $bot_path не найдена"
        return 1
    fi
    
    if [ ! -f "$bot_path/main.py" ]; then
        echo "❌ main.py не найден в $bot_path"
        return 1
    fi
    
    echo "🚀 Запуск $bot_name..."
    
    # Запускаем бота в фоне с логированием
    cd "$bot_path"
    nohup python main.py > "${bot_name,,}.log" 2>&1 &
    local pid=$!
    cd - > /dev/null
    
    echo "✅ $bot_name запущен (PID: $pid)"
    return 0
}

# Запускаем ботов
echo "🎯 Запуск ботов..."

start_bot "Telescan Bot" "Telescan_bot"
sleep 3

start_bot "MineServ Bot" "MineServ_bot"
sleep 3

start_bot "Manager Bot" "Mather_bots"
sleep 3

# Запускаем Bot Monitor отдельно
echo "📊 Запуск Bot Monitor..."
cd BotMonitor
nohup python main.py > bot_monitor.log 2>&1 &
monitor_pid=$!
cd - > /dev/null
echo "✅ Bot Monitor запущен (PID: $monitor_pid)"

# Показываем статус
echo ""
echo "🎉 Система ботов запущена!"
echo "📊 Проверьте статус через Bot Monitor"
echo "💡 Для остановки: pkill -f 'main.py'"
echo "📝 Логи в папках каждого бота"

# Проверяем процессы
echo ""
echo "🔍 Проверка процессов:"
ps aux | grep "main.py" | grep -v grep || echo "❌ Процессы не найдены"

echo ""
echo "✅ Готово! Боты работают в фоне." 