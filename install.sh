#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Установка системы управления ботами для Termux"
echo "================================================"

# Обновление системы
echo "📦 Обновление пакетов..."
pkg update -y && pkg upgrade -y

# Установка Python и pip
echo "🐍 Установка Python..."
pkg install python python-pip -y

# Установка зависимостей для менеджера
echo "📥 Установка зависимостей для менеджера..."
cd Mather_bots
pip install -r requirements.txt

# Установка зависимостей для Telescan
echo "📥 Установка зависимостей для Telescan..."
cd ../Telescan_bot
pip install -r requirements.txt

# Создание папки для логов
echo "📁 Создание папок для логов..."
cd ..
mkdir -p logs

# Настройка автозапуска
echo "⚙️ Настройка автозапуска..."
mkdir -p ~/.termux/boot

cat > ~/.termux/boot/start_bots.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $(dirname $0)/../../Bots/Mather_bots
python main.py > ../logs/manager.log 2>&1 &
EOF

chmod +x ~/.termux/boot/start_bots.sh

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте токены ботов в config.json файлах"
echo "2. Добавьте свой Telegram ID в admin_ids"
echo "3. Запустите менеджер: cd Mather_bots && python main.py"
echo ""
echo "🔧 Для автозапуска при перезагрузке Termux:"
echo "   Файл ~/.termux/boot/start_bots.sh уже создан"
echo ""
echo "📚 Подробная документация в README.md" 