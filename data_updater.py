import yfinance as yf
import json
from datetime import datetime
import pytz

def fetch_data():
    # 設定台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz)
    
    # 1. 抓取美股與 ADR 數據
    tickers = {
        'TSM': 'tsmcAdr',
        '^SOX': 'sox',
        '^IXIC': 'nasdaq',
        '^DJI': 'dow',
        'NVDA': 'nvda'
    }
    
    results = {}
    for ticker, key in tickers.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="2d")
            close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((close - prev_close) / prev_close) * 100
            results[key] = round(change_pct, 2)
        except:
            results[key] = 0.0

    # 2. 抓取匯率 (USD/TWD)
    try:
        usdtwd = yf.Ticker("TWD=X")
        currency_hist = usdtwd.history(period="2d")
        current_rate = round(currency_hist['Close'].iloc[-1], 3)
        prev_rate = round(currency_hist['Close'].iloc[-2], 3)
    except:
        current_rate, prev_rate = 32.0, 32.0

    # 3. 整合數據結構
    output = {
        "lastUpdate": now.strftime("%Y/%m/%d %H:%M:%S"),
        "usMarket": results,
        "currency": {
            "current": current_rate,
            "prev1600": prev_rate,
            "change": round(current_rate - prev_rate, 3)
        },
        "marketNews": f"自動更新：美股{ '上漲' if results['nasdaq'] > 0 else '回檔' }，台幣報 {current_rate}。",
        "tradingPlan": {
            "openHigh": "ADR 表現強勁，開高不追，觀察 9:15 支撐。",
            "openLow": "觀察匯率是否貶破 32 元關卡。",
            "stopLoss": "昨日低點為最終防線。"
        }
    }

    # 寫入 json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_data()