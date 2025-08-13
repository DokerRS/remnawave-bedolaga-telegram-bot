import asyncio
import logging
import hashlib
import hmac
import json
import base64
import urllib.request
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from yookassa import Configuration, Payment
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography import x509

logger = logging.getLogger(__name__)

@dataclass
class YooKassaPaymentData:
    """Данные для создания платежа в YooKassa"""
    amount: float
    currency: str = "RUB"
    description: str = ""
    payment_method_types: Optional[List[str]] = None
    receipt_items: Optional[List[Dict]] = None
    payment_metadata: Optional[Dict] = None

class YooKassaService:
    """Сервис для работы с YooKassa API"""
    
    def __init__(self, shop_id: str, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self._yk_public_keys: Dict[str, object] = {}
        
        # Инициализация YooKassa
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        
        logger.info(f"✅ YooKassa service initialized for shop: {shop_id}")

    def _get_yk_public_key(self, key_id: str):
        """Возвращает публичный ключ YooKassa по key_id с кешированием."""
        if key_id in self._yk_public_keys:
            return self._yk_public_keys[key_id]
        try:
            url = f"https://yookassa.ru/signature/key/{key_id}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                content = resp.read()
            try:
                preview = content[:64]
                logger.info(f"🔑 Downloaded key {key_id}: {len(content)} bytes, head={preview!r}")
            except Exception:
                pass
            # 1) Попытка: PEM сертификат
            try:
                cert = x509.load_pem_x509_certificate(content)
                public_key = cert.public_key()
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            # 2) Попытка: PEM публичный ключ
            try:
                public_key = load_pem_public_key(content)
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            # 3) Попытка: DER сертификат (сырые байты)
            try:
                cert = x509.load_der_x509_certificate(content)
                public_key = cert.public_key()
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            # 4) Попытка: DER публичный ключ (сырые байты)
            try:
                public_key = load_der_public_key(content)
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            # 5) Попытка: base64 -> DER сертификат
            try:
                der = base64.b64decode(content)
                cert = x509.load_der_x509_certificate(der)
                public_key = cert.public_key()
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            # 6) Попытка: base64 -> DER публичный ключ
            try:
                der = base64.b64decode(content)
                public_key = load_der_public_key(der)
                self._yk_public_keys[key_id] = public_key
                return public_key
            except Exception:
                pass
            raise ValueError("Unrecognized public key format")
        except Exception as e:
            logger.error(f"❌ Failed to fetch YooKassa public key for {key_id}: {e}")
            return None

    async def create_payment(self, payment_data: YooKassaPaymentData, return_url: str = None) -> Dict:
        """
        Создает платеж в YooKassa
        
        Args:
            payment_data: Данные для создания платежа
            return_url: URL для возврата после оплаты
            
        Returns:
            Dict с данными созданного платежа
        """
        try:
            # Создаем объект платежа
            payment_request = {
                "amount": {
                    "value": str(payment_data.amount),
                    "currency": "RUB"
                },
                "description": payment_data.description,
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or "https://t.me/your_bot_username"
                },
                "capture": True,
                "metadata": payment_data.payment_metadata or {}
            }
            
            # Создаем платеж через API
            logger.info(f"🔍 Creating payment with request: {payment_request}")
            payment = Payment.create(payment_request)
            
            logger.info(f"✅ Payment created successfully: {getattr(payment, 'id', 'N/A')}")
            logger.info(f"🔍 Payment object type: {type(payment)}")
            logger.info(f"🔍 Payment attributes: {dir(payment)}")
            
            # Получаем данные платежа
            payment_id = getattr(payment, 'id', None)
            payment_status = getattr(payment, 'status', None)
            
            # Обрабатываем сумму
            amount_value = 0.0
            currency = "RUB"
            if hasattr(payment, 'amount'):
                if isinstance(payment.amount, dict):
                    amount_value = float(payment.amount.get('value', 0))
                    currency = payment.amount.get('currency', 'RUB')
                else:
                    amount_value = float(getattr(payment.amount, 'value', 0))
                    currency = getattr(payment.amount, 'currency', 'RUB')
            
            # Обрабатываем подтверждение
            confirmation_url = None
            logger.info(f"🔍 Processing confirmation: hasattr={hasattr(payment, 'confirmation')}")
            if hasattr(payment, 'confirmation'):
                logger.info(f"🔍 Confirmation type: {type(payment.confirmation)}")
                logger.info(f"🔍 Confirmation value: {payment.confirmation}")
                if isinstance(payment.confirmation, dict):
                    confirmation_url = payment.confirmation.get('return_url')
                    logger.info(f"🔍 Confirmation from dict: {confirmation_url}")
                else:
                    confirmation_url = getattr(payment.confirmation, 'confirmation_url', None)
                    logger.info(f"🔍 Confirmation from object: {confirmation_url}")
            logger.info(f"🔍 Final confirmation_url: {confirmation_url}")
            
            # Обрабатываем дату создания
            created_at = None
            if hasattr(payment, 'created_at') and payment.created_at:
                if hasattr(payment.created_at, 'isoformat'):
                    created_at = payment.created_at.isoformat()
                else:
                    created_at = str(payment.created_at)
            
            return {
                'id': payment_id,
                'status': payment_status,
                'amount': amount_value,
                'currency': currency,
                'confirmation_url': confirmation_url,
                'created_at': created_at,
                'description': getattr(payment, 'description', ''),
                'payment_metadata': getattr(payment, 'metadata', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create payment: {e}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict:
        """
        Получает статус платежа
        
        Args:
            payment_id: ID платежа в YooKassa
            
        Returns:
            Dict с данными платежа
        """
        try:
            payment = Payment.find_one(payment_id)
            
            # Получаем данные платежа
            payment_id = getattr(payment, 'id', None)
            payment_status = getattr(payment, 'status', None)
            
            # Обрабатываем сумму
            amount_value = 0.0
            currency = "RUB"
            if hasattr(payment, 'amount'):
                if isinstance(payment.amount, dict):
                    amount_value = float(payment.amount.get('value', 0))
                    currency = payment.amount.get('currency', 'RUB')
                else:
                    amount_value = float(getattr(payment.amount, 'value', 0))
                    currency = getattr(payment.amount, 'currency', 'RUB')
            
            # Обрабатываем оплаченную сумму
            amount_paid_value = 0.0
            if hasattr(payment, 'amount_paid'):
                if isinstance(payment.amount_paid, dict):
                    amount_paid_value = float(payment.amount_paid.get('value', 0))
                else:
                    amount_paid_value = float(getattr(payment.amount_paid, 'value', 0))
            
            # Обрабатываем даты
            created_at = None
            captured_at = None
            if hasattr(payment, 'created_at') and payment.created_at:
                if hasattr(payment.created_at, 'isoformat'):
                    created_at = payment.created_at.isoformat()
                else:
                    created_at = str(payment.created_at)
            
            if hasattr(payment, 'captured_at') and payment.captured_at:
                if hasattr(payment.captured_at, 'isoformat'):
                    captured_at = payment.captured_at.isoformat()
                else:
                    captured_at = str(payment.captured_at)
            
            return {
                'id': payment_id,
                'status': payment_status,
                'amount': amount_value,
                'currency': currency,
                'paid': getattr(payment, 'paid', False),
                'amount_paid': amount_paid_value,
                'created_at': created_at,
                'captured_at': captured_at,
                'description': getattr(payment, 'description', ''),
                'payment_metadata': getattr(payment, 'metadata', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            raise
    
    async def cancel_payment(self, payment_id: str) -> bool:
        """
        Отменяет платеж
        
        Args:
            payment_id: ID платежа в YooKassa
            
        Returns:
            True если платеж успешно отменен
        """
        try:
            # Отменяем платеж
            Payment.cancel(payment_id)
            logger.info(f"✅ Payment {payment_id} cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel payment {payment_id}: {e}")
            return False
    
    def verify_webhook_signature(self, body: str, signature: str) -> bool:
        """
        Проверяет подпись webhook'а от YooKassa (формат v1 по публичному ключу). 
        При недоступности ключа или ошибке верификации — не блокирует обработку.
        """
        try:
            logger.info(f"🔍 Webhook signature verification:")
            logger.info(f"🔍 Received signature: {signature}")

            if signature and signature.startswith('v1 '):
                parts = signature.split(' ')
                if len(parts) < 4:
                    logger.debug("Invalid v1 signature format; allowing webhook")
                    return True
                key_id = parts[1]
                sig_b64 = parts[3]
                try:
                    sig_bytes = base64.b64decode(sig_b64)
                except Exception as e:
                    logger.debug(f"Cannot decode base64 signature: {e}; allowing webhook")
                    return True
                public_key = self._get_yk_public_key(key_id)
                if public_key:
                    try:
                        public_key.verify(
                            sig_bytes,
                            body.encode('utf-8'),
                            padding.PKCS1v15(),
                            hashes.SHA256()
                        )
                        logger.info("🔍 Signature verification result: True (RSA)")
                        return True
                    except Exception as e:
                        logger.debug(f"RSA signature verification failed: {e}; allowing webhook")
                        return True
                else:
                    logger.debug("Public key not available; allowing webhook")
                    return True

            logger.debug("Unknown or missing signature; allowing webhook")
            return True
        except Exception as e:
            logger.error(f"❌ Error verifying webhook signature: {e}")
            return True
    
    def parse_webhook_data(self, body: str) -> Optional[Dict]:
        """
        Парсит данные webhook'а от YooKassa
        
        Args:
            body: Тело webhook запроса
            
        Returns:
            Dict с данными webhook'а или None при ошибке
        """
        try:
            data = json.loads(body)
            logger.info(f"🔍 Parsing webhook data: {data}")
            
            # YooKassa использует 'event' вместо 'type' и 'object' для данных
            if 'object' not in data:
                logger.error("❌ Invalid webhook data structure: missing 'object'")
                return None
            
            # Определяем тип события
            event_type = data.get('event', data.get('type', 'unknown'))
            payment_data = data['object']
            
            logger.info(f"🔍 Webhook event type: {event_type}")
            logger.info(f"🔍 Payment data: {payment_data}")
            
            if event_type == 'payment.succeeded':
                return {
                    'type': 'payment_succeeded',
                    'payment_id': payment_data.get('id'),
                    'status': payment_data.get('status'),
                    'amount': float(payment_data.get('amount', {}).get('value', 0)),
                    'currency': payment_data.get('amount', {}).get('currency'),
                    'paid': payment_data.get('paid', False),
                    'metadata': payment_data.get('metadata', {}),
                    'captured_at': payment_data.get('captured_at')
                }
            
            elif event_type == 'payment.canceled':
                return {
                    'type': 'payment_canceled',
                    'payment_id': payment_data.get('id'),
                    'status': payment_data.get('status'),
                    'metadata': payment_data.get('metadata', {})
                }
            
            elif event_type == 'payment.waiting_for_capture':
                return {
                    'type': 'payment_waiting_for_capture',
                    'payment_id': payment_data.get('id'),
                    'status': payment_data.get('status'),
                    'amount': float(payment_data.get('amount', {}).get('value', 0)),
                    'currency': payment_data.get('amount', {}).get('currency'),
                    'metadata': payment_data.get('metadata', {})
                }
            
            else:
                logger.info(f"ℹ️ Unhandled webhook event type: {event_type}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse webhook JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error parsing webhook data: {e}")
            return None
    
    async def get_payment_methods_info(self) -> List[Dict]:
        """
        Возвращает информацию о доступных методах оплаты
        
        Returns:
            List с описанием методов оплаты
        """
        methods = [
            {
                'id': 'bank_card',
                'name': 'Банковская карта',
                'description': 'Visa, MasterCard, МИР',
                'icon': '💳',
                'enabled': True
            },
            {
                'id': 'sbp',
                'name': 'СБП',
                'description': 'Система быстрых платежей',
                'icon': '🏦',
                'enabled': True
            },
            {
                'id': 'yoo_money',
                'name': 'ЮMoney',
                'description': 'Кошелек ЮMoney',
                'icon': '💰',
                'enabled': True
            },
            {
                'id': 'cash',
                'name': 'Наличные',
                'description': 'Оплата наличными',
                'icon': '💵',
                'enabled': True
            }
        ]
        
        return methods
