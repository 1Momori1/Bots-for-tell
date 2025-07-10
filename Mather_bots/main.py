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

import sys
import traceback

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
        
        await self.show_main_menu(update.message)
    
    async def show_main_menu(self, message_or_query):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("📊 Статус ботов", callback_data='status')],
            [InlineKeyboardButton("▶️ Запустить всех", callback_data='start_all')],
            [InlineKeyboardButton("⏹️ Остановить всех", callback_data='stop_all')],
            [InlineKeyboardButton("🔄 Перезапустить всех", callback_data='restart_all')],
            [InlineKeyboardButton("📱 Система", callback_data='system')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "🤖 **Менеджер ботов**\n\nВыберите действие:"
        # Корректно обновляем меню
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
        elif query.data == 'back_to_main':
            await self.show_main_menu(query)
        elif query.data.startswith('bot_'):
            await self.handle_bot_action(query, context)
    
    async def show_status(self, query):
        """Показать статус всех ботов с кнопками управления под каждым ботом"""
        status_text = "📊 **Статус ботов:**\n\n"
        keyboard = []
        for bot_id, bot_config in self.config.get('bots', {}).items():
            is_running = bot_id in self.bot_processes and self.bot_processes[bot_id].poll() is None
            status = "🟢 Работает" if is_running else "🔴 Остановлен"
            status_text += f"**{bot_config['name']}:** {status}\n"
            row = []
            if is_running:
                row.append(InlineKeyboardButton("⏹️ Остановить", callback_data=f'bot_stop_{bot_id}'))
                row.append(InlineKeyboardButton("🔄 Перезапустить", callback_data=f'bot_restart_{bot_id}'))
            else:
                row.append(InlineKeyboardButton("▶️ Запустить", callback_data=f'bot_start_{bot_id}'))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def start_all_bots(self, query):
        """Запустить всех ботов"""
        started_count = 0
        failed_bots = []
        
        for bot_id, bot_config in self.config.get('bots', {}).items():
            if not bot_config.get('enabled', True):
                continue
                
            success, error = await self.start_bot(bot_id)
            if success:
                started_count += 1
            else:
                failed_bots.append(f"{bot_config['name']}: {error}")
        
        message = f"✅ Запущено ботов: {started_count}"
        if failed_bots:
            message += f"\n❌ Ошибки:\n" + "\n".join(failed_bots)
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
        )
    
    async def stop_all_bots(self, query):
        """Остановить всех ботов"""
        stopped_count = 0
        for bot_id in list(self.bot_processes.keys()):
            success, _ = await self.stop_bot(bot_id)
            if success:
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
    
    async def handle_bot_action(self, query, context):
        """Обработка действий с конкретным ботом"""
        action, bot_id = query.data.split('_', 2)[1:]
        error_message = None
        if action == 'start':
            success, error_message = await self.start_bot(bot_id, context)
        elif action == 'stop':
            success, error_message = await self.stop_bot(bot_id, context)
        elif action == 'restart':
            success, error_message = await self.restart_bot(bot_id, context)
        # После действия возвращаемся к статусу
        await self.show_status(query)
        # Если была ошибка — отправляем админу
        if error_message:
            for admin_id in self.config.get('admin_ids', []):
                await context.bot.send_message(admin_id, f"Ошибка: {error_message}")

    async def start_bot(self, bot_id, context=None):
        """Запустить конкретного бота универсально"""
        import os, sys
        try:
            bot_config = self.config['bots'][bot_id]
            
            # Проверяем, не запущен ли уже бот
            if bot_id in self.bot_processes and self.bot_processes[bot_id].poll() is None:
                logger.info(f"Бот {bot_id} уже запущен")
                return True, "Уже запущен"
            
            # Получаем абсолютный путь к файлу бота
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bot_path = os.path.abspath(os.path.join(current_dir, bot_config['path']))
            
            if not os.path.exists(bot_path):
                error = f"Файл бота не найден: {bot_path}"
                logger.error(error)
                return False, error
            
            # Проверяем, что файл является Python скриптом
            if not bot_path.endswith('.py'):
                error = f"Файл не является Python скриптом: {bot_path}"
                logger.error(error)
                return False, error
            
            # Используем sys.executable для универсального запуска
            python_exec = sys.executable
            
            # Запускаем процесс в зависимости от ОС
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    [python_exec, bot_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Linux/Android (Termux)
                process = subprocess.Popen(
                    [python_exec, bot_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Проверяем, что процесс запустился успешно
            if process.poll() is not None:
                error = f"Процесс завершился сразу после запуска"
                logger.error(f"Ошибка запуска бота {bot_id}: {error}")
                return False, error
            
            self.bot_processes[bot_id] = process
            logger.info(f"Бот {bot_id} запущен (PID: {process.pid})")
            return True, None
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота {bot_id}: {e}")
            return False, str(e)
    
    async def stop_bot(self, bot_id, context=None):
        try:
            if bot_id in self.bot_processes:
                process = self.bot_processes[bot_id]
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                del self.bot_processes[bot_id]
                logger.info(f"Бот {bot_id} остановлен")
                return True, None
            return False, "Процесс не найден"
        except Exception as e:
            logger.error(f"Ошибка остановки бота {bot_id}: {e}")
            return False, str(e)
    
    async def restart_bot(self, bot_id, context=None):
        await self.stop_bot(bot_id, context)
        await asyncio.sleep(2)
        return await self.start_bot(bot_id, context)

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