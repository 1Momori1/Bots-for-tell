#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import time
import psutil
import signal

def kill_python_processes():
    """Убить все процессы Python, связанные с ботами"""
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Проверяем, что это Python процесс
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and any('main.py' in arg for arg in cmdline):
                    print(f"🔪 Убиваю процесс {proc.info['pid']}: {' '.join(cmdline)}")
                    try:
                        proc.kill()  # Принудительно убиваем
                        killed_count += 1
                    except psutil.NoSuchProcess:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return killed_count

def kill_telegram_bot_processes():
    """Убить процессы по имени файлов ботов"""
    bot_files = [
        "Telescan_bot/main.py",
        "MineServ_bot/main.py", 
        "Mather_bots/main.py"
    ]
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                cmdline_str = ' '.join(cmdline)
                for bot_file in bot_files:
                    if bot_file in cmdline_str:
                        print(f"🔪 Убиваю процесс бота {proc.info['pid']}: {cmdline_str}")
                        try:
                            proc.kill()
                            killed_count += 1
                        except psutil.NoSuchProcess:
                            pass
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return killed_count

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

def wait_for_processes_to_die():
    """Ждать, пока процессы полностью завершатся"""
    print("⏳ Ждем завершения процессов...")
    
    for _ in range(10):  # Ждем максимум 10 секунд
        active_processes = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in arg for arg in cmdline):
                        active_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if active_processes == 0:
            print("✅ Все процессы завершены")
            return True
        
        print(f"⏳ Осталось процессов: {active_processes}")
        time.sleep(1)
    
    print("⚠️ Некоторые процессы не завершились за 10 секунд")
    return False

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
    print("🧹 Чистый запуск системы ботов...")
    
    # 1. Убиваем все процессы Python с main.py
    print("\n🔪 Шаг 1: Убиваем все процессы ботов...")
    killed1 = kill_python_processes()
    killed2 = kill_telegram_bot_processes()
    total_killed = killed1 + killed2
    print(f"🔪 Убито процессов: {total_killed}")
    
    # 2. Ждем завершения процессов
    print("\n⏳ Шаг 2: Ждем завершения процессов...")
    wait_for_processes_to_die()
    
    # 3. Очищаем логи
    print("\n🧹 Шаг 3: Очищаем лог-файлы...")
    cleared = clear_logs()
    print(f"🧹 Очищено логов: {cleared}")
    
    # 4. Пауза для стабилизации
    print("\n⏳ Шаг 4: Пауза для стабилизации...")
    time.sleep(3)
    
    # 5. Запускаем ботов
    print("\n🚀 Шаг 5: Запускаем ботов...")
    
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