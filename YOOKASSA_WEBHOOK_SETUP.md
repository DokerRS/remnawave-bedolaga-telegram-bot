# 🚀 Настройка Webhook для YooKassa

## 📋 Что такое Webhook?

Webhook - это автоматическое уведомление от YooKassa о статусе платежей. Когда пользователь оплачивает счет, YooKassa отправляет уведомление на ваш сервер, и бот автоматически обновляет статус платежа и зачисляет средства на баланс.

## 🔧 Настройка в YooKassa

### 1. В личном кабинете YooKassa:
- Перейдите в **Настройки** → **Уведомления**
- В поле **Webhook URL** введите: `http://your-domain:8000/webhook/yookassa`
- Убедитесь, что включены уведомления для:
  - ✅ `payment.succeeded` (платеж успешно завершен)
  - ✅ `payment.canceled` (платеж отменен)
  - ✅ `payment.waiting_for_capture` (платеж ожидает подтверждения)

### 2. Настройте переменные окружения:
В файле `.env` добавьте:
```bash
YOOKASSA_ENABLED=true
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
YOOKASSA_WEBHOOK_SECRET=your_webhook_secret

# Для тестирования можно временно отключить проверку подписи:
# YOOKASSA_SKIP_SIGNATURE_VERIFICATION=true
```

## 🌐 Webhook URL для разных сценариев

### Для локального тестирования:
```
http://localhost:8000/webhook/yookassa
```

### Для Docker (локально):
```
http://localhost:8000/webhook/yookassa
```

### Для продакшена (с доменом):
```
https://yourdomain.com/webhook/yookassa
```

### Для тестирования с ngrok:
```
https://abc123.ngrok.io/webhook/yookassa
```

## 📡 Endpoints Webhook сервера

После запуска бота webhook сервер будет доступен по следующим адресам:

- **Webhook endpoint**: `POST /webhook/yookassa` - основной endpoint для YooKassa
- **Health check**: `GET /health` - проверка здоровья сервера
- **Status**: `GET /webhook/yookassa/status` - статус webhook сервера

## 🚀 Запуск

### 1. Пересоберите Docker контейнер:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 2. Проверьте логи:
В логах должно появиться:
```
✅ YooKassa webhook server started at http://0.0.0.0:8000
🔗 Webhook endpoint: http://0.0.0.0:8000/webhook/yookassa
📊 Health check: http://0.0.0.0:8000/health
📈 Status: http://0.0.0.0:8000/webhook/yookassa/status
```

## 🧪 Тестирование

### 1. Проверьте статус webhook сервера:
```bash
curl http://localhost:8000/webhook/yookassa/status
```

### 2. Проверьте health check:
```bash
curl http://localhost:8000/health
```

### 3. Создайте тестовый платеж через бота и проверьте логи

## 🔒 Безопасность

- Webhook сервер проверяет подпись от YooKassa
- Используйте HTTPS в продакшене
- Настройте firewall для ограничения доступа к порту 8000
- Регулярно обновляйте `YOOKASSA_WEBHOOK_SECRET`

## ❗ Устранение проблем

### Webhook сервер не запускается:
1. Проверьте переменные окружения
2. Убедитесь, что порт 8000 свободен
3. Проверьте логи на ошибки

### Webhook не приходят:
1. Проверьте URL в настройках YooKassa
2. Убедитесь, что сервер доступен из интернета
3. Проверьте firewall и настройки сети

### Ошибки подписи:
1. Проверьте `YOOKASSA_WEBHOOK_SECRET`
2. Убедитесь, что webhook отправляется от YooKassa
3. Проверьте формат данных webhook
4. Для тестирования временно отключите проверку подписи:
   ```bash
   YOOKASSA_SKIP_SIGNATURE_VERIFICATION=true
   ```
5. Проверьте логи на детальную информацию о проверке подписи

## 📚 Дополнительная информация

- [Документация YooKassa по webhook](https://yookassa.ru/developers/using-api/webhooks)
- [Примеры webhook обработчиков](https://github.com/yoomoney/yookassa-python-sdk)
- [Тестирование webhook](https://yookassa.ru/developers/using-api/webhooks#test-webhook)
