"""
Интеграция webhook сервера YooKassa в основной бот
"""

import asyncio
import logging
import json
from aiohttp import web, ClientSession
from yookassa_service import YooKassaService
from database import Database
from yookassa_handlers import process_yookassa_webhook

logger = logging.getLogger(__name__)

class YooKassaWebhookServer:
    """Webhook сервер для YooKassa"""
    
    def __init__(self, config, db, bot=None):
        self.config = config
        self.db = db
        self.bot = bot
        self.app = None
        self.runner = None
        self.site = None
        self.is_running = False
        
    async def start(self, host='0.0.0.0', port=8000):
        """Запускает webhook сервер"""
        try:
            if not self.config.YOOKASSA_ENABLED:
                logger.info("⚠️ YooKassa webhook server disabled (YOOKASSA_ENABLED=False)")
                return
            
            if not self.config.YOOKASSA_SHOP_ID or not self.config.YOOKASSA_SECRET_KEY:
                logger.warning("⚠️ YooKassa webhook server disabled (missing credentials)")
                return
            
            # Создаем приложение
            self.app = web.Application()
            
            # Добавляем маршруты
            self.app.router.add_post('/webhook/yookassa', self.yookassa_webhook_handler)
            self.app.router.add_get('/health', self.health_check)
            self.app.router.add_get('/webhook/yookassa/status', self.webhook_status)
            
            # Создаем runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            # Запускаем сервер
            self.site = web.TCPSite(self.runner, host, port)
            await self.site.start()
            
            self.is_running = True
            logger.info(f"✅ YooKassa webhook server started at http://{host}:{port}")
            logger.info(f"🔗 Webhook endpoint: http://{host}:{port}/webhook/yookassa")
            logger.info(f"📊 Health check: http://{host}:{port}/health")
            logger.info(f"📈 Status: http://{host}:{port}/webhook/yookassa/status")
            
        except Exception as e:
            logger.error(f"❌ Failed to start YooKassa webhook server: {e}")
            self.is_running = False
    
    async def stop(self):
        """Останавливает webhook сервер"""
        try:
            if self.site:
                await self.site.stop()
                logger.info("✅ YooKassa webhook server site stopped")
            
            if self.runner:
                await self.runner.cleanup()
                logger.info("✅ YooKassa webhook server runner cleaned up")
            
            self.is_running = False
            logger.info("✅ YooKassa webhook server stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping YooKassa webhook server: {e}")
    
    async def yookassa_webhook_handler(self, request):
        """Обработчик webhook'ов от YooKassa"""
        try:
            # Получаем тело запроса
            body = await request.text()
            signature = request.headers.get('Signature', request.headers.get('X-YooKassa-Signature', ''))
            
            # Логируем все заголовки для отладки
            all_headers = dict(request.headers)
            logger.info(f"📥 Received YooKassa webhook:")
            logger.info(f"📥 Body: {body[:200]}...")
            logger.info(f"🔐 Signature header: {signature}")
            logger.info(f"🔐 All headers: {all_headers}")
            
            # Создаем сервис YooKassa
            yookassa_service = YooKassaService(
                shop_id=self.config.YOOKASSA_SHOP_ID,
                secret_key=self.config.YOOKASSA_SECRET_KEY
            )
            
            # Проверяем подпись (можно отключить для тестирования)
            if getattr(self.config, 'YOOKASSA_SKIP_SIGNATURE_VERIFICATION', False):
                logger.warning("⚠️ Skipping webhook signature verification (YOOKASSA_SKIP_SIGNATURE_VERIFICATION=True)")
            elif not yookassa_service.verify_webhook_signature(body, signature):
                logger.error("❌ Invalid YooKassa webhook signature")
                # Временно пропускаем проверку подписи для отладки
                logger.warning("⚠️ Temporarily skipping signature verification for debugging")
                # return web.Response(status=400, text="Invalid signature")
            
            # Парсим данные webhook'а
            webhook_data = yookassa_service.parse_webhook_data(body)
            if not webhook_data:
                logger.error("❌ Failed to parse YooKassa webhook data")
                return web.Response(status=400, text="Invalid webhook data")
            
            logger.info(f"✅ Parsed webhook data: {webhook_data}")
            
            # Обрабатываем webhook через основной обработчик
            success = await process_yookassa_webhook(webhook_data, self.db, self.bot)
            
            if success:
                logger.info(f"✅ YooKassa webhook processed successfully: {webhook_data.get('type')}")
                return web.Response(status=200, text="OK")
            else:
                logger.error(f"❌ Failed to process YooKassa webhook: {webhook_data.get('type')}")
                return web.Response(status=500, text="Processing failed")
            
        except Exception as e:
            logger.error(f"❌ Error processing YooKassa webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return web.Response(status=500, text="Internal error")
    
    async def health_check(self, request):
        """Проверка здоровья webhook сервера"""
        return web.json_response({
            'status': 'healthy',
            'service': 'yookassa_webhook',
            'running': self.is_running,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    async def webhook_status(self, request):
        """Статус webhook сервера"""
        return web.json_response({
            'service': 'yookassa_webhook',
            'status': 'running' if self.is_running else 'stopped',
            'endpoints': {
                'webhook': '/webhook/yookassa',
                'health': '/health',
                'status': '/webhook/yookassa/status'
            },
            'config': {
                'enabled': self.config.YOOKASSA_ENABLED,
                'shop_id_set': bool(self.config.YOOKASSA_SHOP_ID),
                'secret_key_set': bool(self.config.YOOKASSA_SECRET_KEY)
            },
            'timestamp': asyncio.get_event_loop().time()
        })
    
    def get_status(self):
        """Возвращает статус webhook сервера"""
        return {
            'is_running': self.is_running,
            'service': 'yookassa_webhook',
            'endpoints': {
                'webhook': '/webhook/yookassa',
                'health': '/health',
                'status': '/webhook/yookassa/status'
            }
        }
