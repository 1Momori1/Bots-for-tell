#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def run_tests_for_bot(bot_name, bot_path):
    """Запустить тесты для конкретного бота"""
    print(f"\n🧪 Запуск тестов для {bot_name}...")
    
    if not os.path.exists(bot_path):
        print(f"❌ Папка {bot_path} не найдена")
        return False
    
    test_path = os.path.join(bot_path, 'tests')
    if not os.path.exists(test_path):
        print(f"⚠️ Папка тестов не найдена: {test_path}")
        return False
    
    try:
        # Переходим в папку бота
        original_dir = os.getcwd()
        os.chdir(bot_path)
        
        # Запускаем тесты
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 'discover', 'tests', '-v'
        ], capture_output=True, text=True)
        
        # Возвращаемся в исходную папку
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print(f"✅ Тесты {bot_name} прошли успешно")
            return True
        else:
            print(f"❌ Тесты {bot_name} провалились:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска тестов {bot_name}: {e}")
        return False

def main():
    """Основная функция"""
    print("🧪 Запуск всех unit-тестов...")
    
    # Список ботов для тестирования
    bots = [
        ("Telescan Bot", "Telescan_bot"),
        ("MineServ Bot", "MineServ_bot"),
        ("Manager Bot", "Mather_bots")
    ]
    
    total_tests = len(bots)
    passed_tests = 0
    
    for bot_name, bot_path in bots:
        if run_tests_for_bot(bot_name, bot_path):
            passed_tests += 1
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Пройдено: {passed_tests}/{total_tests}")
    print(f"❌ Провалено: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("⚠️ Некоторые тесты провалились")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 