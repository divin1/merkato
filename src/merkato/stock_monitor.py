#!/usr/bin/env python3
"""
Merkato: Stock Monitor Bot
Checks stock prices hourly and sends email notifications when targets are met.
"""

from datetime import datetime

import pandas as pd
import yfinance as yf

from merkato.util import get_data_file, load_config, load_or_create_data, send_email


def get_stock_price(symbol):
    """Fetch current stock price using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            return data["Close"].iloc[-1]
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def save_data(df):
    """Save data to CSV"""
    df.to_csv(get_data_file(), index=False)


def check_and_record_prices(config):
    """Check all stocks and record prices"""
    df = load_or_create_data()
    timestamp = datetime.now().isoformat()
    alerts = []

    for stock in config["stocks"]:
        symbol = stock["symbol"]
        target_price = stock["target_price"]

        print(f"Checking {symbol}...")
        current_price = get_stock_price(symbol)

        if current_price is not None:
            # Record price
            new_row = pd.DataFrame({"timestamp": [timestamp], "symbol": [symbol], "price": [current_price]})
            df = pd.concat([df, new_row], ignore_index=True)

            # Check if alert should be sent
            if current_price <= target_price:
                alerts.append({"symbol": symbol, "current_price": current_price, "target_price": target_price})
                print(f"ALERT: {symbol} is at ${current_price:.2f} (target: ${target_price:.2f})")

    save_data(df)
    return alerts


def send_price_alerts(alerts, config):
    """Send email for price target alerts"""
    if not alerts:
        return

    body = "<h2>Stock Price Alerts</h2>"
    body += "<p>The following stocks have reached or dropped below your target price:</p>"
    body += "<ul>"

    for alert in alerts:
        body += f"<li><strong>{alert['symbol']}</strong>: "
        body += f"${alert['current_price']:.2f} "
        body += f"(Target: ${alert['target_price']:.2f})</li>"

    body += "</ul>"

    send_email("🎯 Stock Price Alert!", body, config)


def main():
    """Main execution function"""
    config = load_config()

    # Check prices and get alerts
    alerts = check_and_record_prices(config)

    # Send price alerts if any
    if alerts:
        send_price_alerts(alerts, config)


if __name__ == "__main__":
    main()
