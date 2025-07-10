#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к родительской папке для импорта main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBotManager(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временный конфиг для тестов
        self.test_config = {
            "bot_token": "test_token",
            "admin_ids": [123456789],
            "bots": {
                "telescan": {
                    "name": "Telescan Bot",
                    "path": "../Telescan_bot/main.py",
                    "enabled": True,
                    "auto_restart": True
                },
                "mineserv": {
                    "name": "MineServ Bot",
                    "path": "../MineServ_bot/main.py",
                    "enabled": True,
                    "auto_restart": True
                }
            },
            "monitoring": {
                "check_interval": 30,
                "max_restart_attempts": 3,
                "log_level": "INFO"
            }
        }
        
        # Создаем временный файл конфига
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временный файл
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)
    
    @patch('main.open')
    def test_load_config_success(self, mock_open):
        """Тест успешной загрузки конфигурации"""
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(self.test_config)
        
        from main import BotManager
        manager = BotManager()
        
        self.assertEqual(manager.config['bot_token'], 'test_token')
        self.assertEqual(manager.config['admin_ids'], [123456789])
        self.assertIn('telescan', manager.config['bots'])
        self.assertIn('mineserv', manager.config['bots'])
    
    @patch('main.open')
    def test_load_config_file_not_found(self, mock_open):
        """Тест обработки отсутствующего файла конфига"""
        mock_open.side_effect = FileNotFoundError()
        
        from main import BotManager
        manager = BotManager()
        
        self.assertEqual(manager.config, {})
    
    def test_bot_config_validation(self):
        """Тест валидации конфигурации ботов"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        # Проверяем структуру ботов
        bots = manager.config['bots']
        for bot_id, bot_config in bots.items():
            required_fields = ['name', 'path', 'enabled', 'auto_restart']
            for field in required_fields:
                self.assertIn(field, bot_config)
            
            # Проверяем типы данных
            self.assertIsInstance(bot_config['name'], str)
            self.assertIsInstance(bot_config['path'], str)
            self.assertIsInstance(bot_config['enabled'], bool)
            self.assertIsInstance(bot_config['auto_restart'], bool)
    
    def test_admin_check(self):
        """Тест проверки администратора"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        # Тест с правильным ID
        self.assertTrue(123456789 in manager.config.get('admin_ids', []))
        
        # Тест с неправильным ID
        self.assertFalse(999999999 in manager.config.get('admin_ids', []))
    
    def test_bot_processes_initialization(self):
        """Тест инициализации словаря процессов ботов"""
        from main import BotManager
        manager = BotManager()
        
        self.assertEqual(manager.bot_processes, {})
        self.assertEqual(manager.restart_attempts, {})
    
    @patch('os.path.exists')
    @patch('subprocess.Popen')
    def test_start_bot_success(self, mock_popen, mock_exists):
        """Тест успешного запуска бота"""
        mock_exists.return_value = True
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Процесс запущен
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        success, error = await manager.start_bot('telescan')
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIn('telescan', manager.bot_processes)
    
    @patch('os.path.exists')
    def test_start_bot_file_not_found(self, mock_exists):
        """Тест запуска бота с несуществующим файлом"""
        mock_exists.return_value = False
        
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        success, error = await manager.start_bot('telescan')
        
        self.assertFalse(success)
        self.assertIn('не найден', error)
    
    def test_stop_bot_success(self):
        """Тест успешной остановки бота"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        # Создаем мок процесса
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Процесс запущен
        manager.bot_processes['telescan'] = mock_process
        
        success, error = await manager.stop_bot('telescan')
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertNotIn('telescan', manager.bot_processes)
    
    def test_stop_bot_not_found(self):
        """Тест остановки несуществующего бота"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        success, error = await manager.stop_bot('nonexistent')
        
        self.assertFalse(success)
        self.assertIn('не найден', error)
    
    def test_monitoring_config_validation(self):
        """Тест валидации конфигурации мониторинга"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        monitoring = manager.config['monitoring']
        required_fields = ['check_interval', 'max_restart_attempts', 'log_level']
        for field in required_fields:
            self.assertIn(field, monitoring)
        
        # Проверяем типы данных
        self.assertIsInstance(monitoring['check_interval'], int)
        self.assertIsInstance(monitoring['max_restart_attempts'], int)
        self.assertIsInstance(monitoring['log_level'], str)
    
    def test_config_structure_completeness(self):
        """Тест полноты структуры конфигурации"""
        from main import BotManager
        manager = BotManager()
        manager.config = self.test_config
        
        # Проверяем все основные секции
        required_sections = ['bot_token', 'admin_ids', 'bots', 'monitoring']
        for section in required_sections:
            self.assertIn(section, manager.config)
        
        # Проверяем количество ботов
        self.assertEqual(len(manager.config['bots']), 2)
        self.assertIn('telescan', manager.config['bots'])
        self.assertIn('mineserv', manager.config['bots'])

if __name__ == '__main__':
    unittest.main() 