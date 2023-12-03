from datetime import datetime
from decimal import Decimal
import calendar
import requests
import xml.etree.ElementTree as ET

# GET /api?documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart=
API_CALL = "https://web-api.tp.entsoe.eu/api?securityToken=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U"
TESTDATE1 = "20230601"
TESTDATE2 = "20221231"
START_TIME = "0100"
END_TIME = "2300"

# Define how many cheapest hours you want to know
HOURS = 3


"""
Get tomorrow's date in a form that the API call needs it. Uses datetime and calendar libraries   
"""
def getCorrectDate():
    beforeDate = datetime.today()
    daysInMonth = calendar.monthrange(beforeDate.year, beforeDate.month)
    if beforeDate.day == daysInMonth[1] and beforeDate.month == 12:
        date = beforeDate.replace(day=1, month=1, year=beforeDate.year + 1).strftime('%Y%m%d')
    elif beforeDate.day == daysInMonth[1]:
        date = beforeDate.replace(day=1, month=beforeDate.month + 1).strftime('%Y%m%d')
    else:
        date = beforeDate.replace(day=beforeDate.day + 1).strftime('%Y%m%d')
    # date = TESTDATE1
    # date = TESTDATE2
    return date

""" 
Call the API, receive the data and retrieve the price information for each hour
"""
def getElecPriceData():
    date = getCorrectDate()
    first = date + START_TIME
    second = date + END_TIME
    apiCall = API_CALL + "&periodStart=" + first + "&periodEnd=" + second
    file = requests.get(apiCall)
    root = ET.fromstring(file.content)
    arr = []
    for elem in root.findall("./{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}TimeSeries/"
                             "{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}Period/"
                             "{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}Point"):
        element = elem.find("./{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}price.amount")
        arr.append(element.text)
    return arr


"""
Go through the price array and retrieve the x amount of cheapest hours
"""
def getActiveHours(priceArr):
    lowestPriceHours = []
    for index, price in enumerate(priceArr):
        if len(lowestPriceHours) == 0:
            lowestPriceHours.append(index)
        else:
            for index2, elem in enumerate(lowestPriceHours):
                if Decimal(price) > Decimal(priceArr[elem]):
                    lowestPriceHours.insert(index2, index)
                    break
                elif index2 == len(lowestPriceHours) - 1:
                    lowestPriceHours.append(index)
                    break
        if len(lowestPriceHours) > HOURS:
            lowestPriceHours.pop(0)
    print(lowestPriceHours)
    return lowestPriceHours


if __name__ == '__main__':
    prices = getElecPriceData()
    times = getActiveHours(prices)

