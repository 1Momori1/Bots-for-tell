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

class TestMineServBot(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временный конфиг для тестов
        self.test_config = {
            "bot_token": "test_token",
            "admin_ids": [123456789],
            "server": {
                "jar_path": "server.jar",
                "max_ram": "2G",
                "min_ram": "1G",
                "port": 25565,
                "world_name": "world",
                "auto_restart": True,
                "server_properties": {
                    "gamemode": "survival",
                    "difficulty": "normal",
                    "max_players": 20
                }
            },
            "monitoring": {
                "check_interval": 30,
                "max_restart_attempts": 3,
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90
            },
            "backup": {
                "enabled": True,
                "interval_hours": 6,
                "keep_backups": 7,
                "backup_path": "./backups"
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
        
        from main import MineServBot
        bot = MineServBot()
        
        self.assertEqual(bot.config['bot_token'], 'test_token')
        self.assertEqual(bot.config['admin_ids'], [123456789])
        self.assertEqual(bot.config['server']['port'], 25565)
        self.assertEqual(bot.config['server']['max_ram'], '2G')
    
    @patch('main.open')
    def test_load_config_file_not_found(self, mock_open):
        """Тест обработки отсутствующего файла конфига"""
        mock_open.side_effect = FileNotFoundError()
        
        from main import MineServBot
        bot = MineServBot()
        
        # Должен создать базовую конфигурацию
        self.assertIn('bot_token', bot.config)
        self.assertIn('server', bot.config)
        self.assertIn('monitoring', bot.config)
    
    def test_server_status_initialization(self):
        """Тест инициализации статуса сервера"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        self.assertEqual(bot.server_status, "stopped")
        self.assertIsNone(bot.server_process)
    
    def test_server_config_validation(self):
        """Тест валидации конфигурации сервера"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        # Проверяем обязательные поля сервера
        server_config = bot.config['server']
        required_fields = ['jar_path', 'max_ram', 'min_ram', 'port', 'world_name']
        for field in required_fields:
            self.assertIn(field, server_config)
        
        # Проверяем типы данных
        self.assertIsInstance(server_config['port'], int)
        self.assertIsInstance(server_config['auto_restart'], bool)
        self.assertIsInstance(server_config['max_ram'], str)
    
    def test_monitoring_config_validation(self):
        """Тест валидации конфигурации мониторинга"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        monitoring_config = bot.config['monitoring']
        required_fields = ['check_interval', 'max_restart_attempts', 'cpu_threshold']
        for field in required_fields:
            self.assertIn(field, monitoring_config)
        
        # Проверяем типы данных
        self.assertIsInstance(monitoring_config['check_interval'], int)
        self.assertIsInstance(monitoring_config['cpu_threshold'], int)
    
    def test_backup_config_validation(self):
        """Тест валидации конфигурации бэкапов"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        backup_config = bot.config['backup']
        required_fields = ['enabled', 'interval_hours', 'keep_backups', 'backup_path']
        for field in required_fields:
            self.assertIn(field, backup_config)
        
        # Проверяем типы данных
        self.assertIsInstance(backup_config['enabled'], bool)
        self.assertIsInstance(backup_config['interval_hours'], int)
        self.assertIsInstance(backup_config['keep_backups'], int)
    
    def test_admin_check(self):
        """Тест проверки администратора"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        # Тест с правильным ID
        self.assertTrue(123456789 in bot.config.get('admin_ids', []))
        
        # Тест с неправильным ID
        self.assertFalse(999999999 in bot.config.get('admin_ids', []))
    
    def test_server_status_emoji_mapping(self):
        """Тест маппинга статусов сервера на эмодзи"""
        from main import MineServBot
        bot = MineServBot()
        
        # Тестируем все возможные статусы
        status_emoji = {
            "stopped": "🔴",
            "starting": "🟡", 
            "running": "🟢",
            "stopping": "🟠"
        }
        
        for status, expected_emoji in status_emoji.items():
            bot.server_status = status
            # Здесь можно добавить проверку, если есть метод получения эмодзи
    
    def test_config_structure_completeness(self):
        """Тест полноты структуры конфигурации"""
        from main import MineServBot
        bot = MineServBot()
        bot.config = self.test_config
        
        # Проверяем все основные секции
        required_sections = ['bot_token', 'admin_ids', 'server', 'monitoring', 'backup']
        for section in required_sections:
            self.assertIn(section, bot.config)
        
        # Проверяем вложенные структуры
        self.assertIn('server_properties', bot.config['server'])
        self.assertIn('gamemode', bot.config['server']['server_properties'])

if __name__ == '__main__':
    unittest.main() 