from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
import logging
from typing import Dict

from database import Database, User
from keyboards import balance_keyboard, topup_keyboard, cancel_keyboard, yookassa_payment_link_keyboard
from translations import t
from utils import log_user_action
from yookassa_service import YooKassaService, YooKassaPaymentData
from referral_utils import process_referral_rewards

logger = logging.getLogger(__name__)

yookassa_router = Router()

class YooKassaTopupStates(StatesGroup):
    """Состояния для пополнения через YooKassa"""
    waiting_for_amount = State()

@yookassa_router.callback_query(F.data == "cancel")
async def cancel_yookassa_callback(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Обработчик кнопки отмены для YooKassa"""
    user = kwargs.get('user')
    
    logger.info(f"🔍 cancel_yookassa_callback: user={user is not None}")
    
    if not user:
        await callback.answer("❌ Ошибка пользователя")
        return
    
    # Сбрасываем состояние
    await state.clear()
    
    # Возвращаемся в меню баланса
    await callback.message.edit_text(
        t('balance', user.language),
        reply_markup=balance_keyboard(user.language)
    )

@yookassa_router.callback_query(F.data == "topup_yookassa")
async def topup_yookassa_callback(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Обработчик кнопки пополнения через YooKassa"""
    user = kwargs.get('user')
    config = kwargs.get('config')
    
    logger.info(f"🔍 topup_yookassa_callback: user={user is not None}, config={config is not None}")
    if config:
        logger.info(f"🔍 topup_yookassa_callback: YOOKASSA_ENABLED={config.YOOKASSA_ENABLED}")
        logger.info(f"🔍 topup_yookassa_callback: YOOKASSA_SHOP_ID={'SET' if config.YOOKASSA_SHOP_ID else 'NOT SET'}")
        logger.info(f"🔍 topup_yookassa_callback: YOOKASSA_SECRET_KEY={'SET' if config.YOOKASSA_SECRET_KEY else 'NOT SET'}")
    
    if not user:
        await callback.answer("❌ Ошибка пользователя")
        return
    
    if not config or not config.YOOKASSA_ENABLED:
        await callback.message.edit_text(
            "❌ Пополнение через YooKassa временно недоступно",
            reply_markup=balance_keyboard(user.language)
        )
        return
    
    if not config.YOOKASSA_SHOP_ID or not config.YOOKASSA_SECRET_KEY:
        await callback.message.edit_text(
            "❌ Сервис YooKassa не настроен",
            reply_markup=balance_keyboard(user.language)
        )
        return
    
    text = "💳 **Пополнение через YooKassa**\n\n"
    text += "🚀 **Преимущества:**\n"
    text += "• Безопасные платежи\n"
    text += "• Множество способов оплаты\n"
    text += "• Мгновенное зачисление\n"
    text += "• Поддержка всех банков\n\n"
    
    text += "💎 **Доступные способы оплаты:**\n"
    text += "• 💳 Банковские карты (Visa, MasterCard, МИР)\n"
    text += "• 🏦 СБП (Система быстрых платежей)\n"
    text += "• 💰 ЮMoney кошелек\n"
    text += "• 💵 Наличные\n\n"
    
    text += "💰 **Введите сумму для пополнения (руб.):**"
    
    # Переходим в состояние ожидания суммы
    await state.set_state(YooKassaTopupStates.waiting_for_amount)
    
    # Показываем сообщение с инструкцией и клавиатурой для отмены
    await callback.message.edit_text(
        text,
        reply_markup=cancel_keyboard(user.language),
        parse_mode='Markdown'
    )

@yookassa_router.message(YooKassaTopupStates.waiting_for_amount)
async def process_yookassa_amount(message: Message, state: FSMContext, **kwargs):
    """Обработчик введенной суммы для YooKassa"""
    user = kwargs.get('user')
    config = kwargs.get('config')
    db = kwargs.get('db')
    
    logger.info(f"🔍 process_yookassa_amount: user={user is not None}, config={config is not None}, db={db is not None}")
    logger.info(f"🔍 process_yookassa_amount: message.text='{message.text}'")
    
    if not user or not config or not db:
        logger.error(f"❌ process_yookassa_amount: Missing required data - user={user is not None}, config={config is not None}, db={db is not None}")
        await message.answer("❌ Ошибка пользователя")
        return
    
    try:
        amount = float(message.text)
        
        # Проверяем минимальную и максимальную сумму
        if amount < 1:
            await message.answer(t('yookassa_min_amount', user.language))
            return
        
        if amount > 75000:
            await message.answer(t('yookassa_max_amount', user.language))
            return
        
        # Создаем платеж в YooKassa
        await message.answer(t('yookassa_processing_payment', user.language))
        
        yookassa_service = YooKassaService(
            shop_id=config.YOOKASSA_SHOP_ID,
            secret_key=config.YOOKASSA_SECRET_KEY
        )
        
        # Создаем данные для платежа
        payment_data = YooKassaPaymentData(
            amount=amount,
            description=f"Пополнение баланса на {amount:.2f}₽",
            payment_metadata={
                'user_id': user.telegram_id,
                'username': user.username,
                'payment_type': 'balance_topup'
            }
        )
        
        # Создаем платеж
        payment_result = await yookassa_service.create_payment(
            payment_data,
            return_url=f"https://t.me/{config.BOT_USERNAME}"
        )
        
        # Сохраняем платеж в базе данных
        db_payment = await db.create_yookassa_payment(
            user_id=user.telegram_id,
            yookassa_payment_id=payment_result['id'],
            amount=amount,
            description=payment_data.description,
            confirmation_url=payment_result.get('confirmation_url'),
            payment_metadata=payment_data.payment_metadata
        )
        
        # Отправляем сообщение с ссылкой на оплату
        text = f"✅ **{t('yookassa_payment_created', user.language)}**\n\n"
        text += f"💰 **Сумма:** {amount:.2f}₽\n"
        text += f"🆔 **ID платежа:** `{payment_result['id']}`\n"
        text += f"📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        if payment_result.get('confirmation_url'):
            text += f"🔗 **{t('yookassa_payment_link', user.language)}:**\n"
            text += f"`{payment_result['confirmation_url']}`\n\n"
            text += "💡 **Нажмите на ссылку выше для оплаты**\n\n"
        else:
            text += "⚠️ **Ссылка для оплаты не получена**\n\n"
        
        text += "📊 **Статус:** " + t('yookassa_payment_pending', user.language)
        
        await message.answer(
            text,
            reply_markup=(yookassa_payment_link_keyboard(payment_result['confirmation_url'], user.language) if payment_result.get('confirmation_url') else balance_keyboard(user.language)),
            parse_mode='Markdown'
        )
        
        # Логируем действие
        log_user_action(
            user_id=user.telegram_id,
            action="yookassa_payment_created",
            details=f"amount={amount}, payment_id={payment_result['id']}"
        )
        
        logger.info(f"✅ YooKassa payment flow completed successfully for user {user.telegram_id}")
        
        # Сбрасываем состояние
        await state.clear()
        
    except ValueError:
        await message.answer(
            t('yookassa_invalid_amount', user.language),
            reply_markup=cancel_keyboard(user.language)
        )
    except Exception as e:
        logger.error(f"Error creating YooKassa payment: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        await message.answer(
            t('yookassa_payment_error', user.language),
            reply_markup=cancel_keyboard(user.language)
        )
        await state.clear()

@yookassa_router.callback_query(F.data == "yookassa_payment_status")
async def yookassa_payment_status_callback(callback: CallbackQuery, **kwargs):
    """Обработчик проверки статуса платежа YooKassa"""
    user = kwargs.get('user')
    config = kwargs.get('config')
    db = kwargs.get('db')
    
    if not user or not config or not db:
        await callback.answer("❌ Ошибка пользователя")
        return
    
    # Получаем последние платежи пользователя
    payments = await db.get_user_yookassa_payments(user.telegram_id, limit=5)
    
    if not payments:
        await callback.answer("❌ У вас нет платежей через YooKassa")
        return
    
    text = "📊 **Статус платежей YooKassa:**\n\n"
    
    for payment in payments:
        status_emoji = {
            'pending': '⏳',
            'succeeded': '✅',
            'canceled': '❌',
            'waiting_for_capture': '⏸️'
        }.get(payment.status, '❓')
        
        status_text = {
            'pending': t('yookassa_payment_pending', user.language),
            'succeeded': t('yookassa_payment_success', user.language),
            'canceled': t('yookassa_payment_cancelled', user.language),
            'waiting_for_capture': 'Ожидает подтверждения'
        }.get(payment.status, payment.status)
        
        created_date = payment.created_at.strftime('%d.%m.%Y %H:%M')
        text += f"{status_emoji} **{created_date}** - {payment.amount:.2f}₽\n"
        text += f"   📊 {status_text}\n"
        text += f"   🆔 `{payment.yookassa_payment_id}`\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=balance_keyboard(user.language),
        parse_mode='Markdown'
    )

