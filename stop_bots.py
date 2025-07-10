#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import os
import sys
import time

def stop_python_processes():
    """Остановить все процессы Python"""
    stopped_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Проверяем, что это Python процесс
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and any('main.py' in arg for arg in cmdline):
                    print(f"🛑 Останавливаю процесс {proc.info['pid']}: {' '.join(cmdline)}")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)  # Ждем 3 секунды
                        stopped_count += 1
                    except psutil.TimeoutExpired:
                        print(f"🔪 Принудительно убиваю процесс {proc.info['pid']}")
                        proc.kill()
                        stopped_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return stopped_count

def clear_logs():
    """Очистить все лог-файлы"""
    log_files = [
        "Telescan_bot/telescan.log",
        "MineServ_bot/mineserv.log",
        "Mather_bots/manager.log"
    ]
    
    cleared_count = 0
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Очищаем файл, оставляя только заголовок
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Лог очищен {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"🧹 Очищен лог: {log_file}")
                cleared_count += 1
            except Exception as e:
                print(f"❌ Ошибка очистки {log_file}: {e}")
    
    return cleared_count

def main():
    """Основная функция"""
    print("🛑 Остановка всех ботов...")
    
    # Останавливаем процессы Python с main.py
    stopped = stop_python_processes()
    
    if stopped > 0:
        print(f"✅ Остановлено процессов: {stopped}")
    else:
        print("ℹ️ Не найдено запущенных ботов")
    
    # Очищаем логи
    print("\n🧹 Очищаем лог-файлы...")
    cleared = clear_logs()
    print(f"🧹 Очищено логов: {cleared}")
    
    # Дополнительно можно остановить по имени файлов
    bot_files = [
        "Telescan_bot/main.py",
        "MineServ_bot/main.py", 
        "Mather_bots/main.py"
    ]
    
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"📁 Проверяю {bot_file}...")

if __name__ == '__main__':
    main() 