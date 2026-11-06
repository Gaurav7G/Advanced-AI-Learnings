from datetime import datetime
import requests
import os
import json

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url,timeout=10)  #we will use this 3rd party Library to call this web API and get the weather information for the given city.
    return response.text

def get_stock_price(symbol):
    url = "https://finnhub.io/api/v1/quote"

    #paramters required by finnhub to identify the stock and authenticate our API request.
    params = {
        "symbol": symbol.upper(),  #convert the symbol to uppercase as finnhub expects the stock symbol in uppercase.
        "token": os.getenv("FINNHUB_API_KEY")  #get the API key from environment variable

    }
    response = requests.get(url,params=params,timeout=10)
    #raise an excpetion if the API returns an HTTP error
    response.raise_for_status()

    data = response.json() #convert the json response from Finnhub into a python dictionary

     # Finnhub returns 0 for the current price when valid quote data is unavailable
    if not data or data.get("c", 0) == 0:
        return f"No valid stock quote found for {symbol}"
    return {
        "symbol": symbol.upper(),
        "current_price": data["c"],       # Latest available stock price
        "change": data["d"],              # Price change from previous close
        "percentage_change": data["dp"],  # Percentage change from previous close
        "high": data["h"],                # High price of the day
        "low": data["l"],                 # Low price of the day
        "open": data["o"],                # Opening price of the day
        "previous_close": data["pc"]      # Previous trading day's closing price
    }
    

#TOOLS = [{},{},{}]


TOOLS = [
    {
        "type": "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Returns the current date and time as a formatted string",  # LLM will use this description to understand what the function does and when to call it.
            "parameter" : {
                "type" : "object",
                "properties" : {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Returns the current weather information for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City to get the weather for.",
                    }
                },

            },
        },
    },
{
    "type": "function",
    "function": {
        "name": "get_stock_price",

        # This description helps Qwen understand WHEN to call this function
        "description": "Returns the latest available stock price and market quote information for a given stock ticker symbol.",

        "parameters": {
            "type": "object",

            # Define what arguments Python function expects
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol. For example, AAPL for Apple, MSFT for Microsoft, NVDA for NVIDIA."
                }
            },

            # Tells Qwen that symbol must be provided when calling this tool
            "required": ["symbol"]
        }
    }
}

]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_stock_price" : get_stock_price,
}