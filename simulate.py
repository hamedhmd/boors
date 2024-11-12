import jdatetime
from os import listdir
from os.path import isfile, join
import pandas as pd 
import numpy as np
import sys
from datetime import datetime, timedelta
from html_template import *
from pathlib import Path
import argparse


#load_last_days = 64
rsi_period = 10
ema_period = 5
#load_last_days = max(rsi_period, ema_period) * 2 + 2
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


def load_stocks_data(files_list, stock_names, from_date, to_date):
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
                    day_date = int(stock_day_data[1])
                    if day_date < from_date or day_date > to_date:
                        continue
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
#                if (line_counter > load_last_days):
#                    break

            #Ignore stocks with fewer days

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


def make_signal(stocks_data):
    sood = 0
    sahm = 0
    sale_stocks = []
    buy_stocks = []
    for each_stock_data in stocks_data:
        pool = 10000000
        rsi_values = each_stock_data['rsi']
        ema_values = each_stock_data['ema']
        close_prices = each_stock_data['close']
        stock_dates = each_stock_data['date']
        for day_date in stock_dates:
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
                    if yesterday_rsi <= 30 and sahm == 0:
                        sahm = pool / today_close_price
                        pool = 0
                        print ("KH:", convert_to_shamsi(str(day_date)), today_close_price)
                elif (today_ema > today_close_price and yesterday_ema < yesterday_close_price):
                    if yesterday_rsi >= 50 and sahm != 0:
                        pool =  sahm * today_close_price
                        sahm = 0
                        print ("FO:", convert_to_shamsi(str(day_date)), today_close_price)
                        print ((pool-10000000)/100000)
        if (sahm != 0):
            pool =  sahm * today_close_price
            sahm = 0
        print ((pool-10000000)/100000)
    return True


def main():
    parser = argparse.ArgumentParser(description='python3 simulate.py -from 20210101 -to 20211110 -stock 55916539620839777')
    parser.add_argument('-from', help='Ex: 20211102', required=True)
    parser.add_argument('-to', help='Ex: 20211109', required=True)
    parser.add_argument('-stock', help='Ex: 20212131231109', required=True)
    args = vars(parser.parse_args())
    try:
        from_date = int(args['from'])
        to_date = int(args['to'])
        stock_id = int(args['stock'])
    except:
        print ("Wrong FROM date or TO date or STOCK id")
        quit(2)

#    files_list = get_files(stocks_directory)
    stock_file = str(stock_id) + "_stock_history.csv"
    files_list = [stock_file]
    stock_names = load_stock_names(stock_names_file)
    stocks_data = load_stocks_data(files_list, stock_names, from_date, to_date)
    calculate_rsi(stocks_data, rsi_period)
    calculate_ema(stocks_data, ema_period)
    make_signal(stocks_data)


if __name__ == "__main__":
    main()


