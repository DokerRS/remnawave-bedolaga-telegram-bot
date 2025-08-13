# 🤖 Remnawave Bedolaga Bot

<div align="center">

[![Docker Image](https://img.shields.io/badge/Docker-fr1ngg/remnawave--bedolaga--telegram--bot-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/fr1ngg/remnawave-bedolaga-telegram-bot)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Fr1ngg/remnawave-bedolaga-telegram-bot?style=social)](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/stargazers)

![Logo](./assets/logo2.svg)

**Современный Telegram-бот для управления VPN подписками через Remnawave API**

*Полнофункциональное решение с управлением пользователями, платежами и администрированием*

[🚀 Быстрый старт](#-быстрый-старт) • [📖 Документация](#-документация) • [💬 Поддержка](#-поддержка) • [🤝 Вклад](#-вклад-в-проект)

</div>

---

## ✨ Основные возможности

<table>
<tr>
<td width="50%">

### 👤 **Для пользователей**
- 💰 **Управление балансом** - Telegram Stars + YooKassa + P2P через поддержку
- 🛒 **Покупка подписок** - различные тарифы с настройкой squad
- 📱 **Управление подписками** - просмотр, продление, ссылки
- 🎁 **Промокоды** - денежные бонусы
- 👥 **Реферальная программа** - зарабатывай с друзей
- 🎰 **Игра удачи** - ежедневные бонусы
- 🆓 **Тестовая подписка** - бесплатная пробная версия
- ♾️ **Автопродление** - настраиваемое автообновление
- 🌐 **Мультиязычность** - русский и английский

</td>
<td width="50%">

### ⚙️ **Для администраторов**
- 📊 **Детальная статистика** - пользователи, платежи, подписки
- 👥 **Управление пользователями** - поиск, редактирование, баланс
- 💳 **Управление платежами** - одобрение, история, Telegram Stars
- 🎫 **Управление промокодами** - создание, статистика, массовые операции
- 🖥 **Мониторинг системы** - состояние нод, синхронизация с Remnawave
- 📨 **Рассылки** - уведомления пользователям
- 🔍 **Мониторинг подписок** - автоуведомления об истечении
- 📋 **Правила сервиса** - настройка через админ-панель
- ♾️ **Статистика автопродления** - полный контроль

</td>
</tr>
</table>

---

## 🚀 Быстрый старт

### ⚡ Автоматическая установка (Ubuntu)

Установите бота **одной командой** с интерактивным мастером настройки:

```bash
curl -sSL https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/raw/main/bedolaga.sh | sudo bash
```

<details>
<summary>🔧 Что делает установщик</summary>

- ✅ Обновляет систему Ubuntu
- ✅ Устанавливает Docker и зависимости  
- ✅ Создает структуру проекта в `/opt/bedolaga-bot`
- ✅ Интерактивная настройка всех параметров
- ✅ Создает systemd службу (опционально)
- ✅ Запускает удобное меню управления

</details>

### 🎛 Интерактивное меню управления

После установки вы получаете полнофункциональное меню:

<img width="500" alt="Интерфейс управления ботом" src="https://github.com/user-attachments/assets/9ab876f5-2758-4c52-93dd-6c9c654a07aa">

**Доступные действия:**
- 🚀 Запуск/остановка/перезапуск бота
- 📺 Просмотр логов в реальном времени
- 💾 Создание и восстановление резервных копий БД
- ✏️ Редактирование конфигурации
- 🩺 Диагностика и устранение проблем
- 🔄 Автообновление бота

---

## 📖 Документация

### 🎯 Варианты установки

<table>
<tr>
<th>Сценарий</th>
<th>Описание</th>
<th>Команда</th>
</tr>
<tr>
<td>🏠 <strong>Локальная установка</strong></td>
<td>Панель + бот на одном сервере</td>
<td><code>./bedolaga.sh</code> → вариант 2</td>
</tr>
<tr>
<td>🌐 <strong>Удаленная установка</strong></td>
<td>Бот отдельно от панели</td>
<td><code>./bedolaga.sh</code> → вариант 1</td>
</tr>
<tr>
<td>⚡ <strong>Расширенная</strong></td>
<td>С Redis и Nginx</td>
<td><code>./bedolaga.sh</code> → вариант 3</td>
</tr>
</table>

### ⚙️ Ключевые настройки

<details>
<summary>📋 Основные параметры</summary>

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) | `123456:ABC-DEF...` |
| `BOT_USERNAME` | Username бота (без @) | `your_bot` |
| `REMNAWAVE_URL` | URL панели Remnawave | `https://panel.com` |
| `REMNAWAVE_TOKEN` | API токен панели | `your_api_token` |
| `ADMIN_IDS` | ID администраторов | `123456789,987654321` |

</details>

<details>
<summary>🎁 Реферальная программа</summary>

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `REFERRAL_FIRST_REWARD` | Награда за первого реферала | `100.0` |
| `REFERRAL_REFERRED_BONUS` | Бонус приглашенному | `100.0` |
| `REFERRAL_THRESHOLD` | Порог активации (руб.) | `200.0` |
| `REFERRAL_PERCENTAGE` | % с последующих платежей | `0.2` (20%) |

</details>

<details>
<summary>⭐ Telegram Stars</summary>

| Переменная | Описание | Пример |
|------------|----------|---------|
| `STARS_ENABLED` | Включить оплату звездами | `true` |
| `STARS_100_RATE` | Курс 100 звезд → рублей | `110` |
| `STARS_250_RATE` | Курс 250 звезд → рублей | `280` |
| `STARS_500_RATE` | Курс 500 звезд → рублей | `550` |

</details>

<details>
<summary>💳 YooKassa</summary>

| Переменная | Описание | Пример |
|------------|----------|---------|
| `YOOKASSA_ENABLED` | Включить оплату через YooKassa | `true` |
| `YOOKASSA_SHOP_ID` | ID магазина в YooKassa | `123456` |
| `YOOKASSA_SECRET_KEY` | Секретный ключ API | `test_...` |
| `YOOKASSA_WEBHOOK_SECRET` | Секрет для webhook'ов | `webhook_secret` |
| `YOOKASSA_PAYMENT_METHODS` | Доступные способы оплаты | `bank_card,sbp,yoo_money` |

**Поддерживаемые способы оплаты:**
- 💳 **Банковские карты** - Visa, MasterCard, МИР
- 🏦 **СБП** - Система быстрых платежей  
- 💰 **ЮMoney** - кошелек ЮMoney
- 💵 **Наличные** - оплата наличными

[📖 Подробная настройка YooKassa](YOOKASSA_SETUP.md)

</details>

<details>
<summary>🔍 Мониторинг подписок</summary>

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `MONITOR_ENABLED` | Включить мониторинг | `true` |
| `MONITOR_CHECK_INTERVAL` | Интервал проверки (сек) | `1800` (30 мин) |
| `MONITOR_WARNING_DAYS` | За сколько дней предупреждать | `3` |
| `AUTO_DELETE_ENABLED` | Автоудаление истекших | `true` |

</details>

<details>
<summary> Триал</summary>

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TRIAL_ENABLED` | Включить триал | `true` |
| `TRIAL_DURATION_DAYS` | Дней триала | `3` |
| `TRIAL_SQUAD_UUID` | Сквад триальной подписки | `` |
| `TRIAL_NOTIFICATION_ENABLED` | Уведомление об истечении триал подписки | `true` |
| `TRIAL_NOTIFICATION_HOURS_AFTER` | Через сколько отсылать сообщение  | `1` |
| `TRIAL_NOTIFICATION_HOURS_WINDOW` | Через сколько выслать повторно  | `` |

</details>
### 🐳 Docker Compose примеры

<details>
<summary>🏠 Для локальной установки (панель + бот)</summary>

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: remnawave_bot_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: remnawave_bot
      POSTGRES_USER: remnawave_user
      POSTGRES_PASSWORD: secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - remnawave-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U remnawave_user -d remnawave_bot"]

  bot:
    image: fr1ngg/remnawave-bedolaga-telegram-bot:latest
    container_name: remnawave_bot
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://remnawave_user:secure_password_123@postgres:5432/remnawave_bot
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - remnawave-network

volumes:
  postgres_data:

networks:
  remnawave-network:
    name: remnawave-network
    external: true
```

</details>

<details>
<summary>🌐 Для удаленной установки</summary>

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: remnawave_bot_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: remnawave_bot
      POSTGRES_USER: remnawave_user
      POSTGRES_PASSWORD: secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bot_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U remnawave_user -d remnawave_bot"]

  bot:
    image: fr1ngg/remnawave-bedolaga-telegram-bot:latest
    container_name: remnawave_bot
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://remnawave_user:secure_password_123@postgres:5432/remnawave_bot
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - bot_network

volumes:
  postgres_data:

networks:
  bot_network:
    driver: bridge
```

</details>

---

## 🎯 Использование

### 👤 Для пользователей

1. **Запуск** → Найдите бота и нажмите `/start`
2. **Язык** → Выберите русский или английский  
3. **Баланс** → "💰 Баланс" → "💳 Пополнить" → Telegram Stars
4. **Подписка** → "🛒 Купить подписку" → выбор тарифа → оплата
5. **Управление** → "📋 Мои подписки" → выбор → получение ссылки
6. **Рефералы** → "👥 Рефералы" → поделиться ссылкой

### ⚙️ Для администраторов

Доступ через кнопку **"⚙️ Админ панель"**:

- **📦 Управление подписками** → создание и настройка тарифов
- **👥 Управление пользователями** → поиск, редактирование балансов
- **💰 Управление платежами** → одобрение Telegram Stars платежей
- **🎁 Промокоды** → создание денежных бонусов
- **📨 Рассылки** → уведомления пользователям
- **🖥 Система Remnawave** → мониторинг нод, синхронизация
- **📊 Статистика** → подробная аналитика

---

## 📊 Производительность

### 💪 Рекомендуемые ресурсы

| Пользователей | RAM | CPU | Диск | Описание |
|---------------|-----|-----|------|----------|
| **До 500** | 1GB | 1 vCPU | 10GB | Начальная конфигурация |
| **До 1,000** | 2GB | 1 vCPU | 20GB | Малый бизнес |
| **До 10,000** | 4GB | 2 vCPU | 50GB | Средний бизнес |
| **До 50,000** | 8GB | 4 vCPU | 100GB | Крупный бизнес |

### ⚡ Оптимизация

- **Redis** → включите для кэширования (`--profile with-redis`)
- **PostgreSQL** → настройте для production нагрузок
- **Nginx** → используйте как reverse proxy (`--profile with-nginx`)
- **Мониторинг** → отслеживайте через `docker stats`

---

## 🔧 Управление

### 📋 Основные команды

```bash
# Переход в директорию
cd /opt/bedolaga-bot

# Управление через Docker Compose
docker compose up -d           # Запуск
docker compose down            # Остановка  
docker compose restart bot     # Перезапуск бота
docker compose logs -f bot     # Логи в реальном времени

# Управление через systemd (если настроено)
sudo systemctl start bedolaga-bot
sudo systemctl stop bedolaga-bot
sudo systemctl restart bedolaga-bot
```

### 🔄 Обновление

```bash
# Автоматическое через меню
sudo ./bedolaga.sh

# Ручное обновление
docker compose down
docker compose pull bot
docker compose up -d
```

### 💾 Резервное копирование

```bash
# Создание backup
docker exec remnawave_bot_db pg_dump -U remnawave_user remnawave_bot > backup.sql

# Восстановление
docker exec -i remnawave_bot_db psql -U remnawave_user remnawave_bot < backup.sql
```

---

## 🐛 Устранение неполадок

### ❓ Частые проблемы

<details>
<summary>🤖 Бот не отвечает</summary>

**Проверьте:**
- ✅ Правильность `BOT_TOKEN`
- ✅ Интернет соединение
- ✅ Логи: `docker compose logs bot`

**Решение:**
```bash
# Перезапуск бота
docker compose restart bot

# Проверка токена
docker exec remnawave_bot env | grep BOT_TOKEN
```

</details>

<details>
<summary>🗄️ Ошибки базы данных</summary>

**Симптомы:**
- SQL ошибки в логах
- Бот не сохраняет данные

**Решение:**
```bash
# Проверка PostgreSQL
docker compose logs postgres

# Подключение к БД
docker exec -it remnawave_bot_db psql -U remnawave_user remnawave_bot

# Экстренное восстановление через меню
sudo ./bedolaga.sh → "10) Экстренное исправление БД"
```

</details>

<details>
<summary>🔌 Проблемы с Remnawave API</summary>

**Проверьте:**
- ✅ Доступность `REMNAWAVE_URL`
- ✅ Валидность `REMNAWAVE_TOKEN`
- ✅ Сетевое подключение

**Диагностика:**
```bash
# Проверка URL
curl -I https://your-panel.com

# Тест API из контейнера
docker exec remnawave_bot curl -I http://remnawave:3000
```

</details>

<details>
<summary>⚠️ Проблема обновления 1.3.3 → 1.3.4</summary>

**Симптом:** SQL ошибки после обновления связанные с автоплатежами

**Решение через меню:**
```bash
sudo ./bedolaga.sh
# Выберите: "10) Экстренное исправление БД (Python)"
# Или: "11) Экстренное исправление БД (SQL)"
```

**Ручное решение:**
1. Скачайте `emergency_fix.py`
2. Добавьте в `docker-compose.yml`:
```yaml
emergency-fix:
  image: fr1ngg/remnawave-bedolaga-telegram-bot:latest
  volumes:
    - ./emergency_fix.py:/app/emergency_fix.py
  environment:
    - DATABASE_URL=postgresql+asyncpg://remnawave_user:secure_password_123@postgres:5432/remnawave_bot
  networks:
    - bot_network
  profiles:
    - emergency
  command: python emergency_fix.py
```
3. Запустите: `docker compose run --rm emergency-fix`

</details>

---

## 🗺️ Roadmap

### ✅ Реализовано

- ✅ **Мониторинг подписок** - автоуведомления и контроль
- ✅ **Telegram Stars** - пополнение баланса звездами  
- ✅ **Синхронизация Remnawave** - импорт пользователей и статистика
- ✅ **Реферальная система** - полнофункциональная программа
- ✅ **Игра удачи** - ежедневные розыгрыши бонусов
- ✅ **Управление промокодами** - создание, редактирование, статистика
- ✅ **Правила сервиса** - настройка через админ-панель
- ✅ **Автоплатежи** - настраиваемое автопродление подписок
- ✅ **Просмотр подписок пользователей** - детальная статистика

### 🎯 В планах

| Версия | Функция | Приоритет | Описание |
|--------|---------|-----------|----------|
| **v1.4.0** | ЮKassa интеграция | 🔴 High | Автоматические платежи |
| **v1.4.0** | Веб-панель управления | 🟡 Medium | Полный веб-интерфейс |
| **v1.4.0** | Безопасное удаление | 🟡 Medium | Архивирование вместо удаления |
| **v1.5.0** | Дополнительные платежи | 🟡 Medium | Сбербанк, Tinkoff, Crypto |
| **v1.5.0** | Уведомления | 🟡 Medium | Webhook, Email, другие чаты |
| **v1.6.0** | Система блокировок | 🟢 Low | Бан/разбан пользователей |

### 💡 Хотите добавить функцию?

- 🐛 [Сообщите о баге](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/issues)
- ✨ [Предложите улучшение](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/discussions)
- 🔧 [Создайте Pull Request](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/pulls)

---

## 🤝 Вклад в проект

### 💪 Как помочь

**🔧 Разработчикам:**
- Fork репозитория
- Создайте feature branch: `git checkout -b feature/amazing-feature`
- Внесите изменения и сделайте commit: `git commit -m 'Add amazing feature'`
- Push в branch: `git push origin feature/amazing-feature`
- Создайте Pull Request

**🐞 Пользователям:**
- Сообщайте о багах в [Issues](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/issues)
- Предлагайте идеи в [Discussions](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/discussions)
- Ставьте ⭐ проекту
- Рассказывайте друзьям

**💰 Спонсорам:**
- Поддержите разработку
- Закажите приоритетные функции
- Получите корпоративную поддержку

---

## 💬 Поддержка

### 📞 Контакты

- **Telegram:** [@fringg](https://t.me/fringg)
- **Issues:** [GitHub Issues](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Fr1ngg/remnawave-bedolaga-telegram-bot/discussions)

### 📚 Полезные ссылки

- [📖 Документация Remnawave](https://docs.remna.st)
- [🤖 Создание Telegram бота](https://t.me/BotFather)
- [🐳 Docker документация](https://docs.docker.com)
- [🐘 PostgreSQL документация](https://www.postgresql.org/docs)

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT**. Подробности в файле [LICENSE](LICENSE).

---

<div align="center">

### 🌟 Понравился проект? Поставьте звезду!

[![Star History Chart](https://api.star-history.com/svg?repos=Fr1ngg/remnawave-bedolaga-telegram-bot&type=Date)](https://star-history.com/#Fr1ngg/remnawave-bedolaga-telegram-bot&Date)

---

**💝 Создано с любовью для Remnawave сообщества**

*Автор не является профессиональным разработчиком, но прикладывает все усилия для создания удобного бота для ваших сервисов* 💪

[🔝 Вернуться наверх](#-remnawave-bedolaga-bot)

</div>
