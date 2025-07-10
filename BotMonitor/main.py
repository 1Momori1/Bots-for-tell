#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
import psutil
import sys
import traceback
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Попробуем импортировать nest_asyncio для Windows/IDE
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Обработчик необработанных исключений
ERROR_LOG = 'errors.txt'

def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*40}\n")
        f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Тип: {exc_type.__name__}\n")
        f.write(f"Ошибка: {exc_value}\n")
        traceback.print_tb(exc_traceback, file=f)
        f.write(f"{'='*40}\n")

sys.excepthook = log_uncaught_exception

class BotMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.status_message = None
        self.monitoring_task = None
        self.auto_update_enabled = self.config.get('monitoring', {}).get('auto_update', True)
        
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            config = {
                "bot_token": "8058368540:AAFzYy41vBayoIQG8RQ_DDGPSr1gbA690d8",
                "admin_ids": [824312416],
                "bots": {
                    "telescan": {
                        "name": "Telescan Bot",
                        "path": "../Telescan_bot/main.py",
                        "process_name": "python"
                    },
                    "mineserv": {
                        "name": "MineServ Bot", 
                        "path": "../MineServ_bot/main.py",
                        "process_name": "python"
                    },
                    "manager": {
                        "name": "Manager Bot",
                        "path": "../Mather_bots/main.py", 
                        "process_name": "python"
                    }
                },
                "monitoring": {
                    "update_interval": 30,  # секунды
                    "auto_update": True
                }
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return config
    
    def get_bot_status(self, bot_id, bot_config):
        """Получить статус конкретного бота"""
        try:
            # Ищем процесс по имени файла main.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in arg for arg in cmdline):
                        # Проверяем, что это нужный бот
                        if bot_config['path'] in ' '.join(cmdline):
                            if proc.poll() is None:
                                return "🟢 Работает", proc.pid
                            else:
                                return "🔴 Упал", None
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return "🔴 Остановлен", None
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса бота {bot_id}: {e}")
            return "❓ Ошибка", None
    
    def get_system_info(self):
        """Получить информацию о системе"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3)
            }
        except Exception as e:
            logger.error(f"Ошибка получения системной информации: {e}")
            return {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if update.effective_user.id not in self.config.get('admin_ids', []):
            await update.message.reply_text("⛔ У вас нет доступа к этому боту!")
            return
        
        await self.show_status(update.message)
    
    async def show_status(self, message_or_query):
        """Показать статус всех ботов"""
        # Получаем системную информацию
        system_info = self.get_system_info()
        
        # Формируем текст статуса
        status_text = "📊 **Монитор ботов**\n\n"
        
        # Статус ботов
        status_text += "🤖 **Боты:**\n"
        total_bots = 0
        running_bots = 0
        
        for bot_id, bot_config in self.config.get('bots', {}).items():
            status, pid = self.get_bot_status(bot_id, bot_config)
            status_text += f"{status} **{bot_config['name']}**"
            if pid:
                status_text += f" (PID: {pid})"
            status_text += "\n"
            
            total_bots += 1
            if "Работает" in status:
                running_bots += 1
        
        status_text += f"\n📈 **Статистика:** {running_bots}/{total_bots} ботов работают\n\n"
        
        # Системная информация
        if system_info:
            status_text += "💻 **Система:**\n"
            status_text += f"🖥️ CPU: {system_info['cpu_percent']:.1f}%\n"
            status_text += f"💾 RAM: {system_info['memory_percent']:.1f}% ({system_info['memory_used_gb']:.1f}GB / {system_info['memory_total_gb']:.1f}GB)\n"
            status_text += f"💿 Диск: {system_info['disk_percent']:.1f}% ({system_info['disk_used_gb']:.1f}GB / {system_info['disk_total_gb']:.1f}GB)\n"
        
        status_text += f"\n⏰ **Обновлено:** {datetime.now().strftime('%H:%M:%S')}"
        
        # Кнопки управления
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data='refresh')],
            [InlineKeyboardButton("🔄 Автообновление", callback_data='toggle_auto')],
            [InlineKeyboardButton("📊 Подробно", callback_data='detailed')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Обновляем или отправляем сообщение
        if hasattr(message_or_query, 'edit_message_text'):
            await message_or_query.edit_message_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            self.status_message = await message_or_query.reply_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'refresh':
            await self.show_status(query)
        elif query.data == 'toggle_auto':
            await self.toggle_auto_update(query)
        elif query.data == 'detailed':
            await self.show_detailed_status(query)
    
    async def toggle_auto_update(self, query):
        """Переключить автообновление"""
        self.auto_update_enabled = not self.auto_update_enabled
        
        if self.auto_update_enabled:
            await query.edit_message_text(
                "✅ Автообновление включено! Статус будет обновляться автоматически.",
                parse_mode='Markdown'
            )
            # Запускаем автообновление
            if not self.monitoring_task or self.monitoring_task.done():
                self.monitoring_task = asyncio.create_task(self.auto_update_status())
        else:
            await query.edit_message_text(
                "❌ Автообновление отключено!",
                parse_mode='Markdown'
            )
            # Останавливаем автообновление
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
    
    async def show_detailed_status(self, query):
        """Показать подробный статус"""
        detailed_text = "📊 **Подробный статус системы**\n\n"
        
        # Подробная информация о ботах
        for bot_id, bot_config in self.config.get('bots', {}).items():
            status, pid = self.get_bot_status(bot_id, bot_config)
            detailed_text += f"**{bot_config['name']}**\n"
            detailed_text += f"Статус: {status}\n"
            if pid:
                detailed_text += f"PID: {pid}\n"
            detailed_text += f"Путь: `{bot_config['path']}`\n\n"
        
        # Подробная системная информация
        system_info = self.get_system_info()
        if system_info:
            detailed_text += "💻 **Системная информация:**\n"
            detailed_text += f"CPU: {system_info['cpu_percent']:.1f}%\n"
            detailed_text += f"RAM: {system_info['memory_percent']:.1f}% ({system_info['memory_used_gb']:.1f}GB / {system_info['memory_total_gb']:.1f}GB)\n"
            detailed_text += f"Диск: {system_info['disk_percent']:.1f}% ({system_info['disk_used_gb']:.1f}GB / {system_info['disk_total_gb']:.1f}GB)\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='refresh')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            detailed_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def auto_update_status(self):
        """Автоматическое обновление статуса"""
        interval = self.config.get('monitoring', {}).get('update_interval', 30)
        
        while self.auto_update_enabled:
            try:
                await asyncio.sleep(interval)
                if self.status_message and self.auto_update_enabled:
                    await self.show_status(self.status_message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка автообновления: {e}")
                await asyncio.sleep(5)

async def main():
    """Главная функция"""
    try:
        # Создаем экземпляр бота
        bot_monitor = BotMonitor()
        
        # Создаем приложение
        application = Application.builder().token(bot_monitor.config['bot_token']).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot_monitor.start_command))
        application.add_handler(CallbackQueryHandler(bot_monitor.button_handler))
        
        # Запускаем автообновление если включено
        if bot_monitor.auto_update_enabled:
            bot_monitor.monitoring_task = asyncio.create_task(bot_monitor.auto_update_status())
        
        logger.info("Bot Monitor запущен!")
        
        # Запускаем бота
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        traceback.print_exc()
        
        # Отправляем уведомление администраторам
        try:
            error_text = f"❌ **Ошибка Bot Monitor:**\n{str(e)}"
            for admin_id in bot_monitor.config.get('admin_ids', []):
                try:
                    await application.bot.send_message(
                        chat_id=admin_id,
                        text=error_text,
                        parse_mode='Markdown'
                    )
                except Exception as send_error:
                    logger.error(f"Не удалось отправить уведомление админу {admin_id}: {send_error}")
        except Exception as notify_error:
            logger.error(f"Ошибка отправки уведомления: {notify_error}")

if __name__ == "__main__":
    try:
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot Monitor остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
        traceback.print_exc()
        
        # Fallback для Windows/IDE
        try:
            def run_bot():
                asyncio.run(main())
            
            import threading
            thread = threading.Thread(target=run_bot)
            thread.daemon = True
            thread.start()
            thread.join()
        except Exception as fallback_error:
            logger.error(f"Fallback тоже не сработал: {fallback_error}") 