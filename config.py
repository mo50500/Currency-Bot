import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')

# Список популярных фиатных валют
FIAT_CURRENCIES = {
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'RUB': '🇷🇺 Российский рубль',
    'GBP': '🇬🇧 Британский фунт',
    'JPY': '🇯🇵 Японская иена',
    'CNY': '🇨🇳 Китайский юань',
    'KZT': '🇰🇿 Казахстанский тенге',
    'UAH': '🇺🇦 Украинская гривна',
    'BYN': '🇧🇾 Белорусский рубль',
    'CHF': '🇨🇭 Швейцарский франк'
}

# Список популярных криптовалют
CRYPTO_CURRENCIES = {
    'BTC': '₿ Биткоин',
    'ETH': 'Ξ Эфириум',
    'USDT': '₮ Tether',
    'BNB': '🔶 Binance Coin',
    'SOL': '◎ Solana',
    'XRP': 'XRP',
    'ADA': '₳ Cardano',
    'DOGE': '🐕 Dogecoin',
    'DOT': '● Polkadot',
    'MATIC': '⬡ Polygon',
    'LTC': 'Ł Litecoin',
    'AVAX': '△ Avalanche'
}

# Объединенный словарь всех валют
ALL_CURRENCIES = {**FIAT_CURRENCIES, **CRYPTO_CURRENCIES}
