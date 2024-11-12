import jdatetime
import requests
from os import listdir
from os.path import isfile, join
import pandas as pd 
import numpy as np
import sys
from datetime import datetime, timedelta
from html_template import *
from pathlib import Path


rsi_period = 10
ema_period = 5
#load_last_days = max(rsi_period, ema_period) * 2 + 2
load_last_days = 90
stocks_directory = "stocks_history_fixed/"
stock_names_file = "stocks.txt"
tse_tmc_link = "http://dev.tsetmc.com/Loader.aspx?ParTree=151323&i="
rahavard_link = "https://rahavard365.com/asset/STOCK_ID/chart"
html_directory = "data/"


def get_files(directory_path):
    try:
        all_files = [afile for afile in listdir(directory_path) if isfile(join(directory_path, afile))]
        return all_files
    except:
        print ("Could not list files", file=sys.stderr)
        quit(10)


def load_stock_names(stock_names_file):
    stocks_data = {}
    try:
        with open(stock_names_file) as myf:
            for each_line in myf:
                if (each_line[-1] == "\n"):
                    each_line = each_line[:-1]
                try:
                    stock_data = each_line.split("*")
                    stock_id = stock_data[0]
                    stock_name = stock_data[1]
                    stock_group = stock_data[2]
                    stock_gid = stock_data[3]
                    stock_rah_id = stock_data[4]
                    stocks_data[stock_id] = [stock_name, stock_group, stock_gid, stock_rah_id]
                except:
                    True

    except Exception as e:
        print("Could not open stock file name", e)
        True
    return stocks_data


def load_stocks_data(files_list, stock_names, stocks_current_data):
    today_date = int(datetime.now().strftime("%Y%m%d"))
    stocks_data = []
    for each_file in files_list:
        file_name = stocks_directory + "/" + each_file
        with open (file_name, "r") as myf:
            line_counter = 0
            stock_data = {}
            stock_ticker = []
            stock_dates = []
            stock_first = []
            stock_high = []
            stock_low = []
            stock_close = []
            stock_value = []
            stock_vol = []
            stock_openint = []
            stock_per = []
            stock_open = []
            stock_last = []
            try:
                #Ignore header
                myf.readline()
            except:
                True
            for each_line in myf:
                #Remove trailing newline
                if (each_line[-1] == "\n"):
                    each_line = each_line[:-1]
                try:
                    stock_day_data = each_line.split(",")
                    stock_ticker.append(stock_day_data[0])
                    stock_dates.append(int(stock_day_data[1]))
#                    stock_dates.append([int(stock_day_data[1]), convert_to_shamsi(stock_day_data[1])])
                    stock_first.append(float(stock_day_data[2]))
                    stock_high.append(float(stock_day_data[3]))
                    stock_low.append(float(stock_day_data[4]))
                    stock_close.append(float(stock_day_data[5]))
                    stock_value.append(int(stock_day_data[6]))
                    stock_vol.append(int(stock_day_data[7]))
                    stock_openint.append(int(stock_day_data[8]))
                    stock_per.append(stock_day_data[9])
                    stock_open.append(float(stock_day_data[10]))
                    stock_last.append(float(stock_day_data[11]))
                except Exception as e:
                    continue
                line_counter += 1
                if (line_counter > load_last_days):
                    break

            #Ignore stocks with fewer days
            if (len(stock_close) < load_last_days):
                continue

            stock_ticker.reverse()
            stock_dates.reverse()
            stock_first.reverse()
            stock_high.reverse()
            stock_low.reverse()
            stock_close.reverse()
            stock_value.reverse()
            stock_vol.reverse()
            stock_openint.reverse()
            stock_per.reverse()
            stock_open.reverse()
            stock_last.reverse()

            stock_id = each_file.split("_")[0]
            stock_name = ""
            stock_group = ""
            stock_gid = ""
            if (stock_id in stock_names):
                stock_name = stock_names[stock_id][0]
                stock_group = stock_names[stock_id][1]
                stock_gid = stock_names[stock_id][2]
                stock_rah_id = stock_names[stock_id][3]
            stock_metadata = [stock_id, stock_name, stock_group, stock_gid, stock_rah_id]

            if stock_id in stocks_current_data:
                ticker = stock_ticker[0]
                today_date = stocks_current_data[stock_id][0]
                if (today_date != stock_dates[-1]):
                    stock_ticker.append(ticker)
                    stock_dates.append(stocks_current_data[stock_id][0])
                    stock_first.append(stocks_current_data[stock_id][1])
                    stock_high.append(stocks_current_data[stock_id][2])
                    stock_low.append(stocks_current_data[stock_id][3])
                    stock_close.append(stocks_current_data[stock_id][4])
                    stock_value.append(stocks_current_data[stock_id][5])
                    stock_vol.append(stocks_current_data[stock_id][6])
                    stock_openint.append(stocks_current_data[stock_id][7])
                    stock_per.append(stocks_current_data[stock_id][8])
                    stock_open.append(stocks_current_data[stock_id][9])
                    stock_last.append(stocks_current_data[stock_id][10])


            stock_data["metadata"] = stock_metadata
            stock_data["ticker"] = stock_ticker
            stock_data["date"] = stock_dates
            stock_data["first"] = stock_first
            stock_data["high"] = stock_high
            stock_data["low"] = stock_low
            stock_data["close"] = stock_close
            stock_data["value"] = stock_value
            stock_data["vol"] = stock_vol
            stock_data["openint"] = stock_openint
            stock_data["per"] = stock_per
            stock_data["open"] = stock_open
            stock_data["last"] = stock_last

        stocks_data.append(stock_data)
    return stocks_data


