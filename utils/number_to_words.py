from math import floor

def number_to_words(n):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if n < 20:
        return ones[n]
    elif n < 100:
        return tens[n // 10] + ("" if n % 10 == 0 else " " + ones[n % 10])
    elif n < 1000:
        return ones[n // 100] + " Hundred" + ("" if n % 100 == 0 else " " + number_to_words(n % 100))
    elif n < 1_000_000:
        return number_to_words(n // 1000) + " Thousand" + ("" if n % 1000 == 0 else " " + number_to_words(n % 1000))
    else:
        return number_to_words(n // 1_000_000) + " Million" + ("" if n % 1_000_000 == 0 else " " + number_to_words(n % 1_000_000))

def number_to_words_usd(amount):
    dollars = floor(amount)
    cents = round((amount - dollars) * 100)
    dollar_words = number_to_words(dollars) + " US Dollars"
    if cents > 0:
        cent_words = number_to_words(cents) + (" Cent" if cents == 1 else " Cents")
        return f"{dollar_words} and {cent_words} Only"
    else:
        return f"{dollar_words} Only"

def usd_format(amount):
    return f"USD {amount:,.2f}"