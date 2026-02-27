"""
Chat&Talk GPT - Currency Converter Module
Provides currency conversion functionality using free APIs (ExchangeRate-API, Frankfurter)
"""
import requests
import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger("CurrencyConverter")

# Supported currencies with their full names
SUPPORTED_CURRENCIES = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound Sterling",
    "INR": "Indian Rupee",
    "NPR": "Nepalese Rupee",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "KRW": "South Korean Won",
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone",
    "DKK": "Danish Krone",
    "NZD": "New Zealand Dollar",
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "RUB": "Russian Ruble",
    "ZAR": "South African Rand",
    "TRY": "Turkish Lira",
    "THB": "Thai Baht",
    "MYR": "Malaysian Ringgit",
    "IDR": "Indonesian Rupiah",
    "PHP": "Philippine Peso",
    "PLN": "Polish Zloty",
    "CZK": "Czech Koruna",
    "HUF": "Hungarian Forint",
    "ILS": "Israeli New Shekel",
    "AED": "United Arab Emirates Dirham",
    "SAR": "Saudi Riyal",
    "PKR": "Pakistani Rupee",
    "BDT": "Bangladeshi Taka",
    "LKR": "Sri Lankan Rupee",
    "MMK": "Myanmar Kyat",
    "KWD": "Kuwaiti Dinar",
    "QAR": "Qatari Riyal",
    "BHD": "Bahraini Dinar",
    "OMR": "Omani Rial"
}

# API endpoints (in order of preference - free, no key required)
API_ENDPOINTS = [
    "https://open.er-api.com/v6/latest",  # ExchangeRate-API (free, no key)
    "https://api.frankfurter.app/latest"   # Frankfurter (free, no key)
]

# Cache duration in seconds (15 minutes)
CACHE_DURATION = 900


