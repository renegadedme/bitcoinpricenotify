# This program is a simple bitcoin price notification service
# The program sends the latest bitcoin price to Telegram once every 5mins
# It also sends a direct notification to a mobile device if the price of bitcoin drops below a certain threshold
# It uses Coingecko to get the latest bitcoin price in USD and IFTTT for notification.

import requests
import time
from datetime import datetime

bitcoin_price_threshold = 20000  # This is the minimum price which triggers an emergency notification

def main():
    bitcoin_price_history = []
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_price_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price < bitcoin_price_threshold:
            post_ifttt_webhook('bitcoin_price_emergency', price)

        #Send a Telegram notification. Once we have 5 items in our bitcoin_history send an update
        if len(bitcoin_price_history) == 5:
            post_ifttt_webhook('bitcoin_price_update', format_bitcoin_history(bitcoin_price_history))
            
            # Reset the price history after sending the notification
            bitcoin_history = []

        # Sleeps for 5 minutes 
        # (For testing purposes you can set it to a lower number)
        time.sleep(5 * 60)

def get_latest_bitcoin_price():
    bitcoin_api_url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&order=market_cap_desc&per_page=20&page=1&sparkline=false'
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
    
    #Convert the price to a floating point number
    return float (response_json[0]['current_price'])


def post_ifttt_webhook(event, value):
    ifttt_webhook_url = 'https://maker.ifttt.com/trigger/{}/with/key/yourIFTTTKey'
    
    # The payload that will be sent to IFTTT service
    data = {'value1': value}
    
    # Inserts a desired event based on the event name configured on IFTTT
    ifttt_event_url = ifttt_webhook_url.format(event)
    
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_bitcoin_history(bitcoin_price_history):
    rows = []
    for bitcoin_price in bitcoin_price_history:
        #Formats the date into a string: '24.02.2018 15:09'
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = bitcoin_price['price']
        #<b> (bold) tag creates bolded text
        #24.02.2018 15:09: $<b>10123.4</b>
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)

    # Uses a <br> (break) tag to create a new line
    # Joins the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


if __name__ == '__main__':
    main()