#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import subprocess
import psutil
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
        logging.FileHandler('manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.config = self.load_config()
        self.bot_processes = {}
        self.restart_attempts = {}
        
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Файл config.json не найден!")
            return {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if update.effective_user.id not in self.config.get('admin_ids', []):
            await update.message.reply_text("⛔ У вас нет доступа к этому боту!")
            return
            
        keyboard = [
            [InlineKeyboardButton("📊 Статус ботов", callback_data='status')],
            [InlineKeyboardButton("▶️ Запустить всех", callback_data='start_all')],
            [InlineKeyboardButton("⏹️ Остановить всех", callback_data='stop_all')],
            [InlineKeyboardButton("🔄 Перезапустить всех", callback_data='restart_all')],
            [InlineKeyboardButton("📱 Система", callback_data='system')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Менеджер ботов**\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'status':
            await self.show_status(query)
        elif query.data == 'start_all':
            await self.start_all_bots(query)
        elif query.data == 'stop_all':
            await self.stop_all_bots(query)
        elif query.data == 'restart_all':
            await self.restart_all_bots(query)
        elif query.data == 'system':
            await self.show_system_info(query)
        elif query.data.startswith('bot_'):
            await self.handle_bot_action(query)
    
    async def show_status(self, query):
        """Показать статус всех ботов"""
        status_text = "📊 **Статус ботов:**\n\n"
        
        for bot_id, bot_config in self.config.get('bots', {}).items():
            is_running = bot_id in self.bot_processes and self.bot_processes[bot_id].poll() is None
            status = "🟢 Работает" if is_running else "🔴 Остановлен"
            
            keyboard = []
            if is_running:
                keyboard.append(InlineKeyboardButton("⏹️ Остановить", callback_data=f'bot_stop_{bot_id}'))
                keyboard.append(InlineKeyboardButton("🔄 Перезапустить", callback_data=f'bot_restart_{bot_id}'))
            else:
                keyboard.append(InlineKeyboardButton("▶️ Запустить", callback_data=f'bot_start_{bot_id}'))
            
            status_text += f"**{bot_config['name']}:** {status}\n"
        
        # Кнопка возврата
        keyboard = [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        reply_markup = InlineKeyboardMarkup([keyboard])
        
        await query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def start_all_bots(self, query):
        """Запустить всех ботов"""
        started_count = 0
        for bot_id in self.config.get('bots', {}):
            if await self.start_bot(bot_id):
                started_count += 1
        
        await query.edit_message_text(
            f"✅ Запущено ботов: {started_count}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
        )
    
    async def stop_all_bots(self, query):
        """Остановить всех ботов"""
        stopped_count = 0
        for bot_id in list(self.bot_processes.keys()):
            if await self.stop_bot(bot_id):
                stopped_count += 1
        
        await query.edit_message_text(
            f"⏹️ Остановлено ботов: {stopped_count}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
        )
    
    async def restart_all_bots(self, query):
        """Перезапустить всех ботов"""
        await self.stop_all_bots(query)
        await asyncio.sleep(2)
        await self.start_all_bots(query)
    
    async def show_system_info(self, query):
        """Показать информацию о системе"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = f"""
📱 **Информация о системе:**

🖥️ **CPU:** {cpu_percent}%
💾 **RAM:** {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
💿 **Диск:** {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)
⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
        """
        
        await query.edit_message_text(
            system_info,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]]),
            parse_mode='Markdown'
        )
    
    async def handle_bot_action(self, query):
        """Обработка действий с конкретным ботом"""
        action, bot_id = query.data.split('_', 2)[1:]
        
        if action == 'start':
            success = await self.start_bot(bot_id)
            message = "✅ Бот запущен!" if success else "❌ Ошибка запуска бота"
        elif action == 'stop':
            success = await self.stop_bot(bot_id)
            message = "⏹️ Бот остановлен!" if success else "❌ Ошибка остановки бота"
        elif action == 'restart':
            success = await self.restart_bot(bot_id)
            message = "🔄 Бот перезапущен!" if success else "❌ Ошибка перезапуска бота"
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='status')]])
        )
    
    async def start_bot(self, bot_id):
        """Запустить конкретного бота"""
        try:
            bot_config = self.config['bots'][bot_id]
            if bot_id in self.bot_processes and self.bot_processes[bot_id].poll() is None:
                logger.info(f"Бот {bot_id} уже запущен")
                return True
            
            process = subprocess.Popen(
                ['python', bot_config['path']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.bot_processes[bot_id] = process
            logger.info(f"Бот {bot_id} запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска бота {bot_id}: {e}")
            return False
    
    async def stop_bot(self, bot_id):
        """Остановить конкретного бота"""
        try:
            if bot_id in self.bot_processes:
                process = self.bot_processes[bot_id]
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                del self.bot_processes[bot_id]
                logger.info(f"Бот {bot_id} остановлен")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка остановки бота {bot_id}: {e}")
            return False
    
    async def restart_bot(self, bot_id):
        """Перезапустить конкретного бота"""
        await self.stop_bot(bot_id)
        await asyncio.sleep(2)
        return await self.start_bot(bot_id)

async def main():
    """Основная функция"""
    manager = BotManager()
    
    # Создание приложения
    application = Application.builder().token(manager.config['bot_token']).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", manager.start_command))
    application.add_handler(CallbackQueryHandler(manager.button_handler))
    
    # Запуск бота
    logger.info("Менеджер ботов запущен")
    await application.run_polling()

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