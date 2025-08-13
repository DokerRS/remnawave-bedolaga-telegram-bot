"""
Примеры использования YooKassa API
"""

import asyncio
import logging
from yookassa_service import YooKassaService, YooKassaPaymentData

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_create_payment():
    """Пример создания платежа"""
    
    # Инициализация сервиса
    yookassa_service = YooKassaService(
        shop_id="your_shop_id",
        secret_key="your_secret_key"
    )
    
    # Создание данных для платежа
    payment_data = YooKassaPaymentData(
        amount=100.0,
        description="Тестовый платеж на 100₽",
        payment_metadata={
            'user_id': 123456789,
            'username': 'test_user',
            'payment_type': 'test'
        }
    )
    
    try:
        # Создание платежа
        payment_result = await yookassa_service.create_payment(
            payment_data,
            return_url="https://t.me/your_bot_username"
        )
        
        logger.info(f"Payment created: {payment_result}")
        
        # Получение статуса платежа
        status = await yookassa_service.get_payment_status(payment_result['id'])
        logger.info(f"Payment status: {status}")
        
        return payment_result
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        return None

async def example_webhook_processing():
    """Пример обработки webhook'а"""
    
    # Имитация webhook данных от YooKassa
    webhook_body = '''
    {
        "type": "payment.succeeded",
        "object": {
            "id": "test_payment_id",
            "status": "succeeded",
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "paid": true,
            "metadata": {
                "user_id": "123456789",
                "payment_type": "test"
            }
        }
    }
    '''
    
    yookassa_service = YooKassaService(
        shop_id="your_shop_id",
        secret_key="your_secret_key"
    )
    
    # Парсинг webhook данных
    webhook_data = yookassa_service.parse_webhook_data(webhook_body)
    
    if webhook_data:
        logger.info(f"Webhook data: {webhook_data}")
        
        # Обработка в зависимости от типа
        if webhook_data['type'] == 'payment_succeeded':
            logger.info(f"Payment {webhook_data['payment_id']} succeeded")
            logger.info(f"Amount: {webhook_data['amount']} {webhook_data['currency']}")
        elif webhook_data['type'] == 'payment_canceled':
            logger.info(f"Payment {webhook_data['payment_id']} canceled")
        elif webhook_data['type'] == 'payment_waiting_for_capture':
            logger.info(f"Payment {webhook_data['payment_id']} waiting for capture")
    else:
        logger.error("Failed to parse webhook data")

async def example_payment_methods():
    """Пример получения информации о способах оплаты"""
    
    yookassa_service = YooKassaService(
        shop_id="your_shop_id",
        secret_key="your_secret_key"
    )
    
    methods = await yookassa_service.get_payment_methods_info()
    
    logger.info("Available payment methods:")
    for method in methods:
        logger.info(f"  {method['icon']} {method['name']}: {method['description']}")

async def example_cancel_payment():
    """Пример отмены платежа"""
    
    yookassa_service = YooKassaService(
        shop_id="your_shop_id",
        secret_key="your_secret_key"
    )
    
    payment_id = "test_payment_id"
    
    try:
        success = await yookassa_service.cancel_payment(payment_id)
        if success:
            logger.info(f"Payment {payment_id} cancelled successfully")
        else:
            logger.error(f"Failed to cancel payment {payment_id}")
    except Exception as e:
        logger.error(f"Error cancelling payment: {e}")

async def main():
    """Главная функция с примерами"""
    
    logger.info("🚀 Starting YooKassa examples...")
    
    # Пример создания платежа
    logger.info("\n📝 Example 1: Creating payment")
    await example_create_payment()
    
    # Пример обработки webhook'а
    logger.info("\n📝 Example 2: Processing webhook")
    await example_webhook_processing()
    
    # Пример получения способов оплаты
    logger.info("\n📝 Example 3: Payment methods")
    await example_payment_methods()
    
    # Пример отмены платежа
    logger.info("\n📝 Example 4: Cancelling payment")
    await example_cancel_payment()
    
    logger.info("\n✅ Examples completed!")

if __name__ == '__main__':
    # Проверяем конфигурацию
    if "your_shop_id" in ["your_shop_id", "your_secret_key"]:
        logger.error("Please configure YooKassa credentials in the examples")
        exit(1)
    
    asyncio.run(main())
