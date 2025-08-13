import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from lucky_game import lucky_game_router
from stars_handlers import stars_router
from yookassa_handlers import yookassa_router
from autopay_service import AutoPayService
from webhook_integration import YooKassaWebhookServer

print("🚀 Запуск бота...")
print(f"📍 Рабочая директория: {os.getcwd()}")
print(f"📁 Файлы в директории: {os.listdir('.')}")

if os.path.exists('.env'):
    print("✅ Файл .env найден")
else:
    print("❌ Файл .env НЕ НАЙДЕН!")
    print("💡 Создайте файл .env в корне проекта")

from config import load_config, debug_environment
from database import Database
from remnawave_api import RemnaWaveAPI
from subscription_monitor import create_subscription_monitor
from middlewares import DatabaseMiddleware, UserMiddleware, LoggingMiddleware, ThrottlingMiddleware, WorkflowDataMiddleware, BotMiddleware
from handlers import router
from admin_handlers import admin_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BotApplication:
    
    def __init__(self):
        self.config = None
        self.db = None
        self.api = None
        self.bot = None
        self.dp = None
        self.monitor_service = None
        self.autopay_service = None
        self.webhook_server = None

    async def _init_autopay_service(self):
        """Инициализирует сервис автоплатежей"""
        try:
            logger.info("🔧 Initializing autopay service...")
            
            if not self.bot:
                logger.error("❌ Bot instance is None, cannot initialize autopay")
                return
            
            if not self.db:
                logger.error("❌ Database instance is None, cannot initialize autopay")
                return
            
            self.autopay_service = AutoPayService(self.db, self.api, self.bot)
            
            self.dp.workflow_data["autopay_service"] = self.autopay_service
            logger.info("✅ Autopay service added to workflow_data")
            
            logger.info("🚀 Starting autopay service...")
            await self.autopay_service.start()
            
            status = await self.autopay_service.get_service_status()
            if status['is_running']:
                logger.info("✅ Autopay service started successfully")
                logger.info(f"📊 Autopay status: interval=30min")
            else:
                logger.warning("⚠️ Autopay service created but not running")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize autopay service: {e}", exc_info=True)
            logger.warning("⚠️ Continuing without autopay service")
            self.autopay_service = None
    
    async def _init_webhook_server(self):
        """Инициализирует webhook сервер для YooKassa"""
        try:
            logger.info("🔧 Initializing YooKassa webhook server...")
            
            if not self.config.YOOKASSA_ENABLED:
                logger.info("⚠️ YooKassa webhook server disabled (YOOKASSA_ENABLED=False)")
                return
            
            if not self.config.YOOKASSA_SHOP_ID or not self.config.YOOKASSA_SECRET_KEY:
                logger.warning("⚠️ YooKassa webhook server disabled (missing credentials)")
                return
            
            # Создаем webhook сервер
            self.webhook_server = YooKassaWebhookServer(self.config, self.db, self.bot)
            
            # Запускаем webhook сервер
            await self.webhook_server.start()
            
            if self.webhook_server.is_running:
                logger.info("✅ YooKassa webhook server started successfully")
                logger.info(f"📊 Webhook server status: {self.webhook_server.get_status()}")
            else:
                logger.warning("⚠️ YooKassa webhook server created but not running")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize YooKassa webhook server: {e}", exc_info=True)
            logger.warning("⚠️ Continuing without YooKassa webhook server")
            self.webhook_server = None
        
    async def initialize(self):
        
        debug_environment()
        
        self.config = load_config()
        
        print(f"🔧 Загруженная конфигурация:")
        print(f"   BOT_USERNAME: '{self.config.BOT_USERNAME}'")
        print(f"   REFERRAL_FIRST_REWARD: {self.config.REFERRAL_FIRST_REWARD}")
        print(f"   ADMIN_IDS: {self.config.ADMIN_IDS}")
        
        if not self.config.BOT_TOKEN:
            logger.error("BOT_TOKEN is required")
            raise ValueError("BOT_TOKEN is required")
        
        if not self.config.REMNAWAVE_URL or not self.config.REMNAWAVE_TOKEN:
            logger.error("REMNAWAVE_URL and REMNAWAVE_TOKEN are required")
            raise ValueError("REMNAWAVE_URL and REMNAWAVE_TOKEN are required")
        
        if not self.config.BOT_USERNAME:
            logger.warning("⚠️  BOT_USERNAME не установлен! Реферальные ссылки работать не будут!")
            print("💡 Добавьте BOT_USERNAME=your_bot_username в .env файл")
        
        logger.info("Starting RemnaWave Bot...")
        logger.info(f"RemnaWave URL: {self.config.REMNAWAVE_URL}")
        logger.info(f"Admin IDs: {self.config.ADMIN_IDS}")
        logger.info(f"Bot Username: {self.config.BOT_USERNAME}")
        
        self.db = Database(self.config.DATABASE_URL)
        await self._init_database()
        
        self.api = RemnaWaveAPI(
            self.config.REMNAWAVE_URL, 
            self.config.REMNAWAVE_TOKEN, 
            self.config.SUBSCRIPTION_BASE_URL
        )
        logger.info("RemnaWave API initialized")
        
        await self._test_api_connection()
        
        self.bot = Bot(
            token=self.config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        await self._test_bot_token()
        
        self._setup_dispatcher()
        
        await self._init_monitor_service()
        await self._init_autopay_service()
        await self._init_webhook_server()

        if self.config.STARS_ENABLED:
            logger.info("✅ Telegram Stars пополнение включено")
            logger.info(f"📊 Настроенные курсы: {self.config.STARS_RATES}")
        
            if not self.config.STARS_RATES or len(self.config.STARS_RATES) == 0:
                logger.warning("⚠️  STARS_RATES пустые! Telegram Stars будут недоступны")
                self.config.STARS_ENABLED = False
            else:
                valid_rates = all(
                    isinstance(stars, int) and isinstance(rubles, (int, float)) and stars > 0 and rubles > 0
                    for stars, rubles in self.config.STARS_RATES.items()
                )
                if not valid_rates:
                    logger.warning("⚠️  Неверные STARS_RATES! Telegram Stars будут недоступны")
                    self.config.STARS_ENABLED = False
        else:
            logger.info("❌ Telegram Stars пополнение отключено")
        
    async def _init_database(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.db.init_db()
                logger.info("Database initialized successfully")
                break
            except Exception as e:
                logger.error(f"Database initialization attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("Failed to initialize database after all retries")
                    raise
                await asyncio.sleep(2)
                
    async def _test_api_connection(self):
        try:
            system_stats = await self.api.get_system_stats()
            if system_stats:
                logger.info("RemnaWave API connection successful")
            else:
                logger.warning("RemnaWave API connection test failed - continuing anyway")
        except Exception as e:
            logger.warning(f"RemnaWave API connection error: {e} - continuing anyway")
            
    async def _test_bot_token(self):
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot started: @{bot_info.username} ({bot_info.first_name})")
            
            if not self.config.BOT_USERNAME and bot_info.username:
                self.config.BOT_USERNAME = bot_info.username
                logger.info(f"✅ BOT_USERNAME автоматически установлен: {bot_info.username}")
                print("💡 Добавьте BOT_USERNAME в .env файл для постоянного сохранения")
            
        except Exception as e:
            logger.error(f"Invalid bot token or network error: {e}")
            raise
            
    def _setup_dispatcher(self):
        storage = MemoryStorage()
        self.dp = Dispatcher(storage=storage)
        
        self.dp.workflow_data.update({
            "config": self.config,
            "api": self.api,
            "db": self.db,
            "monitor_service": None
        })
        
        self.dp.message.middleware(LoggingMiddleware())
        self.dp.callback_query.middleware(LoggingMiddleware())
        
        self.dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
        self.dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
        
        self.dp.message.middleware(WorkflowDataMiddleware())
        self.dp.callback_query.middleware(WorkflowDataMiddleware())
        
        self.dp.message.middleware(BotMiddleware(self.bot))
        self.dp.callback_query.middleware(BotMiddleware(self.bot))
        
        self.dp.message.middleware(DatabaseMiddleware(self.db))
        self.dp.callback_query.middleware(DatabaseMiddleware(self.db))
        
        self.dp.message.middleware(UserMiddleware(self.db, self.config))
        self.dp.callback_query.middleware(UserMiddleware(self.db, self.config))
        
        self.dp.include_router(router)
        self.dp.include_router(admin_router)
        self.dp.include_router(lucky_game_router)
        self.dp.include_router(stars_router)
        self.dp.include_router(yookassa_router)
        
    async def _init_monitor_service(self):
        try:
            logger.info("🔧 Initializing subscription monitor service...")
        
            if not self.bot:
                logger.error("❌ Bot instance is None, cannot initialize monitor")
                return
            
            if not self.db:
                logger.error("❌ Database instance is None, cannot initialize monitor")
                return
            
            if not self.config:
                logger.error("❌ Config instance is None, cannot initialize monitor")
                return
        
            self.monitor_service = await create_subscription_monitor(
                self.bot, self.db, self.config, self.api
            )
        
            if not self.monitor_service:
                logger.error("❌ Failed to create monitor service instance")
                return
        
            self.dp.workflow_data["monitor_service"] = self.monitor_service
            logger.info("✅ Monitor service added to workflow_data")
        
            logger.info("🚀 Starting monitor service...")
            await self.monitor_service.start()
        
            status = await self.monitor_service.get_service_status()
            if status['is_running']:
                logger.info("✅ Subscription monitor service started successfully")
                logger.info(f"📊 Monitor status: interval={status['check_interval']}s, daily_hour={status['daily_check_hour']}, warning_days={status['warning_days']}")
            else:
                logger.warning("⚠️ Monitor service created but not running")
                logger.warning(f"📊 Monitor status: {status}")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitor service: {e}", exc_info=True)
            logger.warning("⚠️ Continuing without monitor service")
            self.monitor_service = None
            
    async def start(self):
        logger.info("Bot polling started successfully")
        
        if self.config.BOT_USERNAME:
            logger.info(f"🎁 Реферальная система активна! Ссылки: https://t.me/{self.config.BOT_USERNAME}?start=ref_USERID")
        else:
            logger.warning("⚠️  Реферальная система неактивна! Установите BOT_USERNAME")
        
        if self.webhook_server and self.webhook_server.is_running:
            logger.info(f"🔗 YooKassa webhook server активен на порту 8000")
            logger.info(f"📡 Webhook URL: http://your-domain:8000/webhook/yookassa")
        else:
            logger.info("⚠️  YooKassa webhook server неактивен")
        
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
        finally:
            await self.shutdown()
            
    async def shutdown(self):
        logger.info("Shutting down bot...")

        if self.autopay_service: 
            try:
                await self.autopay_service.stop()
                logger.info("Autopay service stopped")
            except Exception as e:
                logger.error(f"Error stopping autopay service: {e}")
        
        if self.webhook_server:
            try:
                await self.webhook_server.stop()
                logger.info("YooKassa webhook server stopped")
            except Exception as e:
                logger.error(f"Error stopping YooKassa webhook server: {e}")
        
        if self.monitor_service:
            try:
                await self.monitor_service.stop()
                logger.info("Monitor service stopped")
            except Exception as e:
                logger.error(f"Error stopping monitor service: {e}")
        
        if self.api:
            try:
                await self.api.close()
                logger.info("API connection closed")
            except Exception as e:
                logger.error(f"Error closing API: {e}")
        
        if self.db:
            try:
                await self.db.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database: {e}")
        
        if self.bot:
            try:
                await self.bot.session.close()
                logger.info("Bot session closed")
            except Exception as e:
                logger.error(f"Error closing bot session: {e}")
        
        logger.info("Bot shutdown complete")

async def main():
    app = None
    try:
        app = BotApplication()
        await app.initialize()
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if app:
            await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
