from fastapi import FastAPI, Response, Request
import requests
import sympy
import json

app = FastAPI()

def get_airport_weather(iata_code):
    #  suradnice letiska hladanie
    url1 = "https://www.airport-data.com/api/ap_info.json?iata=" + iata_code
    res1 = requests.get(url1, verify=False)
    data1 = res1.json()
    
    lat = data1["latitude"]
    lon = data1["longitude"]
    
    # pocasie letiska cez lat a lon
    url2 = "https://api.open-meteo.com/v1/forecast?latitude=" + str(lat) + "&longitude=" + str(lon) + "&current_weather=true"
    res2 = requests.get(url2)
    data2 = res2.json()
    
    return data2["current_weather"]["temperature"]

def fetch_stock(ticker):
    # yahoo api finance
    link = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker
    req = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    parsed = req.json()
    
    price = parsed["chart"]["result"][0]["meta"]["regularMarketPrice"]
    return price

@app.get("/")
def api_root(request: Request, queryAirportTemp=None, queryStockPrice=None, queryEval=None):
    
    # argument count check - musi byt len jeden argument
    arg_count = 0
    if queryAirportTemp is not None:
        arg_count = arg_count + 1
    if queryStockPrice is not None:
        arg_count = arg_count + 1
    if queryEval is not None:
        arg_count = arg_count + 1
        
    if arg_count != 1:
        return Response(status_code=400) # error 400 ak zle 

    try:
        final_result = 0
        
        # podla toho aky je argument zavolame funkciu
        if queryAirportTemp is not None:
            final_result = get_airport_weather(queryAirportTemp)
            
        elif queryStockPrice is not None:
            final_result = fetch_stock(queryStockPrice)
            
        elif queryEval is not None:
            # sympy 
            expr = sympy.sympify(queryEval)
            final_result = float(expr.evalf())
            
    except Exception as e:
        print("err:", str(e))
        return Response(status_code=400)

    # zistime ci chcu xml alebo json
    acc_header = request.headers.get("accept", "")

    if "application/xml" in acc_header or "text/xml" in acc_header:
        # zlozime xml string
        xml_out = "<result>" + str(final_result) + "</result>"
        return Response(content=xml_out, media_type="application/xml")

    # inak vratime json cize len cislo
    return Response(content=json.dumps(final_result), media_type="application/json")
