import ssl
import requests
import urllib.request, urllib.parse, urllib.error
import json
import http
import schedule
import time
from datetime import datetime

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

api_key = False

if api_key is False:
    api_key = 42
    serviceurl = 'http://py4e-data.dr-chuck.net/json?'
else :
    serviceurl = 'https://maps.googleapis.com/maps/api/geocode/json?'

urlservice = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict'
now = datetime.now()
today_date = now.strftime('%d-%m-%Y')

telegram_api = 'https://api.telegram.org/bot1885646324:AAFiDEfWdqRpPB4V_UTkZEBKbUx2BzykA98/sendMessage?chat_id=__groupid__&text='
group_id = '@Project_2707'

center_name = list()

def fetch_from_cowin(district_id):
    query_parms = '?district_id={}&date={}'.format(district_id, today_date)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox86.0"}
    url = urlservice + query_parms
    uh = requests.get(url, headers=headers)
    fetch_from_availability(uh)

def fetch_from_availability(uh):
    response = uh.json()
    count = 0

    for x in response['centers']:
        center_name.append(x['name'])

    for center in response['centers']:
        count = count + 1
        if count > 5: time.sleep(1)

        if center['sessions'][0]['min_age_limit'] == 18 and (center['sessions'][0]['available_capacity_dose1'] > 9 or center['sessions'][0]['available_capacity_dose2']) > 9 and center['fee_type'] == 'Paid':

            if center['name'] in center_name:
                address = center['address']
                if len(address) < 1: continue

                parms = dict()
                parms['address'] = address
                if api_key is not False: parms['key'] = api_key
                url = serviceurl + urllib.parse.urlencode(parms)

                uh = urllib.request.urlopen(url, context=ctx)
                data = uh.read().decode()

                try:
                    js = json.loads(data)
                except:
                    js = None

                if not js or 'status' not in js or js['status'] != 'OK':
                    continue

                lat = js['results'][0]['geometry']['location']['lat']
                lng = js['results'][0]['geometry']['location']['lng']

                link = 'https://www.google.com/maps/dir//' + str(lat) + ',' + str(lng) + '/'

                message = 'For Age Group 18-44 \nPincode: {} \nLocation: {} \nCentre Name: {} \nDate: {} \nDistrict: {} \nVaccine: {} \nFees: {} \nDose1: {}, Dose2: {} \n\nLink: https://selfregistration.cowin.gov.in/\nDirections: {}\n-----------------\n'.format(center['pincode'], center['address'], center['name'], center['sessions'][0]['date'], center['block_name'], center['sessions'][0]['vaccine'], center['vaccine_fees'][0]['fee'], center['sessions'][0]['available_capacity_dose1'], center['sessions'][0]['available_capacity_dose2'], link)

                #print(message)
                send_message_telegram(message)
                center_name.remove(center['name'])

def send_message_telegram(message):
    final_telegram_url = telegram_api.replace('__groupid__', group_id)
    final_telegram_url = final_telegram_url + message
    response = requests.get(final_telegram_url)
    print(response)

if __name__ == '__main__':
    fetch_from_cowin(650)
