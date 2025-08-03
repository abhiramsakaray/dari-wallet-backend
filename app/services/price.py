import aiohttp
from typing import Dict, Optional, List
from decimal import Decimal
from app.core.config import settings
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

class PriceService:
    """Service for fetching cryptocurrency prices and currency conversions"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = settings.coingecko_api_key
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_crypto_price(self, coin_id: str, currency: str = "usd") -> Optional[Decimal]:
        """Get cryptocurrency price in specified currency"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": currency
            }
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if coin_id in data and currency in data[coin_id]:
                        return Decimal(str(data[coin_id][currency]))
                else:
                    logger.error(f"Failed to get price for {coin_id}: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching price for {coin_id}: {e}")

        return None

    async def get_multiple_crypto_prices(self, coin_ids: List[str], currency: str = "usd") -> Dict[str, Decimal]:
        """Get multiple cryptocurrency prices"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": currency
            }
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        coin_id: Decimal(str(data[coin_id][currency]))
                        for coin_id in coin_ids
                        if coin_id in data and currency in data[coin_id]
                    }
                else:
                    logger.error(f"Failed to get prices: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching prices: {e}")

        return {}

    async def get_currency_conversion_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Get currency conversion rate"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/exchange_rates"
            if self.api_key:
                params = {"x_cg_demo_api_key": self.api_key}
            else:
                params = {}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    rates = data.get("rates", {})
                    if from_currency.lower() in rates and to_currency.lower() in rates:
                        from_rate = Decimal(str(rates[from_currency.lower()]["value"]))
                        to_rate = Decimal(str(rates[to_currency.lower()]["value"]))
                        return to_rate / from_rate
                else:
                    logger.error(f"Failed to get exchange rates: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching exchange rate: {e}")

        return None

    async def convert_crypto_to_currency(self, coin_id: str, amount: Decimal, target_currency: str) -> Optional[Decimal]:
        """Convert cryptocurrency amount to target currency"""
        try:
            usd_price = await self.get_crypto_price(coin_id, "usd")
            if not usd_price:
                return None
            if target_currency.lower() == "usd":
                return amount * usd_price
            conversion_rate = await self.get_currency_conversion_rate("usd", target_currency)
            if not conversion_rate:
                return None
            usd_value = amount * usd_price
            return usd_value * conversion_rate
        except Exception as e:
            logger.error(f"Error converting crypto to currency: {e}")
            return None

    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/simple/supported_vs_currencies"
            if self.api_key:
                params = {"x_cg_demo_api_key": self.api_key}
            else:
                params = {}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get supported currencies: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching supported currencies: {e}")

        return ["usd", "eur", "gbp", "jpy"]

    async def get_coin_list(self) -> Dict[str, str]:
        """Get list of supported cryptocurrencies with their IDs"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/coins/list"
            if self.api_key:
                params = {"x_cg_demo_api_key": self.api_key}
            else:
                params = {}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    coins = await response.json()
                    return {coin["symbol"].upper(): coin["id"] for coin in coins}
                else:
                    logger.error(f"Failed to get coin list: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching coin list: {e}")

        return {}

# Global price service instance
price_service = PriceService()

# Example FastAPI route
router = APIRouter()

@router.get("/prices")
async def get_prices():
    symbols = ["ethereum", "bitcoin", "binancecoin", "solana"]
    prices = await price_service.get_multiple_crypto_prices(symbols)
    return prices