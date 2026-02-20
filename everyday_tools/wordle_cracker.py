import requests
from datetime import datetime

def word():
    today = datetime.now().strftime("%Y-%m-%d")
    the_link = f"https://www.nytimes.com/svc/wordle/v2/{today}.json"

    try:
        response = requests.get(the_link)
        data = response.json()
        return data['solution'].upper()
    except:
        return "ERROR: COULD NOT FETCH THE WORD SORRY TRY AGAIN OR USE A WEBSITE IF THIS IS A LONG-STANDING ISSUE"

the_word = word()

print(f"Todays word fished directly from their API is... {the_word}!!!")