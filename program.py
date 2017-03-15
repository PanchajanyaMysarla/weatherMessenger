#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 11:49:10 2017

@author: panchajanyamysarla
"""
import requests,json,datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from twilio.rest import TwilioRestClient

def get_location():
   r = requests.get("http://freegeoip.net/json")
   j = json.loads(r.text)
   return j

def get_current_forecast_from_owm(parameters):
    currForecast = []
    r = requests.get('http://api.openweathermap.org/data/2.5/weather',params=parameters)
    data = json.loads(r.text)
    currForecast.append("Temperature: %s with %s"%(temp_convertor(data['main']['temp']),data['weather'][0]['description']))
    return currForecast

def get_future_forecast_from_owm(owmDate,parameters):
    futureWeatherForecast = []
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast',params=parameters)
    data = json.loads(r.text)
    reqData = [i for i in data['list'] if i['dt_txt'].find(owmDate) != -1]
    for i in data['list']:
        if i['dt_txt'].find(owmDate) != -1:
            simpleTime = datetime.datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            allTemp = temp_convertor(i['main']['temp'])
            futureWeatherForecast.append("Temperature: %s with %s at %s " %(allTemp,i['weather'][0]['description'],str(simpleTime)))
    
    #print("req data")
    #print(reqData)
    msg = numpy_analyzer(reqData)
    futureWeatherForecast.insert(0,msg)
    return futureWeatherForecast

def send_msg(msg_body,phno):
    account_sid = "AC548c10f7947a779ea4f37d5ed0e24fe9" # Your Account SID from www.twilio.com/console
    auth_token  = "c12a6bc23be34e709a7c1087d210222e"  # Your Auth Token from www.twilio.com/console

    client = TwilioRestClient(account_sid, auth_token)

    client.messages.create(body="Hello PJ, "+str(msg_body),
                                     to=phno,    # Replace with your phone number
                                     from_="+13126255156") # Replace with your Twilio number
def temp_convertor(kTemp):
    temp = []
    cTemp = kTemp-273.15
    fTemp = (kTemp*9/5) - 459.67               
    temp.append(str(round(cTemp))+"C")
    temp.append(str(round(fTemp))+"F")
    temp.append(str(round(kTemp))+"K")
    return temp

def numpy_analyzer(data):
    forecastData = data
    npArray = np.array([[(dic['main']['temp'])-273.15 for dic in forecastData],
                       [(dic['main']['temp_min'])-273.15 for dic in forecastData],
                       [(dic['main']['temp_max'])-273.15 for dic in forecastData]])
    #print(npArray)
    #print(np.median(npArray[0]))
    #print(np.median(npArray[1]))
    #print(np.median(npArray[2]))
    #print(np.mean(npArray[0]))
    
    check = np.median(npArray[0])

    if(check >= 5):
        return "wear regular hoddie"
    elif(check < 5 and check > -5):
        return "wear thick hoodie"
    elif(check < -5):
        return "fully cover your body its pretty cold"

def pandas_analyzer(data):
    forecastData = data
    #print(len(forecastData))
    #print("forecastData")
    #print(forecastData)
    forecastDic = {'temp':[],'temp_min':[],'temp_max':[],'pressure':[],'humidity':[],'weather_main':[],'weather_desc':[],'wind_speed':[]}
    dateList = []
    for dic in forecastData:
        dateList.append(dic['dt_txt'])
        forecastDic['temp'].append(round(((dic['main']['temp'])*9/5)-459.67))
        forecastDic['temp_min'].append(round(((dic['main']['temp_min'])*9/5)-459.67))
        forecastDic['temp_max'].append(round(((dic['main']['temp_max'])*9/5)-459.67))
        forecastDic['pressure'].append(dic['main']['pressure'])     
        forecastDic['humidity'].append(dic['main']['humidity'])
        forecastDic['weather_main'].append(dic['weather'][0]['main'])
        forecastDic['weather_desc'].append(dic['weather'][0]['description'])
        forecastDic['wind_speed'].append(dic['wind']['speed'])
    
    
    #print(forecastDic)
    df = pd.DataFrame(forecastDic,dateList)
    print(df[['temp','temp_min','temp_max','humidity','wind_speed']])
    df2 = df[['temp','temp_min','temp_max','humidity','wind_speed']]
    df2 = df2.cumsum()
    plt.figure(); df2.plot(); plt.legend(loc ='best')
    print(df2.mean())
    print(df2.median())
    
    
def get_forecast(weatherDate,phno):
    loc = get_location()
    lat = loc['latitude']
    long = loc['longitude']
    #lat = 40.3514
    #long = -75.9306
    twilioMsg = ""
    params = {'lat':lat,'lon':long,'appid':'f12f195956d3533f7a8d78665cd69def'}
    forecast = get_current_forecast_from_owm(params)
    futureForecast = get_future_forecast_from_owm(weatherDate,params)
    print("Current Weather : "+",".join(forecast).replace("'",""))
    print("Future Forecast "+weatherDate+" :"+", ".join(futureForecast).replace("'",""))
    twilioMsg += "Current Weather : "+", ".join(forecast).replace("'","")+" Future Forecast "+weatherDate+" : "+", ".join(futureForecast).replace("'","")
    send_msg(twilioMsg,phno)

def main():
    weatherDate = input("Enter date in yyyy-mm-dd to get weather forecast :")
    phno = input("Enter the phone no in +12345678989 format :")
    get_forecast(weatherDate,phno)

if __name__ == '__main__':
    main()