class CurrencyConverter:
    """
    Currency converter class that fetches exchange rates from free APIs
    and provides conversion functionality with caching.
    """
    
    def __init__(self, user_agent: str = "ChatAndTalkGPT/1.0"):
        """
        Initialize the currency converter.
        
        Args:
            user_agent: User agent string for API requests
        """
        self.user_agent = user_agent
        self._rates_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._last_error: Optional[str] = None
        
        # Initialize by loading exchange rates for common base currencies
        self._load_initial_rates()
        
        logger.info("CurrencyConverter initialized successfully")
    
    def _load_initial_rates(self):
        """Load initial exchange rates for common base currencies."""
        common_bases = ["USD", "EUR", "GBP"]
        for base in common_bases:
            self.get_all_rates(base)
    
    def _is_cache_valid(self, base_currency: str) -> bool:
        """Check if cached rates are still valid."""
        if base_currency not in self._cache_timestamp:
            return False
        
        elapsed = time.time() - self._cache_timestamp[base_currency]
        return elapsed < CACHE_DURATION
    
    def _fetch_rates_from_api(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        """
        Fetch exchange rates from free APIs.
        
        Args:
            base_currency: Base currency code (e.g., 'USD', 'EUR')
            
        Returns:
            Dictionary of exchange rates or None if failed
        """
        self._last_error = None
        
        for api_url in API_ENDPOINTS:
            try:
                if "open.er-api.com" in api_url:
                    # ExchangeRate-API format
                    url = f"{api_url}/{base_currency.upper()}"
                elif "frankfurter.app" in api_url:
                    # Frankfurter API format
                    url = f"{api_url}?from={base_currency.upper()}"
                
                logger.info(f"Fetching exchange rates from {url}")
                
                response = requests.get(
                    url, 
                    headers={"User-Agent": self.user_agent},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse response based on API format
                if "open.er-api.com" in api_url:
                    if data.get("result") == "success":
                        rates = data.get("rates", {})
                        # Filter to only supported currencies
                        return {
                            code: rate for code, rate in rates.items() 
                            if code in SUPPORTED_CURRENCIES
                        }
                elif "frankfurter.app" in api_url:
                    rates = data.get("rates", {})
                    return {
                        code: rate for code, rate in rates.items()
                        if code in SUPPORTED_CURRENCIES
                    }
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed for {api_url}: {e}")
                self._last_error = str(e)
                continue
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse API response from {api_url}: {e}")
                self._last_error = str(e)
                continue
        
        logger.error("All currency APIs failed")
        return None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'INR')
            
        Returns:
            Dictionary with conversion result
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Validate currencies
        if from_currency not in SUPPORTED_CURRENCIES:
            return {
                "success": False,
                "error": f"Unsupported source currency: {from_currency}",
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        if to_currency not in SUPPORTED_CURRENCIES:
            return {
                "success": False,
                "error": f"Unsupported target currency: {to_currency}",
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        if amount < 0:
            return {
                "success": False,
                "error": "Amount cannot be negative",
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        # Get exchange rate
        rate = self.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            return {
                "success": False,
                "error": f"Failed to get exchange rate: {self._last_error or 'Unknown error'}",
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        # Calculate result
        result = round(amount * rate, 2)
        
        return {
            "success": True,
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "result": result,
            "rate": rate,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate or None if failed
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Same currency conversion
        if from_currency == to_currency:
            return 1.0
        
        # Try to get rates from cache or fetch new ones
        rates = self._get_rates_for_base(from_currency)
        
        if rates is None:
            # Try fetching with to_currency as base and convert
            rates = self._get_rates_for_base(to_currency)
            if rates and from_currency in rates:
                # Convert using inverse rate
                return 1.0 / rates[from_currency]
            return None
        
        if to_currency in rates:
            return rates[to_currency]
        
        return None
    
    def _get_rates_for_base(self, base_currency: str) -> Optional[Dict[str, float]]:
        """
        Get exchange rates for a base currency (with caching).
        
        Args:
            base_currency: Base currency code
            
        Returns:
            Dictionary of exchange rates or None if failed
        """
        base_currency = base_currency.upper()
        
        # Check cache first
        if base_currency in self._rates_cache and self._is_cache_valid(base_currency):
            return self._rates_cache[base_currency]
        
        # Fetch new rates
        rates = self._fetch_rates_from_api(base_currency)
        
        if rates:
            self._rates_cache[base_currency] = rates
            self._cache_timestamp[base_currency] = time.time()
            logger.info(f"Updated exchange rates for base currency: {base_currency}")
            return rates
        
        # Return cached data even if expired (as fallback)
        if base_currency in self._rates_cache:
            logger.warning(f"Using expired cache for {base_currency}")
            return self._rates_cache[base_currency]
        
        return None
    
    def get_all_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """
        Get all exchange rates for a base currency.
        
        Args:
            base_currency: Base currency code (default: 'USD')
            
        Returns:
            Dictionary with all exchange rates
        """
        base_currency = base_currency.upper()
        
        if base_currency not in SUPPORTED_CURRENCIES:
            return {
                "success": False,
                "error": f"Unsupported base currency: {base_currency}",
                "base_currency": base_currency
            }
        
        rates = self._get_rates_for_base(base_currency)
        
        if rates is None:
            return {
                "success": False,
                "error": f"Failed to fetch rates: {self._last_error or 'Unknown error'}",
                "base_currency": base_currency
            }
        
        return {
            "success": True,
            "base_currency": base_currency,
            "rates": rates,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_supported_currencies(self) -> Dict[str, str]:
        """
        Get list of supported currencies with their names.
        
        Returns:
            Dictionary of currency codes to currency names
        """
        return SUPPORTED_CURRENCIES.copy()
    
    def refresh_cache(self, base_currency: str = "USD") -> bool:
        """
        Manually refresh the cache for a specific base currency.
        
        Args:
            base_currency: Base currency code to refresh
            
        Returns:
            True if refresh successful, False otherwise
        """
        base_currency = base_currency.upper()
        
        # Clear cache for this currency
        if base_currency in self._rates_cache:
            del self._rates_cache[base_currency]
        if base_currency in self._cache_timestamp:
            del self._cache_timestamp[base_currency]
        
        # Fetch new rates
        rates = self._fetch_rates_from_api(base_currency)
        
        if rates:
            self._rates_cache[base_currency] = rates
            self._cache_timestamp[base_currency] = time.time()
            logger.info(f"Successfully refreshed cache for {base_currency}")
            return True
        
        return False


# Import json for error handling
import json

# Create singleton instance
currency_converter = CurrencyConverter()


def get_currency_converter() -> CurrencyConverter:
    """Get the singleton currency converter instance."""
    return currency_converter
