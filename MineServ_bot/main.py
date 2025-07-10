#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
import subprocess
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
        logging.FileHandler('mineserv.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

class MineServBot:
    def __init__(self):
        self.config = self.load_config()
        self.server_process = None
        self.server_status = "stopped"  # stopped, starting, running, stopping
        
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            config = {
                "bot_token": "YOUR_BOT_TOKEN_HERE",
                "admin_ids": [824312416],
                "server": {
                    "jar_path": "server.jar",
                    "max_ram": "2G",
                    "min_ram": "1G",
                    "port": 25565,
                    "world_name": "world",
                    "auto_restart": True
                },
                "monitoring": {
                    "check_interval": 30,
                    "max_restart_attempts": 3
                }
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return config
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if update.effective_user.id not in self.config.get('admin_ids', []):
            await update.message.reply_text("⛔ У вас нет доступа к этому боту!")
            return
        
        await self.show_main_menu(update.message)
    
    async def show_main_menu(self, message_or_query):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("🖥️ Статус сервера", callback_data='server_status')],
            [InlineKeyboardButton("▶️ Запустить сервер", callback_data='start_server')],
            [InlineKeyboardButton("⏹️ Остановить сервер", callback_data='stop_server')],
            [InlineKeyboardButton("🔄 Перезапустить сервер", callback_data='restart_server')],
            [InlineKeyboardButton("📊 Мониторинг", callback_data='monitoring')],
            [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "⛏️ **MineServ Bot**\n\nУправление сервером Minecraft"
        
        if hasattr(message_or_query, 'edit_message_text'):
            await message_or_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif hasattr(message_or_query, 'message'):
            await message_or_query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await message_or_query.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'server_status':
            await self.show_server_status(query)
        elif query.data == 'start_server':
            await self.start_server(query)
        elif query.data == 'stop_server':
            await self.stop_server(query)
        elif query.data == 'restart_server':
            await self.restart_server(query)
        elif query.data == 'monitoring':
            await self.show_monitoring(query)
        elif query.data == 'settings':
            await self.show_settings(query)
        elif query.data == 'back_to_main':
            await self.show_main_menu(query)
    
    async def show_server_status(self, query):
        """Показать статус сервера"""
        status_emoji = {
            "stopped": "🔴",
            "starting": "🟡", 
            "running": "🟢",
            "stopping": "🟠"
        }
        
        status_text = f"""
🖥️ **Статус сервера Minecraft**

{status_emoji.get(self.server_status, "❓")} **Статус:** {self.server_status.upper()}

"""
        
        if self.server_process and self.server_process.poll() is None:
            status_text += f"🆔 **PID:** {self.server_process.pid}\n"
            status_text += f"⏰ **Время работы:** {self.get_uptime()}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def start_server(self, query):
        """Запустить сервер"""
        if self.server_status == "running":
            await query.edit_message_text(
                "⚠️ Сервер уже запущен!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
            return
        
        self.server_status = "starting"
        await query.edit_message_text(
            "🟡 Запускаю сервер Minecraft...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
        )
        
        # Имитация запуска сервера (болванка)
        await asyncio.sleep(3)
        
        try:
            # Здесь будет реальный запуск сервера
            # self.server_process = subprocess.Popen([...])
            self.server_status = "running"
            await query.edit_message_text(
                "✅ Сервер Minecraft запущен!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
        except Exception as e:
            self.server_status = "stopped"
            logger.error(f"Ошибка запуска сервера: {e}")
            await query.edit_message_text(
                f"❌ Ошибка запуска сервера: {e}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
    
    async def stop_server(self, query):
        """Остановить сервер"""
        if self.server_status != "running":
            await query.edit_message_text(
                "⚠️ Сервер не запущен!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
            return
        
        self.server_status = "stopping"
        await query.edit_message_text(
            "🟠 Останавливаю сервер...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
        )
        
        # Имитация остановки сервера (болванка)
        await asyncio.sleep(2)
        
        try:
            # Здесь будет реальная остановка сервера
            # if self.server_process:
            #     self.server_process.terminate()
            #     self.server_process.wait(timeout=10)
            self.server_status = "stopped"
            self.server_process = None
            await query.edit_message_text(
                "⏹️ Сервер остановлен!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
        except Exception as e:
            self.server_status = "running"
            logger.error(f"Ошибка остановки сервера: {e}")
            await query.edit_message_text(
                f"❌ Ошибка остановки сервера: {e}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
            )
    
    async def restart_server(self, query):
        """Перезапустить сервер"""
        await self.stop_server(query)
        await asyncio.sleep(2)
        await self.start_server(query)
    
    async def show_monitoring(self, query):
        """Показать мониторинг системы"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        monitoring_text = f"""
📊 **Мониторинг системы**

🖥️ **CPU:** {cpu_percent}%
💾 **RAM:** {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
💿 **Диск:** {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)
⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}

🎮 **Сервер Minecraft:**
{self.get_server_info()}
        """
        
        await query.edit_message_text(
            monitoring_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]),
            parse_mode='Markdown'
        )
    
    async def show_settings(self, query):
        """Показать настройки"""
        settings_text = f"""
⚙️ **Настройки сервера**

📁 **JAR файл:** {self.config['server']['jar_path']}
💾 **RAM:** {self.config['server']['min_ram']} - {self.config['server']['max_ram']}
🌐 **Порт:** {self.config['server']['port']}
🗺️ **Мир:** {self.config['server']['world_name']}
🔄 **Автоперезапуск:** {'✅' if self.config['server']['auto_restart'] else '❌'}
        """
        
        await query.edit_message_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]),
            parse_mode='Markdown'
        )
    
    def get_uptime(self):
        """Получить время работы сервера"""
        if not self.server_process:
            return "Не запущен"
        # Здесь будет расчет времени работы
        return "00:00:00"
    
    def get_server_info(self):
        """Получить информацию о сервере"""
        if self.server_status == "running":
            return f"🟢 Работает (PID: {self.server_process.pid if self.server_process else 'N/A'})"
        elif self.server_status == "starting":
            return "🟡 Запускается..."
        elif self.server_status == "stopping":
            return "🟠 Останавливается..."
        else:
            return "🔴 Остановлен"

async def main():
    """Основная функция"""
    try:
        bot = MineServBot()
        
        # Создание приложения
        application = Application.builder().token(bot.config['bot_token']).build()
        
        # Добавление обработчиков
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CallbackQueryHandler(bot.button_handler))
        
        # Запуск бота
        logger.info("MineServ Bot запущен")
        logger.info(f"Токен: {bot.config['bot_token'][:10]}...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка в main(): {e}")
        raise

if __name__ == '__main__':
    import sys

    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Если цикл уже работает (Termux/Cursor/встроенные среды) — обходим
        if "event loop is already running" in str(e):
            print("Цикл уже запущен, fallback: прямой await")
            try:
                # Попробуем использовать nest_asyncio если доступен
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main())
            except ImportError:
                # Если nest_asyncio нет, используем старый fallback
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(main())
                except Exception as e2:
                    print(f"Ошибка fallback: {e2}")
                    # Последняя попытка - запустить в отдельном потоке
                    import threading
                    def run_bot():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(main())
                    
                    thread = threading.Thread(target=run_bot)
                    thread.start()
                    thread.join()
        else:
            raise e 