def convert_to_shamsi(date_val):
    price_date_year = int(date_val[0:4])
    price_date_month = int(date_val[4:6])
    price_date_day = int(date_val[6:8])
    jprice_date = jdatetime.date.fromgregorian(day=price_date_day ,month=price_date_month, year=price_date_year).strftime("%Y-%m-%d")
    return jprice_date


def calculate_rsi(stocks_data, ema_period):
    rsi_values = []
    for each_stock_data in stocks_data:
        close_prices = pd.DataFrame(each_stock_data['close'], columns = ['close'])

        close_delta = close_prices['close'].diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        ma_up = up.ewm(com = ema_period - 1, adjust=True, min_periods = ema_period).mean()
        ma_down = down.ewm(com = ema_period - 1, adjust=True, min_periods = ema_period).mean()

        rs = ma_up / ma_down

        close_prices['rsi'] = 100 - (100/(1 + rs))
        close_prices['rsi'] = close_prices['rsi'].replace(np.nan, 0)
        stock_rsi_values = close_prices['rsi'].values.tolist()
        rsi_values.append(stock_rsi_values)
        each_stock_data['rsi'] = stock_rsi_values
    return rsi_values


def calculate_ema(stocks_data, ema_period):
    smoothing = 2
    ema_values = []
    first_days = []
    for i in range(ema_period-1):
        first_days.append(0)
    for each_stock_data in stocks_data:
        close_prices = each_stock_data['close']
        stock_ema_values = []
        stock_ema_values.append(sum(close_prices[:ema_period]) / ema_period)
        for each_price in close_prices[ema_period:]:
            stock_ema_values.append((each_price * (smoothing / (1 + ema_period))) + stock_ema_values[-1] * (1 - (smoothing / (1 + ema_period))))
        stock_ema_values = first_days + stock_ema_values
        ema_values.append(stock_ema_values)
        each_stock_data['ema'] = stock_ema_values
    return ema_values


def make_signal(stocks_data, day_date):
    sale_stocks = []
    buy_stocks = []
    for each_stock_data in stocks_data:
        rsi_values = each_stock_data['rsi']
        ema_values = each_stock_data['ema']
        close_prices = each_stock_data['close']
        stock_dates = each_stock_data['date']

        if (day_date in stock_dates):
            date_index = stock_dates.index(day_date)
            today_rsi = rsi_values[date_index]
            today_ema = ema_values[date_index]
            today_close_price = close_prices[date_index]
            try:
                yesterday_rsi = rsi_values[date_index-1]
                yesterday_ema = ema_values[date_index-1]
                yesterday_close_price = close_prices[date_index-1]
            except:
                continue
            if (today_ema < today_close_price and yesterday_ema > yesterday_close_price):
                #if yesterday_rsi < 45:
                stock_data = [each_stock_data['metadata'], today_rsi, today_ema, convert_to_shamsi(str(day_date)),]
                buy_stocks.append(stock_data)
            elif (today_ema > today_close_price and yesterday_ema < yesterday_close_price):
                #if yesterday_rsi > 55:
                stock_data = [each_stock_data['metadata'], today_rsi, today_ema, convert_to_shamsi(str(day_date)),]
                sale_stocks.append(stock_data)
    sale_stocks.sort(key=lambda x:x[1], reverse=True)
    buy_stocks.sort(key=lambda x:x[1])
    return buy_stocks, sale_stocks


