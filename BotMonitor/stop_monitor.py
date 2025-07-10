#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import psutil
import signal

def stop_bot_monitor():
    """Остановка бота-монитора"""
    try:
        print("🛑 Остановка Bot Monitor...")
        
        # Ищем процесс бота-монитора
        bot_monitor_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'main.py' in ' '.join(cmdline):
                    # Проверяем, что это бот-монитор
                    if 'BotMonitor' in ' '.join(cmdline) or 'bot_monitor' in ' '.join(cmdline):
                        bot_monitor_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if not bot_monitor_processes:
            print("ℹ️ Bot Monitor не найден среди запущенных процессов")
            return True
        
        # Останавливаем найденные процессы
        for proc in bot_monitor_processes:
            try:
                print(f"🔄 Остановка процесса PID: {proc.pid}")
                proc.terminate()
                
                # Ждем завершения
                try:
                    proc.wait(timeout=5)
                    print(f"✅ Процесс {proc.pid} остановлен")
                except psutil.TimeoutExpired:
                    print(f"⚠️ Принудительная остановка процесса {proc.pid}")
                    proc.kill()
                    proc.wait()
                    print(f"✅ Процесс {proc.pid} принудительно остановлен")
                    
            except Exception as e:
                print(f"❌ Ошибка остановки процесса {proc.pid}: {e}")
        
        print("✅ Bot Monitor остановлен!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка остановки Bot Monitor: {e}")
        return False

if __name__ == "__main__":
    stop_bot_monitor() 