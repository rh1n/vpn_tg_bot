# VPN Telegram Bot

Telegram бот для продажи VPN-доступа через Telegram Stars.

## Описание

Этот бот позволяет пользователям:
- Покупать VPN-ключи через Telegram Stars
- Управлять своими подписками
- Продлевать доступ
- Получать инструкции по настройке

## Требования

- Docker и docker-compose
- Telegram бот (получить через @BotFather)
- 3x-ui панель с включенным API

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repo-url>
   cd vpn-bot

Сделайте скрипт развертывания исполняемым:

bash
chmod +x deploy.sh
Запустите скрипт развертывания:

bash
./deploy.sh
При первом запуске скрипт создаст файл .env из .env.example. Отредактируйте его с вашими данными и запустите скрипт снова.

Настройка 3x-ui
Установите 3x-ui панель по инструкции: https://github.com/MHSanaei/3x-ui

Включите API в настройках панели:

Перейдите в Settings → API
Включите API
Установите порт (по умолчанию 54321)
Создайте inbound для VLESS Reality:

Перейдите в Inbounds
Добавьте новый inbound
Выберите протокол VLESS
Настройте Reality
Запомните ID inbound'а для конфигурации бота
Настройка Telegram Stars
Откройте @BotFather в Telegram
Выберите вашего бота
Перейдите в Bot Settings → Payments
Включите Telegram Stars как способ оплаты
Переменные окружения
Переменная	Описание
BOT_TOKEN	Токен Telegram бота
POSTGRES_DSN	Строка подключения к PostgreSQL
PANEL_URL	URL панели 3x-ui
PANEL_USERNAME	Имя пользователя администратора панели
PANEL_PASSWORD	Пароль администратора панели
PANEL_INBOUND_ID	ID inbound для создания ключей
ADMIN_IDS	Список Telegram ID администраторов через запятую
SUPPORT_USERNAME	Юзернейм поддержки
LOCALE_DEFAULT	Язык по умолчанию (ru или en)
STARS_PRICE	Стоимость подписки в звездах
Использование клиента Happ
Для подключения через Happ:

Скачайте приложение Happ (iOS/Android/PC)
Импортируйте конфигурацию по ссылке
Настройки подключения:
Включите Fragmentation (Фрагментирование)
Включите Noise (Шумы)
Включите Routing (Маршрутизация)
Выберите правило "Ru-Direct" (появляется автоматически после импорта подписки)
Нажмите кнопку подключения
Команды бота
/start - Главное меню
/admin - Админ-панель (только для администраторов)
