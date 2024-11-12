import requests
from datetime import datetime
from os import listdir
from os.path import isfile, join
import sys

ERROR_FILE = "ERROR"
stocks_file = "stocks.txt"
stocks_directory = "stocks_history_fixed/"
load_last_days = 90000


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
            if (each_item.find(",IR") >=0 ):
                stock_data = each_item.split(",")
                stock_id = stock_data[0]
                first = stock_data[5]
                last = stock_data[6]
                close = stock_data[7]
                vol = stock_data[9]
                value = stock_data[10]
                low = stock_data[11]
                high = stock_data[12]
                current_data = str(today_date) + "," + first + "," + high + "," + low + "," + close + "," + value + "," + vol + "," + "0" + "," + "0" + "," + "0" + "," + last
                stocks_data[stock_id] = current_data

    else:
        error = "Could not get current data"
        print (error)
        with open (ERROR_FILE, "a") as myf:
            myf.write(error + "\n")
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
    files_list = get_files(stocks_directory)
    files_list = ["50792786683910016_stock_history.csv"]
    stock_names = load_stock_names(stocks_file)
    stocks_data = load_stocks_data(files_list, stock_names)


    today_date = int(datetime.now().strftime("%Y%m%d"))

    stocks_current_data = get_stocks_current_data(today_date)
    print (stocks_data)
    for each_stock in stocks_data:
        sid = each_stock['metadata'][0]
        ticker = each_stock['ticker'][0]
        if sid in stocks_current_data:
            stocks_current_data[sid] = ticker + "," + stocks_current_data[sid]
#            print (stocks_current_data[sid])

#    for each_stock in stocks_current_data:
#        print (stocks_current_data[each_stock])



if __name__ == "__main__":
    main()
