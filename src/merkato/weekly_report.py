# !/usr/bin/env python3
"""
Merkato: Weekly Report Bot
Sends weekly trend reports every Thursday.
"""

from datetime import datetime, timedelta

import pandas as pd

from merkato.util import load_config, load_or_create_data, send_email


def calculate_weekly_trends(df, symbol):
    """Calculate 7-day trend for a symbol"""
    seven_days_ago = datetime.now() - timedelta(days=7)

    symbol_data = df[df["symbol"] == symbol].copy()
    symbol_data["timestamp"] = pd.to_datetime(symbol_data["timestamp"])
    recent_data = symbol_data[symbol_data["timestamp"] >= seven_days_ago]

    if len(recent_data) < 2:
        return None

    # Sort by timestamp to ensure correct order
    recent_data = recent_data.sort_values("timestamp")

    first_price = recent_data.iloc[0]["price"]
    last_price = recent_data.iloc[-1]["price"]
    change = last_price - first_price
    percent_change = (change / first_price) * 100

    return {
        "symbol": symbol,
        "start_price": first_price,
        "end_price": last_price,
        "change": change,
        "percent_change": percent_change,
        "min_price": recent_data["price"].min(),
        "max_price": recent_data["price"].max(),
    }


def send_weekly_report(config):
    """Send weekly trend report"""
    df = load_or_create_data()

    if df.empty:
        print("No data available for weekly report")
        return

    body = "<h2>Weekly Stock Trends Report</h2>"
    body += f"<p>Report for the past 7 days (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})</p>"
    body += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>"
    body += "<tr style='background-color: #f0f0f0;'>"
    body += "<th>Symbol</th><th>Start Price</th><th>End Price</th>"
    body += "<th>Change</th><th>% Change</th><th>Week Low</th><th>Week High</th>"
    body += "</tr>"

    for stock in config["stocks"]:
        trend = calculate_weekly_trends(df, stock["symbol"])
        if trend:
            color = "green" if trend["change"] >= 0 else "red"
            arrow = "▲" if trend["change"] >= 0 else "▼"

            body += "<tr>"
            body += f"<td><strong>{trend['symbol']}</strong></td>"
            body += f"<td>${trend['start_price']:.2f}</td>"
            body += f"<td>${trend['end_price']:.2f}</td>"
            body += f"<td style='color: {color};'>{arrow} ${abs(trend['change']):.2f}</td>"
            body += f"<td style='color: {color};'>{trend['percent_change']:+.2f}%</td>"
            body += f"<td>${trend['min_price']:.2f}</td>"
            body += f"<td>${trend['max_price']:.2f}</td>"
            body += "</tr>"

    body += "</table>"

    send_email("📊 Weekly Stock Trends Report", body, config)


def main():
    config = load_config()
    send_weekly_report(config)


if __name__ == "__main__":
    main()
