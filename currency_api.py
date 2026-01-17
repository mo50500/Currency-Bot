import aiohttp
import asyncio
from typing import Dict, Optional

class CurrencyAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_crypto_price(self, from_crypto: str, to_currency: str = 'usd') -> Optional[float]:
        """Получить цену криптовалюты относительно другой валюты"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': from_crypto.lower(),
                'vs_currencies': to_currency.lower(),
                'precision': 8
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if from_crypto.lower() in data and to_currency.lower() in data[from_crypto.lower()]:
                        return data[from_crypto.lower()][to_currency.lower()]
            return None
        except Exception as e:
            print(f"Error getting crypto price: {e}")
            return None
    
    async def get_fiat_to_crypto_price(self, fiat: str, crypto: str) -> Optional[float]:
        """Получить цену фиатной валюты в криптовалюте"""
        # Сначала получаем цену криптовалюты в фиатной валюте
        crypto_price = await self.get_crypto_price(crypto, fiat)
        if crypto_price and crypto_price > 0:
            return 1 / crypto_price
        return None
    
    async def get_fiat_exchange_rate(self, from_fiat: str, to_fiat: str) -> Optional[float]:
        """Получить курс обмена между фиатными валютами через криптовалюту"""
        try:
            # Используем USDT как промежуточную валюту
            from_fiat_to_usdt = await self.get_fiat_to_crypto_price(from_fiat, 'tether')
            if from_fiat_to_usdt is None:
                return None
            
            to_fiat_to_usdt = await self.get_fiat_to_crypto_price(to_fiat, 'tether')
            if to_fiat_to_usdt is None:
                return None
            
            if to_fiat_to_usdt > 0:
                return from_fiat_to_usdt / to_fiat_to_usdt
            return None
        except Exception as e:
            print(f"Error getting fiat exchange rate: {e}")
            return None
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Универсальный метод получения курса обмена"""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Если валюты одинаковые
        if from_currency == to_currency:
            return 1.0
        
        # Определяем типы валют
        crypto_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'DOT': 'polkadot',
            'MATIC': 'polygon',
            'LTC': 'litecoin',
            'AVAX': 'avalanche-2'
        }
        
        is_from_crypto = from_currency in crypto_mapping
        is_to_crypto = to_currency in crypto_mapping
        
        try:
            if is_from_crypto and not is_to_crypto:
                # Криптовалюта -> фиат
                return await self.get_crypto_price(crypto_mapping[from_currency], to_currency.lower())
            elif not is_from_crypto and is_to_crypto:
                # Фиат -> криптовалюта
                return await self.get_fiat_to_crypto_price(from_currency.lower(), crypto_mapping[to_currency])
            elif is_from_crypto and is_to_crypto:
                # Криптовалюта -> криптовалюта (через USD)
                crypto_to_usd = await self.get_crypto_price(crypto_mapping[from_currency], 'usd')
                if crypto_to_usd:
                    usd_to_crypto = await self.get_fiat_to_crypto_price('usd', crypto_mapping[to_currency])
                    if usd_to_crypto:
                        return crypto_to_usd * usd_to_crypto
            else:
                # Фиат -> фиат
                return await self.get_fiat_exchange_rate(from_currency.lower(), to_currency.lower())
        except Exception as e:
            print(f"Error getting exchange rate: {e}")
        
        return None
