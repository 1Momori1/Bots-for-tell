#!/data/data/com.termux/files/usr/bin/bash

# Скрипт остановки ботов для Termux
# Автор: Bot System
# Версия: 1.0

echo "🛑 Остановка системы ботов в Termux..."

# Переходим в папку проекта
cd /storage/emulated/0/Bots 2>/dev/null || cd ~/Bots 2>/dev/null || {
    echo "❌ Папка Bots не найдена!"
    exit 1
}

echo "📁 Рабочая папка: $(pwd)"

# Останавливаем все процессы Python с main.py
echo "🔄 Поиск процессов ботов..."

# Находим все процессы
pids=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "ℹ️ Не найдено запущенных ботов"
else
    echo "🛑 Остановка процессов: $pids"
    
    # Останавливаем каждый процесс
    for pid in $pids; do
        echo "🔄 Остановка процесса $pid..."
        kill -TERM "$pid" 2>/dev/null
        
        # Ждем завершения
        sleep 2
        
        # Проверяем, завершился ли процесс
        if kill -0 "$pid" 2>/dev/null; then
            echo "⚠️ Принудительная остановка процесса $pid"
            kill -KILL "$pid" 2>/dev/null
        else
            echo "✅ Процесс $pid остановлен"
        fi
    done
fi

# Дополнительно убиваем все процессы с main.py
echo "🧹 Финальная очистка..."
pkill -f "main.py" 2>/dev/null || true

# Очищаем логи
echo "🧹 Очистка логов..."
for log_file in */telescan.log */mineserv.log */manager.log BotMonitor/bot_monitor.log; do
    if [ -f "$log_file" ]; then
        echo "# Лог очищен $(date)" > "$log_file"
        echo "🧹 Очищен: $log_file"
    fi
done

# Проверяем результат
echo ""
echo "🔍 Проверка процессов:"
remaining=$(ps aux | grep "main.py" | grep -v grep)
if [ -z "$remaining" ]; then
    echo "✅ Все боты остановлены!"
else
    echo "⚠️ Остались процессы:"
    echo "$remaining"
fi

echo ""
echo "✅ Остановка завершена!" 