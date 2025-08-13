"""
Простой webhook сервер для тестирования интеграции с YooKassa
Запускайте только для тестирования, не используйте в продакшене!
"""

import asyncio
import logging
import json
from aiohttp import web, ClientSession
from yookassa_service import YooKassaService
from database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация (замените на ваши данные)
YOOKASSA_SHOP_ID = "your_shop_id"
YOOKASSA_SECRET_KEY = "your_secret_key"
DATABASE_URL = "sqlite+aiosqlite:///bot.db"

async def yookassa_webhook_handler(request):
    """Обработчик webhook'ов от YooKassa"""
    try:
        # Получаем тело запроса
        body = await request.text()
        signature = request.headers.get('Signature', request.headers.get('X-YooKassa-Signature', ''))
        
        logger.info(f"Received webhook: {body[:200]}...")
        logger.info(f"Signature: {signature}")
        
        # Создаем сервис YooKassa
        yookassa_service = YooKassaService(
            shop_id=YOOKASSA_SHOP_ID,
            secret_key=YOOKASSA_SECRET_KEY
        )
        
        # Проверяем подпись
        if not yookassa_service.verify_webhook_signature(body, signature):
            logger.error("Invalid webhook signature")
            return web.Response(status=400, text="Invalid signature")
        
        # Парсим данные webhook'а
        webhook_data = yookassa_service.parse_webhook_data(body)
        if not webhook_data:
            logger.error("Failed to parse webhook data")
            return web.Response(status=400, text="Invalid webhook data")
        
        logger.info(f"Webhook data: {webhook_data}")
        
        # Здесь можно добавить обработку webhook'а
        # Например, обновить статус платежа в базе данных
        
        return web.Response(status=200, text="OK")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return web.Response(status=500, text="Internal error")

async def health_check(request):
    """Проверка здоровья сервера"""
    return web.Response(text="OK")

async def create_test_payment(request):
    """Создание тестового платежа"""
    try:
        data = await request.json()
        amount = data.get('amount', 100.0)
        
        yookassa_service = YooKassaService(
            shop_id=YOOKASSA_SHOP_ID,
            secret_key=YOOKASSA_SECRET_KEY
        )
        
        from yookassa_service import YooKassaPaymentData
        
        payment_data = YooKassaPaymentData(
            amount=amount,
            description=f"Тестовый платеж на {amount}₽",
            metadata={'test': True}
        )
        
        payment_result = await yookassa_service.create_payment(payment_data)
        
        return web.json_response({
            'success': True,
            'payment': payment_result
        })
        
    except Exception as e:
        logger.error(f"Error creating test payment: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def create_app():
    """Создает и настраивает приложение"""
    app = web.Application()
    
    # Добавляем маршруты
    app.router.add_post('/webhook/yookassa', yookassa_webhook_handler)
    app.router.add_get('/health', health_check)
    app.router.add_post('/test-payment', create_test_payment)
    
    return app

async def main():
    """Главная функция"""
    app = create_app()
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    
    logger.info("Webhook server started at http://localhost:8000")
    logger.info("Webhook endpoint: http://localhost:8000/webhook/yookassa")
    logger.info("Health check: http://localhost:8000/health")
    logger.info("Test payment: POST http://localhost:8000/test-payment")
    
    try:
        await asyncio.Future()  # Бесконечный цикл
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    # Проверяем конфигурацию
    if YOOKASSA_SHOP_ID == "your_shop_id":
        logger.error("Please configure YooKassa credentials in webhook_server.py")
        exit(1)
    
    asyncio.run(main())