async def process_yookassa_webhook(webhook_data: Dict, db: Database, bot=None) -> bool:
    """
    Обработчик webhook'а от YooKassa
    
    Args:
        webhook_data: Данные webhook'а
        db: Экземпляр базы данных
        bot: Экземпляр бота для уведомлений
        
    Returns:
        True если webhook обработан успешно
    """
    try:
        webhook_type = webhook_data.get('type')
        payment_id = webhook_data.get('payment_id')
        
        if not payment_id:
            logger.error("❌ Webhook without payment_id")
            return False
        
        # Получаем платеж из базы данных
        payment = await db.get_yookassa_payment_by_yookassa_id(payment_id)
        if not payment:
            logger.error(f"❌ Payment {payment_id} not found in database")
            return False
        
        if webhook_type == 'payment_succeeded':
            # Платеж успешно завершен
            await db.update_yookassa_payment_status(
                payment.id, 
                'succeeded',
                completed_at=datetime.utcnow()
            )
            
            # Зачисляем средства на баланс пользователя
            await db.add_balance(payment.user_id, payment.amount)
            
            # Создаем запись о платеже
            await db.create_payment(
                user_id=payment.user_id,
                amount=payment.amount,
                payment_type='yookassa',
                description=f"Пополнение через YooKassa (ID: {payment_id})",
                status='completed'
            )
            
            # Обрабатываем реферальные награды
            await process_referral_rewards(
                user_id=payment.user_id,
                amount=payment.amount,
                payment_id=payment.id,
                db=db,
                bot=bot,
                payment_type='yookassa'
            )
            
            # Уведомляем пользователя
            if bot:
                try:
                    await bot.send_message(
                        payment.user_id,
                        f"✅ **{t('yookassa_payment_success', 'ru')}**\n\n"
                        f"💰 **Сумма:** {payment.amount:.2f}₽\n"
                        f"💳 **Способ:** YooKassa\n"
                        f"📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"🎉 **Баланс пополнен!**",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {payment.user_id}: {e}")
            
            logger.info(f"✅ Payment {payment_id} processed successfully")
            
        elif webhook_type == 'payment_canceled':
            # Платеж отменен
            await db.update_yookassa_payment_status(
                payment.id, 
                'canceled',
                cancelled_at=datetime.utcnow()
            )
            
            logger.info(f"❌ Payment {payment_id} cancelled")
            
        elif webhook_type == 'payment_waiting_for_capture':
            # Платеж ожидает подтверждения
            await db.update_yookassa_payment_status(payment.id, 'waiting_for_capture')
            logger.info(f"⏸️ Payment {payment_id} waiting for capture")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing YooKassa webhook: {e}")
        return False
