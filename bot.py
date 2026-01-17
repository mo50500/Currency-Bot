import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, FIAT_CURRENCIES, CRYPTO_CURRENCIES, ALL_CURRENCIES
from currency_api import CurrencyAPI

# Состояния пользователей
user_states = {}

class UserState:
    def __init__(self):
        self.from_currency = None
        self.to_currency = None
        self.step = 'select_from'  # 'select_from', 'select_to'

def create_currency_keyboard(currencies: dict, callback_prefix: str):
    """Создать клавиатуру с валютами"""
    keyboard = []
    row = []
    
    for code, name in currencies.items():
        button = InlineKeyboardButton(f"{name} ({code})", callback_data=f"{callback_prefix}_{code}")
        row.append(button)
        
        if len(row) == 2:  # Две кнопки в ряду
            keyboard.append(row)
            row = []
    
    if row:  # Добавить оставшиеся кнопки
        keyboard.append(row)
    
    # Добавить кнопку "Назад"
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(keyboard)

def create_main_keyboard():
    """Создать главную клавиатуру"""
    keyboard = [
        [InlineKeyboardButton("💱 Узнать курс", callback_data="start_exchange")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_states[user_id] = UserState()
    
    welcome_text = """
👋 Добро пожаловать в **Currency Bot**!

Этот бот поможет вам узнать актуальные курсы валют и криптовалют.

💡 **Как использовать:**
1. Нажмите "💱 Узнать курс"
2. Выберите валюту, которую хотите конвертировать
3. Выберите валюту, в которую хотите конвертировать
4. Получите актуальный курс!

🔄 Поддерживаются:
- Фиатные валюты (USD, EUR, RUB и др.)
- Криптовалюты (BTC, ETH, USDT и др.)
- Конвертация между любыми валютами

Начните работу, нажав кнопку ниже! 👇
    """
    
    await update.message.reply_text(welcome_text, reply_markup=create_main_keyboard(), parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = UserState()
    
    state = user_states[user_id]
    data = query.data
    
    if data == "start_exchange":
        state = UserState()
        user_states[user_id] = state
        
        text = "📊 **Выберите валюту, которую хотите конвертировать:**"
        await query.edit_message_text(text, reply_markup=create_currency_keyboard(ALL_CURRENCIES, "from"), parse_mode='Markdown')
    
    elif data == "about":
        text = """
ℹ️ **О боте Currency Bot**

🤖 **Версия:** 1.0
📊 **Функции:**
- Получение актуальных курсов валют
- Поддержка фиатных валют и криптовалют
- Конвертация между любыми валютами
- Удобный интерфейс с кнопками

📡 **Данные:** Курсы обновляются в реальном времени через CoinGecko API
        """
        await query.edit_message_text(text, reply_markup=create_main_keyboard(), parse_mode='Markdown')
    
    elif data == "back":
        text = "🏠 **Главное меню:**"
        await query.edit_message_text(text, reply_markup=create_main_keyboard(), parse_mode='Markdown')
    
    elif data.startswith("from_"):
        from_currency = data.split("_")[1]
        state.from_currency = from_currency
        state.step = 'select_to'
        
        from_name = ALL_CURRENCIES.get(from_currency, from_currency)
        text = f"💰 **Выбрано:** {from_name} ({from_currency})\n\n📊 **Теперь выберите валюту, в которую хотите конвертировать:**"
        await query.edit_message_text(text, reply_markup=create_currency_keyboard(ALL_CURRENCIES, "to"), parse_mode='Markdown')
    
    elif data.startswith("to_"):
        to_currency = data.split("_")[1]
        state.to_currency = to_currency
        
        # Показываем загрузку
        await query.edit_message_text("⏳ Получение актуального курса...")
        
        # Получаем курс
        async with CurrencyAPI() as api:
            rate = await api.get_exchange_rate(state.from_currency, to_currency)
        
        from_name = ALL_CURRENCIES.get(state.from_currency, state.from_currency)
        to_name = ALL_CURRENCIES.get(to_currency, to_currency)
        
        if rate is not None:
            if rate < 0.0001:
                rate_str = f"{rate:.8f}"
            elif rate < 1:
                rate_str = f"{rate:.6f}"
            else:
                rate_str = f"{rate:.4f}"
            
            # Дополнительная информация
            inverse_rate = 1 / rate if rate > 0 else 0
            if inverse_rate < 0.0001:
                inverse_str = f"{inverse_rate:.8f}"
            elif inverse_rate < 1:
                inverse_str = f"{inverse_rate:.6f}"
            else:
                inverse_str = f"{inverse_rate:.4f}"
            
            text = f"""💱 **Курс обмена**

{from_name} ({state.from_currency}) → {to_name} ({to_currency})

**1 {state.from_currency} = {rate_str} {to_currency}**
**1 {to_currency} = {inverse_str} {state.from_currency}**

📊 *Данные актуальны на момент запроса*
            """
        else:
            text = f"❌ **Ошибка:** Не удалось получить курс для {from_name} → {to_name}\n\nПопробуйте выбрать другие валюты."
        
        keyboard = [
            [InlineKeyboardButton("🔄 Новый обмен", callback_data="start_exchange")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

def main():
    """Основная функция запуска бота"""
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Бот запускается...")
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
