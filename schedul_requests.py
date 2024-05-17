import requests
import schedule
from schedule import every,repeat
import time


@repeat(every().day.at('09:00'))
@repeat(every().day.at('12:00'))
@repeat(every().day.at('17:00'))
def update_espasa_db():
    try:
        response = requests.get('http://meli.dnoguesdev.com.ar/espasa/update_db/')
        if response.status_code == 200:
            print("Espasa db Update")
            print(response.text)
            print()
    except:
        print("No se pudo conectar con Espasa db")
        print()

        
@repeat(every(5).minutes)
def answer_questions():
    try:
        response = requests.get('http://meli.dnoguesdev.com.ar/api/preguntas/')
        if response.status_code == 200:
            print("apreguntas")
            print(response.text)
            print()
    except:
        print("No se pudo responder preguntas")
        print()
        
@repeat(every(5).minutes)
def get_leads():
    try:
        response = requests.get('http://meli.dnoguesdev.com.ar/leads/get_leads/')
        if response.status_code == 200:
            print("leads")
            print(response.text)
            print()
    except:
        print("No se pudo sincrinizar leads")
        print()


@repeat(every(5).minutes)
def answer_questions():
    try:
        response = requests.get('http://meli.dnoguesdev.com.ar/api/get_stats/')
        if response.status_code == 200:
            print("stats")
            print(response.text)
            print()
    except:
        print("No se pudo conseguir los stats")
        print()




while True:
    schedule.run_pending()
    time.sleep(1)
