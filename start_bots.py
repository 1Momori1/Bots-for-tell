#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import time
import signal
import psutil

def start_bot(bot_name, bot_path):
    """Запустить бота в отдельном процессе"""
    try:
        # Проверяем, что папка существует
        if not os.path.exists(bot_path):
            print(f"❌ Папка {bot_path} не найдена")
            return None
            
        # Проверяем, что main.py существует
        main_file = os.path.join(bot_path, 'main.py')
        if not os.path.exists(main_file):
            print(f"❌ Файл main.py не найден в {bot_path}")
            return None
        
        # Запускаем бота
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                [sys.executable, main_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=bot_path  # Устанавливаем рабочую директорию
            )
        else:  # Linux/Android
            process = subprocess.Popen(
                [sys.executable, main_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=bot_path  # Устанавливаем рабочую директорию
            )
        
        print(f"✅ {bot_name} запущен (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Ошибка запуска {bot_name}: {e}")
        return None

def stop_bot(process, bot_name):
    """Остановить бота"""
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f"⏹️ {bot_name} остановлен")
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"🔪 {bot_name} принудительно остановлен")
        except Exception as e:
            print(f"❌ Ошибка остановки {bot_name}: {e}")

def main():
    """Основная функция"""
    print("🤖 Запуск системы ботов...")
    
    # Список ботов для запуска
    bots = [
        ("Telescan Bot", "Telescan_bot"),
        ("MineServ Bot", "MineServ_bot"),
        ("Manager Bot", "Mather_bots")
    ]
    
    processes = []
    
    try:
        # Запускаем всех ботов
        for bot_name, bot_path in bots:
            if os.path.exists(bot_path):
                process = start_bot(bot_name, bot_path)
                if process:
                    processes.append((process, bot_name))
                time.sleep(2)  # Пауза между запусками
            else:
                print(f"⚠️ Папка {bot_path} не найдена")
        
        print(f"\n🎉 Запущено ботов: {len(processes)}")
        print("💡 Для остановки нажмите Ctrl+C")
        
        # Ждем сигнала остановки
        while True:
            time.sleep(1)
            
            # Проверяем, не упал ли какой-то бот
            for process, bot_name in processes[:]:
                if process.poll() is not None:
                    print(f"⚠️ {bot_name} завершился неожиданно")
                    processes.remove((process, bot_name))
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        
        # Останавливаем всех ботов
        for process, bot_name in processes:
            stop_bot(process, bot_name)
        
        print("✅ Все боты остановлены")
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        
        # Останавливаем всех ботов при ошибке
        for process, bot_name in processes:
            stop_bot(process, bot_name)

if __name__ == '__main__':
    main() 