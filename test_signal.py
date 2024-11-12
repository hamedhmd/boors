import jdatetime
from os import listdir
from os.path import isfile, join
import pandas as pd 
import numpy as np
import sys
from datetime import datetime, timedelta
from html_template import *
from pathlib import Path
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt


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


def load_stocks_data(files_list, stock_names):
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
        #        if yesterday_rsi < 45:
                stock_data = [each_stock_data['metadata'], today_rsi, today_ema, convert_to_shamsi(str(day_date)),]
                buy_stocks.append(stock_data)
            elif (today_ema > today_close_price and yesterday_ema < yesterday_close_price):
         #      if yesterday_rsi > 55:
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


def find_mins(stocks_data):
    for each_stock_data in stocks_data:
        df_close = pd.DataFrame(each_stock_data['close'], columns = ['close'])
        rsi_values = each_stock_data['rsi']
        n = 1  # number of points to be checked before and after
        df_close['min'] = df_close.iloc[argrelextrema(df_close.close.values, np.less_equal, order=n)[0]]['close']
        df_close['max'] = df_close.iloc[argrelextrema(df_close.close.values, np.greater_equal, order=n)[0]]['close']
        '''
        if pd.notnull(df_close['min'].iloc[-1]):
            trend_flag = "desc"
        else:
            trend_flag = "asc"
        '''

        old_min_price = 1
        old_min_rsi = 1
        div_min_value = 0
        div_flag = True
        for item in range(len(df_close['min'])-2, -1, -1):
            frame = df_close['min'].iloc[item]
            if pd.notnull(frame):
                div_flag = False
                new_min_price = frame
                new_min_rsi = rsi_values[item]
                new_date = str(each_stock_data['date'][item])
                if old_min_price == 1:
                    old_min_price = new_min_price
                    old_min_rsi = new_min_rsi
                    old_date = new_date
                    continue
                if old_min_rsi == 0:
                    old_min_rsi = 1
                if item > rsi_period:   #Ignore first rsi zero values
                    if new_min_price < old_min_price and new_min_rsi >= old_min_rsi:
                        div_min_value += 1
                        #print (new_date, (old_min_price-new_min_price)*100/old_min_price, (old_min_rsi-new_min_rsi)/old_min_rsi,old_date, convert_to_shamsi(old_date), new_date, convert_to_shamsi(new_date), "M+++++++++")
                        #print (each_stock_data['metadata'])
                    elif new_min_price > old_min_price and new_min_rsi <= old_min_rsi:
                        div_min_value += 1
                        #print (new_date, (old_min_price-new_min_price)*100/old_min_price, (old_min_rsi-new_min_rsi)/old_min_rsi,old_date, convert_to_shamsi(old_date), new_date, convert_to_shamsi(new_date), "M+++++++++")
                        #print (each_stock_data['metadata'])
                    else:
                        div_flag = False
                old_min_price = new_min_price
                old_min_rsi = new_min_rsi
                old_date = new_date
            if div_flag == False:
                True
                #break

        old_max_price = 1
        old_max_rsi = 1
        div_max_value = 0
        div_flag = True
        for item in range(len(df_close['max'])-2, -1, -1):
            frame = df_close['max'].iloc[item]
            if pd.notnull(frame):
                div_flag = False
                new_max_price = frame
                new_max_rsi = rsi_values[item]
                new_date = str(each_stock_data['date'][item])
                if old_max_price == 1:
                    old_max_price = new_max_price
                    old_max_rsi = new_max_rsi
                    old_date = new_date
                    continue
                if old_max_rsi == 0:
                    old_max_rsi = 1
                if item > rsi_period:   #Ignore first rsi zero values
                    if new_max_price > old_max_price and  new_max_rsi <= old_max_rsi:
                        div_max_value += 1
                        #print (new_date, (old_max_price-new_max_price)*100/old_max_price, (old_max_rsi-new_max_rsi)/old_max_rsi,old_date, convert_to_shamsi(old_date), new_date, convert_to_shamsi(new_date), "X-----")
                        #print (each_stock_data['metadata'])
                    elif new_max_price < old_max_price and new_max_rsi >= old_max_rsi:
                        div_max_value += 1
                        #print (new_date, (old_max_price-new_max_price)*100/old_max_price, (old_max_rsi-new_max_rsi)/old_max_rsi,old_date, convert_to_shamsi(old_date), new_date, convert_to_shamsi(new_date), "X-----")
                        #print (each_stock_data['metadata'])
                    else:
                        div_flag = False
                old_max_price = new_max_price
                old_max_rsi = new_max_rsi
                old_date = new_date
            if div_flag == False:
                True
                #break
        if div_min_value != 0:
            print (each_stock_data['metadata'], "M+++++++++++++", div_min_value)
        if div_max_value != 0:
            print (each_stock_data['metadata'], "X-------------", div_max_value)
#        plt.scatter([str(d) for d in each_stock_data['date']], df_close['min'], c='r')
#        plt.scatter([str(d) for d in each_stock_data['date']], df_close['max'], c='g')
#        plt.plot([str(d) for d in each_stock_data['date']], df_close['close'])
#        plt.scatter([str(d) for d in div_date], div_price, c='b')
#        plt.show()

    return True


def main():
    files_list = get_files(stocks_directory)
#    files_list = ["57273529732791251_stock_history.csv"]
    stock_names = load_stock_names(stock_names_file)
    stocks_data = load_stocks_data(files_list, stock_names)
    calculate_rsi(stocks_data, rsi_period)
    calculate_ema(stocks_data, ema_period)
    find_mins(stocks_data)
#    today_date = int(datetime.now().strftime("%Y%m%d"))
#    today_date = 20211123

#    buy_stocks, sale_stocks = make_signal(stocks_data, today_date)
#    make_html(buy_stocks, sale_stocks, today_date)


#    print (rsi_stocks, ema_stocks)


if __name__ == "__main__":
    main()


