#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

def start_bot_monitor():
    """Запуск бота-монитора"""
    try:
        # Переходим в папку бота-монитора
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("🚀 Запуск Bot Monitor...")
        print(f"📁 Рабочая папка: {script_dir}")
        
        # Проверяем наличие main.py
        if not os.path.exists('main.py'):
            print("❌ Ошибка: main.py не найден!")
            return False
        
        # Проверяем наличие config.json
        if not os.path.exists('config.json'):
            print("⚠️ config.json не найден, будет создан автоматически")
        
        # Запускаем бота
        print("🤖 Запуск Bot Monitor...")
        process = subprocess.Popen([sys.executable, 'main.py'])
        
        print(f"✅ Bot Monitor запущен с PID: {process.pid}")
        print("📊 Бот будет мониторить статус других ботов")
        print("💡 Используйте /start в Telegram для просмотра статуса")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска Bot Monitor: {e}")
        return False

if __name__ == "__main__":
    start_bot_monitor() 