def make_html(buy_stocks, sale_stocks, day_date):
    Path(html_directory).mkdir(parents=True, exist_ok=True)
    html_file_name = html_directory + "/" + str(day_date) + ".html"
    day_datetime = datetime.strptime(str(day_date), '%Y%m%d')
    next_day = (day_datetime + timedelta(days=1)).strftime("%Y%m%d")
    prev_day = (day_datetime - timedelta(days=1)).strftime("%Y%m%d")


    html_content = html_header + sale_header
    for each_stock in sale_stocks:
        stock_id = each_stock[0][0]
        stock_name = each_stock[0][1]
        stock_group = each_stock[0][2]
        stock_rah_id = each_stock[0][4]
        rsi_value = int(each_stock[1])
        ema_value = int(each_stock[2])
        day_date_shamsi = each_stock[3]
        tse_link = tse_tmc_link + stock_id
        rah_link = rahavard_link.replace("STOCK_ID", stock_rah_id)
        if stock_name == "":
            stock_name = "XXX"
        html_content += '<tr>\n<td> <a href="' + rah_link + '" target="_blank">' + stock_name + '</a> </td>\n<td>' + str(rsi_value) + '</td>\n<td>' + str(ema_value) + '</td>\n<td>' + day_date_shamsi + '</td>\n</tr>'
    html_content += sale_footer.replace("PREVIOUS", prev_day)
    html_content += buy_header

    for each_stock in buy_stocks:
        stock_id = each_stock[0][0]
        stock_name = each_stock[0][1]
        stock_group = each_stock[0][2]
        stock_rah_id = each_stock[0][4]
        rsi_value = int(each_stock[1])
        ema_value = int(each_stock[2])
        day_date_shamsi = each_stock[3]
        tse_link = tse_tmc_link + stock_id
        rah_link = rahavard_link.replace("STOCK_ID", stock_rah_id)
        if stock_name == "":
            stock_name = "XXX"
        html_content += '<tr>\n<td> <a href="' + rah_link + '" target="_blank">' + stock_name + '</a> </td>\n<td>' + str(rsi_value) + '</td>\n<td>' + str(ema_value) + '</td>\n<td>' + day_date_shamsi + '</td>\n</tr>'

    html_content += buy_footer.replace("NEXT", next_day)
    html_content += html_footer
    
    with open(html_file_name, "w") as myf:
        myf.write(html_content)

    return True


def get_stocks_current_data(today_date):
    stocks_data = {}
    stocks_list_link = 'http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0'

    req_headers_tse = {
        "Host": "www.tsetmc.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Cookie": "_ga=GA1.2.795106609.1629610541; ASP.NET_SessionId=vmd31u1eiyfv3zwaudo1tb4v; _gid=GA1.2.885640986.1636785174"
    }

    response = requests.get(stocks_list_link, headers=req_headers_tse)
    if (response.status_code == 200):
        stocks_data_all = response.text.replace("@", "\n").replace(";", "\n").split("\n")
        for each_item in stocks_data_all:
            stock_data = []
            if (each_item.find(",IR") >=0 ):
                stock_data = each_item.split(",")
                stock_id = stock_data[0]
                first = float(stock_data[5])
                close =  float(stock_data[6])
                last =  float(stock_data[7])
                vol = int(stock_data[9])
                value = int(stock_data[10])
                low =  float(stock_data[11])
                high =  float(stock_data[12])
                stock_data = [today_date, first, high, low, close, value, vol, 0, '0', 0.0, last]
#                current_data = str(today_date) + "," + first + "," + high + "," + low + "," + close + "," + value + "," + vol + "," + "0" + "," + "0" + "," + "0" + "," + last
                stocks_data[stock_id] = stock_data

    else:
        error = "Could not get current data"
        print (error)
        with open (ERROR_FILE, "a") as myf:
            myf.write(error + "\n")
    return stocks_data


def main():
    files_list = get_files(stocks_directory)
#    files_list = ["50792786683910016_stock_history.csv"]
    today_date = int(datetime.now().strftime("%Y%m%d"))
#    today_date = 20211109
    stocks_current_data = get_stocks_current_data(today_date)
    stock_names = load_stock_names(stock_names_file)
    stocks_data = load_stocks_data(files_list, stock_names, stocks_current_data)
    calculate_rsi(stocks_data, rsi_period)
    calculate_ema(stocks_data, ema_period)

    buy_stocks, sale_stocks = make_signal(stocks_data, today_date)
    make_html(buy_stocks, sale_stocks, today_date)


#    print (rsi_stocks, ema_stocks)


if __name__ == "__main__":
    main()


