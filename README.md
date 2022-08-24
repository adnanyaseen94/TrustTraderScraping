# TrustATrader Scraping
Scrap www.trustatrader.com search using **Python3** and **BeautifulSoup** library.

The program takes the search url as an input and scrap the the pages to find companies details: 
- company name
- tel number
- mob number
- location
- post code
- rating 


**--url** trustatrader.com search url

**--all_pages** optional command line argument to specify if all pages needs to be scanned.

**--file_path** opional command line argument to specify the directory where to save search_result.csv file, by default saved in the project directory.

How to run examples:
```
python3 trusttrader.py --all_pages --file_path /home/adnan/ --url "https://www.trustatrader.com/search?trade_name=Builder&search_trade_id=5b4cbdcb8811d346b846d974&location_str=Bury+St+Edmunds&lat=&lon=&trader=&search_trader_id="
```

```
python3 trusttrader.py --url "https://www.trustatrader.com/search?trade_name=Builder&search_trade_id=5b4cbdcb8811d346b846d974&location_str=Bury+St+Edmunds&lat=&lon=&trader=&search_trader_id="
```
