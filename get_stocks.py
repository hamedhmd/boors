import requests
import json
from pathlib import Path

#TODO Save stocks names, search only new ones, not all of them

ERROR_FILE = "ERROR"
stocks_file = "stocks.txt"


def get_stocks():
    stocks_names = []
    stocks_names_with_id = []
    last_stocks = []


    stocks_list_link = 'https://rahavard365.com/api/marketmap/data?asset=1&market=&category=1&industry=&size=1&color=1'
    search_stock_by_name_tse_link = "http://www.tsetmc.com/tsev2/data/search.aspx?skey="
#    search_stock_by_name_tse_link = "http://tse.fanafzar.net/tsev2/data/search.aspx?skey="
    search_stock_by_name_rahavard_link = "https://rahavard365.com/api/search/items/real?keyword="

    req_headers = {
            "Host": "rahavard365.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Cache-Control": "max-age=0",
            "TE": "trailers"
            }

    req_headers_tse = {
        "Host": "www.tsetmc.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Cookie": "_ga=GA1.2.1878575426.1595773453; ASP.NET_SessionId=ssdgngp21ui2qcjx1v4z"
    }
    try:
        response = requests.get(stocks_list_link, headers=req_headers) #Sometimes, it make error first time!
        response = requests.get(stocks_list_link, headers=req_headers)
        response = requests.get(stocks_list_link, headers=req_headers)
        if (response.status_code == 200):
            stocks_data = response.text.split("\n")[4].split("=")[1].split(";")[0]
        else:
            error = "Could not get list of stocks"
            print (error)
            with open (ERROR_FILE, "a") as myf:
                myf.write(error + "\n")

        raw_data = json.loads(stocks_data)
        for each_group in raw_data['item']['children']:
            for each_stock in each_group['children']:
                rname = each_stock['name'] + "*" + each_group['name'] + "*" + each_group['id']
                stocks_names.append(rname)

        print ("Number of Stocks:", len(stocks_names))
    except:
        error = "Could not get list of stocks"
        print (error)
        with open (ERROR_FILE, "a") as myf:
            myf.write(error + "\n")
    try:
        with open(stocks_file, "r") as myf:
            for each_stock in myf:
                last_stocks.append(each_stock.split("*")[1])
    except:
        True

    for each_stock in stocks_names:
        print ("Searching item number: ", stocks_names.index(each_stock)+1, "/", len(stocks_names), end='\r')
        stock_raw_name = each_stock.split("*")[0]
        stock_name = stock_raw_name.replace(" ", "%20")
        stock_id = "0"
        rahavard_id = "0"
        if stock_raw_name not in last_stocks:
            req_response = requests.get(search_stock_by_name_tse_link+stock_name, headers=req_headers_tse)
            if (req_response.status_code == 200):
                stock_id = (req_response.text.split("\n")[0].split(",")[2]) #get first line, take the the third part which is id
                if (stock_id.isnumeric()):
                    stock_name_with_id = stock_id + "*" + each_stock
                    #stocks_names_with_id.append(stock_name_with_id)
            else:
                    error = "Stock id not found for tse: " + stock_name
                    print (error)
                    with open (ERROR_FILE, "a") as myf:
                        myf.write(error + "\n")
                        continue
            #search for rahavard id
            req_response = requests.get(search_stock_by_name_rahavard_link+stock_name, headers=req_headers)
            if (req_response.status_code == 200):
                rahvard_data = json.loads(req_response.text)
                for each_stock in rahvard_data['data']:
                    if (each_stock['type_id'] == "1" and each_stock['unlisted_item'] == False and each_stock['trade_symbol'] == stock_name ):
                        rahavard_id = each_stock['entity_id']
                        stock_name_with_id = stock_name_with_id + "*" + rahavard_id
                        break
            else:
                    error = "Stock id not found for rahavard: " + stock_name
                    print (error)
                    with open (ERROR_FILE, "a") as myf:
                        myf.write(error + "\n")
            stocks_names_with_id.append(stock_name_with_id)

    print("Finished getting stocks names")
    with open(stocks_file, "a") as myf:
        for each_stock in stocks_names_with_id:
            myf.write(each_stock + "\n")
    return stocks_names_with_id


def get_history_of_stock():
    stocks = []
    print ("Start getting stocks data")
    output_dir = "stocks_history"
    src_link = "http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i="
    req_headers = {"Host": "google.com",
            "Cache-Control": "max-age=0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
            "HTTPS": "1",
            "DNT": "1",
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.8,en-GB;q=0.6,es;q=0.4",
            "If-Modified-Since": "Thu, 23 Jul 2015 20:31:28 GMT"
            }
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        with open(stocks_file, "r") as myf:
            for each_stock in myf:
                stocks.append(each_stock)
    except Exception as e:
        print (e)
        True

    for each_stock in stocks:
        print ("Downloading number: ", stocks.index(each_stock)+1, "/", len(stocks), end='\r')
        stock_id = each_stock.split("*")[0]
        output_file = output_dir + "/" + stock_id + "_stock_history.csv"

        req_response = requests.get(src_link + stock_id, headers=req_headers)
        if (req_response.status_code == 200):
            with open(output_file, "w") as wf:
                wf.write(req_response.text)
        else:
            error = "Could not get data of: " + each_stock
            print (error)
            with open (ERROR_FILE, "a") as myf:
                myf.write(error + "\n")
        print ("\nDownload finished")
    return True

def main():
    get_stocks()
    get_history_of_stock()


if __name__ == "__main__":
    main()
