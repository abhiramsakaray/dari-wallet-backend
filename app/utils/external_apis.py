import aiohttp
import asyncio
from typing import Optional, Dict, Any
from decimal import Decimal
from app.core.config import settings


class ExternalAPIService:
    """Service for external API integrations"""
    
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        """Get aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_gas_price(self, chain: str) -> Dict[str, Any]:
        """Get current gas price for a chain"""
        try:
            session = await self.get_session()
            
            if chain == "ethereum":
                # Use Etherscan API
                url = f"https://api.etherscan.io/api"
                params = {
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": settings.etherscan_api_key or ""
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data["status"] == "1":
                        result = data["result"]
                        return {
                            "slow": int(result["SafeLow"]),
                            "standard": int(result["ProposeGasPrice"]),
                            "fast": int(result["FastGasPrice"]),
                            "chain": chain
                        }
            
            elif chain == "bsc":
                # Use BSCScan API
                url = f"https://api.bscscan.com/api"
                params = {
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": settings.bscscan_api_key or ""
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data["status"] == "1":
                        result = data["result"]
                        return {
                            "slow": int(result["SafeLow"]),
                            "standard": int(result["ProposeGasPrice"]),
                            "fast": int(result["FastGasPrice"]),
                            "chain": chain
                        }
            
            # Default gas prices for other chains
            default_prices = {
                "tron": {"standard": 1, "fast": 1, "slow": 1},
                "solana": {"standard": 5000, "fast": 5000, "slow": 5000},
                "bitcoin": {"standard": 10, "fast": 20, "slow": 5},
                "xrp": {"standard": 0.00001, "fast": 0.00001, "slow": 0.00001}
            }
            
            if chain in default_prices:
                return {**default_prices[chain], "chain": chain}
            
            return {"error": f"Unsupported chain: {chain}"}
            
        except Exception as e:
            return {"error": f"Failed to get gas price: {str(e)}"}
    
    async def get_token_price(self, symbol: str) -> Dict[str, Any]:
        """Get token price from CoinGecko"""
        try:
            session = await self.get_session()
            
            # Use CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true"
            }
            
            if settings.coingecko_api_key:
                params["x_cg_demo_api_key"] = settings.coingecko_api_key
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if symbol.lower() in data:
                    token_data = data[symbol.lower()]
                    return {
                        "symbol": symbol.upper(),
                        "price_usd": token_data.get("usd"),
                        "price_change_24h": token_data.get("usd_24h_change"),
                        "market_cap": token_data.get("usd_market_cap")
                    }
                else:
                    return {"error": f"Token {symbol} not found"}
            
        except Exception as e:
            return {"error": f"Failed to get token price: {str(e)}"}
    
    async def get_rpc_status(self, chain: str) -> Dict[str, Any]:
        """Check RPC status for a chain"""
        try:
            session = await self.get_session()
            
            # Get RPC URL for the chain
            rpc_urls = {
                "ethereum": settings.ethereum_rpc_url,
                "bsc": settings.bsc_rpc_url,
                "tron": settings.tron_rpc_url,
                "solana": settings.solana_rpc_url,
                "bitcoin": settings.bitcoin_rpc_url,
                "xrp": settings.xrp_rpc_url
            }
            
            if chain not in rpc_urls:
                return {"error": f"Unsupported chain: {chain}"}
            
            rpc_url = rpc_urls[chain]
            
            # Simple health check
            if chain in ["ethereum", "bsc"]:
                # Ethereum-style RPC
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1
                }
                
                async with session.post(rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data:
                            return {
                                "chain": chain,
                                "status": "healthy",
                                "latest_block": int(data["result"], 16)
                            }
            
            elif chain == "tron":
                # Tron RPC
                async with session.get(f"{rpc_url}/wallet/getnowblock") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "block_header" in data:
                            return {
                                "chain": chain,
                                "status": "healthy",
                                "latest_block": data["block_header"]["raw_data"]["number"]
                            }
            
            # For other chains, just check if the URL is reachable
            async with session.get(rpc_url) as response:
                if response.status == 200:
                    return {
                        "chain": chain,
                        "status": "healthy",
                        "latest_block": None
                    }
            
            return {
                "chain": chain,
                "status": "unhealthy",
                "error": "RPC endpoint not responding"
            }
            
        except Exception as e:
            return {
                "chain": chain,
                "status": "error",
                "error": str(e)
            }
    
    async def get_market_data(self, symbols: list) -> Dict[str, Any]:
        """Get market data for multiple tokens"""
        try:
            session = await self.get_session()
            
            # Use CoinGecko API for multiple tokens
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": ",".join([symbol.lower() for symbol in symbols]),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            if settings.coingecko_api_key:
                params["x_cg_demo_api_key"] = settings.coingecko_api_key
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                market_data = {}
                for symbol in symbols:
                    if symbol.lower() in data:
                        token_data = data[symbol.lower()]
                        market_data[symbol.upper()] = {
                            "price_usd": token_data.get("usd"),
                            "price_change_24h": token_data.get("usd_24h_change"),
                            "market_cap": token_data.get("usd_market_cap"),
                            "volume_24h": token_data.get("usd_24h_vol")
                        }
                
                return market_data
            
        except Exception as e:
            return {"error": f"Failed to get market data: {str(e)}"}


# Global instance
external_api_service = ExternalAPIService() 