#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import psutil
import schedule
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telescan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelescanBot:
    def __init__(self):
        self.config = self.load_config()
        self.last_alert_time = {}
        self.monitoring_task = None
        
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Файл config.json не найден!")
            return {}
    
    def get_system_info(self):
        """Получение информации о системе"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Память
            memory = psutil.virtual_memory()
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Диск
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Температура (если доступно)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000
            except:
                temp = None
            
            # Сеть
            network = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory.percent,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'disk_percent': disk.percent,
                'disk_used_gb': disk_used_gb,
                'disk_total_gb': disk_total_gb,
                'temperature': temp,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
        except Exception as e:
            logger.error(f"Ошибка получения системной информации: {e}")
            return {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if update.effective_user.id not in self.config.get('admin_ids', []):
            await update.message.reply_text("⛔ У вас нет доступа к этому боту!")
            return
            
        keyboard = [
            [InlineKeyboardButton("📊 Системная информация", callback_data='system_info')],
            [InlineKeyboardButton("🌡️ Температура", callback_data='temperature')],
            [InlineKeyboardButton("💾 Память", callback_data='memory')],
            [InlineKeyboardButton("💿 Диск", callback_data='disk')],
            [InlineKeyboardButton("🌐 Сеть", callback_data='network')],
            [InlineKeyboardButton("⚙️ Настройки мониторинга", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📱 **Telescan Bot - Мониторинг телефона**\n\n"
            "Выберите что хотите проверить:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'system_info':
            await self.show_system_info(query)
        elif query.data == 'temperature':
            await self.show_temperature(query)
        elif query.data == 'memory':
            await self.show_memory_info(query)
        elif query.data == 'disk':
            await self.show_disk_info(query)
        elif query.data == 'network':
            await self.show_network_info(query)
        elif query.data == 'settings':
            await self.show_settings(query)
        elif query.data == 'back_to_main':
            await self.show_main_menu(query)
    
    async def show_system_info(self, query):
        """Показать общую системную информацию"""
        info = self.get_system_info()
        
        if not info:
            await query.edit_message_text("❌ Ошибка получения данных")
            return
        
        # Определение статуса системы
        status_emoji = "🟢"
        if info['cpu_percent'] > self.config['monitoring']['cpu_threshold']:
            status_emoji = "🔴"
        elif info['memory_percent'] > self.config['monitoring']['memory_threshold']:
            status_emoji = "🟡"
        
        system_text = f"""
{status_emoji} **Системная информация**

🖥️ **CPU:** {info['cpu_percent']:.1f}% ({info['cpu_count']} ядер)
💾 **RAM:** {info['memory_percent']:.1f}% ({info['memory_used_gb']:.1f}GB / {info['memory_total_gb']:.1f}GB)
💿 **Диск:** {info['disk_percent']:.1f}% ({info['disk_used_gb']:.1f}GB / {info['disk_total_gb']:.1f}GB)
⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        if info['temperature']:
            system_text += f"\n🌡️ **Температура:** {info['temperature']:.1f}°C"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            system_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_temperature(self, query):
        """Показать информацию о температуре"""
        info = self.get_system_info()
        
        if info.get('temperature'):
            temp = info['temperature']
            status = "🟢 Нормальная" if temp < self.config['monitoring']['temperature_threshold'] else "🔴 Высокая"
            
            temp_text = f"""
🌡️ **Температура системы**

**Текущая:** {temp:.1f}°C
**Статус:** {status}
**Порог:** {self.config['monitoring']['temperature_threshold']}°C

⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
            """
        else:
            temp_text = "❌ Информация о температуре недоступна"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            temp_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_memory_info(self, query):
        """Показать информацию о памяти"""
        info = self.get_system_info()
        
        memory_text = f"""
💾 **Информация о памяти**

**Использовано:** {info['memory_percent']:.1f}%
**Объем:** {info['memory_used_gb']:.1f}GB / {info['memory_total_gb']:.1f}GB
**Свободно:** {info['memory_total_gb'] - info['memory_used_gb']:.1f}GB

**Статус:** {'🔴 Критично' if info['memory_percent'] > self.config['monitoring']['memory_threshold'] else '🟢 Нормально'}

⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            memory_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_disk_info(self, query):
        """Показать информацию о диске"""
        info = self.get_system_info()
        
        disk_text = f"""
💿 **Информация о диске**

**Использовано:** {info['disk_percent']:.1f}%
**Объем:** {info['disk_used_gb']:.1f}GB / {info['disk_total_gb']:.1f}GB
**Свободно:** {info['disk_total_gb'] - info['disk_used_gb']:.1f}GB

**Статус:** {'🔴 Критично' if info['disk_percent'] > self.config['monitoring']['disk_threshold'] else '🟢 Нормально'}

⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            disk_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_network_info(self, query):
        """Показать информацию о сети"""
        info = self.get_system_info()
        
        # Конвертация в MB
        sent_mb = info['network_bytes_sent'] / (1024**2)
        recv_mb = info['network_bytes_recv'] / (1024**2)
        
        network_text = f"""
🌐 **Информация о сети**

**Отправлено:** {sent_mb:.1f}MB
**Получено:** {recv_mb:.1f}MB
**Всего:** {sent_mb + recv_mb:.1f}MB

⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            network_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_settings(self, query):
        """Показать настройки мониторинга"""
        settings_text = f"""
⚙️ **Настройки мониторинга**

**Интервал проверки:** {self.config['monitoring']['check_interval']} сек
**Порог CPU:** {self.config['monitoring']['cpu_threshold']}%
**Порог памяти:** {self.config['monitoring']['memory_threshold']}%
**Порог диска:** {self.config['monitoring']['disk_threshold']}%
**Порог температуры:** {self.config['monitoring']['temperature_threshold']}°C

**Уведомления:** {'✅ Включены' if self.config['alerts']['enable_notifications'] else '❌ Выключены'}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_main_menu(self, query):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("📊 Системная информация", callback_data='system_info')],
            [InlineKeyboardButton("🌡️ Температура", callback_data='temperature')],
            [InlineKeyboardButton("💾 Память", callback_data='memory')],
            [InlineKeyboardButton("💿 Диск", callback_data='disk')],
            [InlineKeyboardButton("🌐 Сеть", callback_data='network')],
            [InlineKeyboardButton("⚙️ Настройки мониторинга", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📱 **Telescan Bot - Мониторинг телефона**\n\n"
            "Выберите что хотите проверить:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def main():
    """Основная функция"""
    bot = TelescanBot()
    
    # Создание приложения
    application = Application.builder().token(bot.config['bot_token']).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Запуск бота
    logger.info("Telescan Bot запущен")
    await application.run_polling()

if __name__ == '__main__':
    import sys

    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Если цикл уже работает (Termux/Cursor/встроенные среды) — обходим
        if "event loop is already running" in str(e):
            print("Цикл уже запущен, fallback: прямой await")
            coro = main()
            task = asyncio.ensure_future(coro)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(task)
        else:
            raise e 