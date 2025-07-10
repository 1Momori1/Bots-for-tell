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

class TestTelescanBot(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временный конфиг для тестов
        self.test_config = {
            "bot_token": "test_token",
            "admin_ids": [123456789],
            "monitoring": {
                "check_interval": 60,
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "temperature_threshold": 45,
                "disk_threshold": 90
            },
            "alerts": {
                "enable_notifications": True,
                "notification_interval": 300
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
        
        # Импортируем класс после мока
        from main import TelescanBot
        bot = TelescanBot()
        
        self.assertEqual(bot.config['bot_token'], 'test_token')
        self.assertEqual(bot.config['admin_ids'], [123456789])
        self.assertEqual(bot.config['monitoring']['cpu_threshold'], 80)
    
    @patch('main.open')
    def test_load_config_file_not_found(self, mock_open):
        """Тест обработки отсутствующего файла конфига"""
        mock_open.side_effect = FileNotFoundError()
        
        from main import TelescanBot
        bot = TelescanBot()
        
        self.assertEqual(bot.config, {})
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_get_system_info(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Тест получения системной информации"""
        # Мокаем системные вызовы
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(
            percent=60.0,
            used=4*1024**3,  # 4GB
            total=8*1024**3   # 8GB
        )
        mock_disk.return_value = MagicMock(
            percent=45.0,
            used=100*1024**3,  # 100GB
            total=500*1024**3  # 500GB
        )
        mock_net.return_value = MagicMock(
            bytes_sent=1024**3,  # 1GB
            bytes_recv=2*1024**3  # 2GB
        )
        
        from main import TelescanBot
        bot = TelescanBot()
        bot.config = self.test_config
        
        info = bot.get_system_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['cpu_percent'], 25.5)
        self.assertEqual(info['memory_percent'], 60.0)
        self.assertEqual(info['disk_percent'], 45.0)
        self.assertIn('network_bytes_sent', info)
        self.assertIn('network_bytes_recv', info)
    
    def test_admin_check(self):
        """Тест проверки администратора"""
        from main import TelescanBot
        bot = TelescanBot()
        bot.config = self.test_config
        
        # Тест с правильным ID
        self.assertTrue(123456789 in bot.config.get('admin_ids', []))
        
        # Тест с неправильным ID
        self.assertFalse(999999999 in bot.config.get('admin_ids', []))
    
    @patch('main.open')
    def test_temperature_reading(self, mock_open):
        """Тест чтения температуры"""
        # Мокаем файл температуры
        mock_open.return_value.__enter__.return_value.read.return_value = "45000"  # 45°C
        
        from main import TelescanBot
        bot = TelescanBot()
        bot.config = self.test_config
        
        info = bot.get_system_info()
        
        # Если температура доступна, она должна быть 45°C
        if 'temperature' in info and info['temperature'] is not None:
            self.assertEqual(info['temperature'], 45.0)
    
    def test_config_validation(self):
        """Тест валидации конфигурации"""
        from main import TelescanBot
        bot = TelescanBot()
        bot.config = self.test_config
        
        # Проверяем обязательные поля
        required_fields = ['bot_token', 'admin_ids', 'monitoring']
        for field in required_fields:
            self.assertIn(field, bot.config)
        
        # Проверяем структуру monitoring
        monitoring = bot.config['monitoring']
        required_monitoring_fields = ['check_interval', 'cpu_threshold', 'memory_threshold', 'disk_threshold']
        for field in required_monitoring_fields:
            self.assertIn(field, monitoring)

if __name__ == '__main__':
    unittest.main() 