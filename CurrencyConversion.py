import json
import requests
import sys
import os

CONFIG_FILE = 'config.json'
CACHE_FILE = 'cache.json'
OUTPUT_FILE = 'conversions.json'
API_URL = 'https://api.fastforex.io/historical'

def load_api_key():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config['api_key']

def get_exchange_rates_for_currency(api_key, date, base_currency, cache):
    cache_key = f"{date}_{base_currency}"
    if cache_key in cache:
        rates = cache[cache_key]
    else:
        response = requests.get(f"{API_URL}?date={date}&from={base_currency}&api_key={api_key}")
        data = response.json()
        rates = data['results']
        cache[cache_key] = rates
        with open(CACHE_FILE, 'w') as cache_file:
            json.dump(cache, cache_file)
    return rates

def validate_amount(amount_str):
    try:
        amount = round(float(amount_str), 2)
        
        str_split = amount_str.split('.')
        if len(str_split) > 1 and len(str_split[1]) > 2:
            return None
        return amount
    except ValueError:
        return None


def validate_currency_code(code):
    return code.upper() if len(code) == 3 and code.isalpha() else None

def save_conversion(conversion):
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as file:
            conversions = json.load(file)
    else:
        conversions = []

    conversions.append(conversion)
    with open(OUTPUT_FILE, 'w') as file:
        json.dump(conversions, file, indent=4)

def main():    
    date = sys.argv[1]
    
    api_key = load_api_key()
    
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            cache = json.load(file)
    else:
        cache = {}
    
    amount = None
    base_currency = None
    target_currency = None
    while True:

        if amount is None:
            amount_str = input()
            if amount_str.strip().lower() == 'end':
                break
            
            amount = validate_amount(amount_str)
            if amount is None:
                print("Please enter a valid amount")
                continue
            
            
        if base_currency is None:
            base_currency = validate_currency_code(input().strip())

            if base_currency is None:
                print("Please enter a valid currency code")
                continue
        
            rates = None
            try:
                rates = get_exchange_rates_for_currency(api_key, date, base_currency, cache)
            except KeyError:
                base_currency = None
                print("Please enter a valid currency code")
                continue
        
        rate = None
        if target_currency is None:
            target_currency = validate_currency_code(input().strip())
            if target_currency is None:
                print("Please enter a valid currency code")
                continue

            try:
                rate = rates[target_currency]
            except KeyError:
                target_currency = None
                print("Please enter a valid currency code")
                continue

        if rate:
            try:
                converted_amount = int(amount * rate * 100) / 100
                print(f"{amount} {base_currency} is {converted_amount} {target_currency}")
                
                conversion = {
                    "date": date,
                    "amount": amount,
                    "base_currency": base_currency,
                    "target_currency": target_currency,
                    "converted_amount": converted_amount
                }
                save_conversion(conversion)

            except TypeError:
                print("Invalid target currency for the given date")
        
        amount = None
        base_currency = None
        target_currency = None
    
if __name__ == "__main__":
    main()
