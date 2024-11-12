import requests
import json
from pathlib import Path
import jdatetime
from os import listdir
from os.path import isfile, join



ERROR_FILE = "ERROR_CAPITAL_RISING"
stocks_directory = "stocks_history/"
stocks_fixed_directory = "stocks_history_fixed/"
stocks_history_rising_directory = "stocks_capital_risong_history/"
stock_history_header = "<TICKER>,<DTYYYYMMDD>,<FIRST>,<HIGH>,<LOW>,<CLOSE>,<VALUE>,<VOL>,<OPENINT>,<PER>,<OPEN>,<LAST>"


def get_files(directory_path):
    all_files = [afile for afile in listdir(directory_path) if isfile(join(directory_path, afile))]
    return all_files


def load_rising_prices():
    stocks_rising_files = get_files(stocks_history_rising_directory)

    all_rising_values = {}
    for each_file in stocks_rising_files:
        stock_id = each_file.split("_")[0]
        file_name = stocks_history_rising_directory + each_file
        stock_rising_data = []
        with open (file_name, "r") as myf:
            for each_line in myf:
                if (each_line[-1] == "\n"):
                    each_line = each_line[:-1]

                rising_list = each_line.split(",")
                rising_date_list = rising_list[0].split("/")
                rising_date_year = int(rising_date_list[0])
                rising_date_month = int(rising_date_list[1])
                rising_date_day = int(rising_date_list[2])
                rising_date = int(jdatetime.date(rising_date_year, rising_date_month, rising_date_day).togregorian().strftime("%Y%m%d"))
                rising_val_after = float(rising_list[1])
                rising_val_before = float(rising_list[2])
                rising_data_list = [rising_date, rising_val_after, rising_val_before]
                stock_rising_data.append(rising_data_list)
        stock_rising_data.reverse()
        all_rising_values[stock_id] = stock_rising_data
    return all_rising_values


def load_stock_prices():
    stocks_files = get_files(stocks_directory)

    all_stocks_values = {}
    for each_file in stocks_files:
        stock_id = each_file.split("_")[0]
        file_name = stocks_directory + each_file
        stock_history_data = []
        with open (file_name, "r") as myf:
            header = myf.readline()
            for each_line in myf:
                if (each_line[-1] == "\n"):
                    each_line = each_line[:-1]
                line_list = each_line.split(",")
                ticker = line_list[0]
                sdate = int(line_list[1])
                first_price = float(line_list[2])
                high_price = float(line_list[3])
                low_price = float(line_list[4])
                close_price = float(line_list[5])
                value = line_list[6]
                vol = line_list[7]
                openint = line_list[8]
                per = line_list[9]
                open_price = float(line_list[10])
                last_price = float(line_list[11])

                stock_data_list = [ticker, sdate, first_price, high_price, low_price, close_price, value, vol, openint, per, open_price, last_price]
                stock_history_data.append(stock_data_list)
        stock_history_data.reverse()
        all_stocks_values[stock_id] = stock_history_data
#        if len (all_stocks_values) > 1:
#            return all_stocks_values #FIXME
    return all_stocks_values


def fix_capital_rising_prices(rising_data, stocks_data):
    for each_stock_id in stocks_data:
        if each_stock_id in rising_data:
            for each_rising in rising_data[each_stock_id]:
                rising_date = each_rising[0]
                rising_factor = each_rising[2] / each_rising[1]
                for each_day in stocks_data[each_stock_id]:
                    sdate = each_day[1]
                    first_price = each_day[2]
                    high_price = each_day[3]
                    low_price = each_day[4]
                    close_price = each_day[5]
                    open_price = each_day[10]
                    last_price = each_day[11]
                    if (sdate < rising_date):
                        each_day[2] = first_price * rising_factor
                        each_day[3] = high_price  * rising_factor
                        each_day[4] = low_price * rising_factor
                        each_day[5] = close_price * rising_factor
                        each_day[10] = open_price * rising_factor
                        each_day[11] = last_price * rising_factor
                    else:
                        break
    return stocks_data


def write_fixed_prices(stocks_data):
    Path(stocks_fixed_directory).mkdir(parents=True, exist_ok=True)
    for each_stock_id in stocks_data:
        file_name = stocks_fixed_directory + each_stock_id + "_stock_history.csv"
        with open(file_name, "w") as myf:
            myf.write(stock_history_header)
            stocks_data[each_stock_id].reverse()
            for each_day in stocks_data[each_stock_id]:
                day_data = "\n"
                for each_part in each_day:
                    day_data = day_data + "," + str(each_part)
                day_data = day_data.replace("\n,", "\n")
                myf.write(day_data)


def main():
    rising_data = load_rising_prices()
    stocks_data = load_stock_prices()
    stock_fixed_data = fix_capital_rising_prices(rising_data, stocks_data)
    write_fixed_prices(stocks_data)


if __name__ == "__main__":
    main()
