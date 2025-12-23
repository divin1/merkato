#!/usr/bin/env python3
"""
Test script to verify the stock monitor works locally before deploying
"""

import merkato.stock_monitor as stock_monitor
from merkato.util import load_config


def test_config():
    """Test config loading"""
    print("Testing configuration...")
    try:
        config = load_config()
        print("✓ Config loaded successfully")
        print(f"  - Monitoring {len(config['stocks'])} stocks")
        print(f"  - Email configured for: {config['email']['sender']}")
        return config
    except Exception as e:
        print(f"✗ Config error: {e}")
        return None


def test_price_fetch():
    """Test fetching stock prices"""
    print("\nTesting price fetching...")
    test_symbols = ["SPY", "AAPL"]

    for symbol in test_symbols:
        price = stock_monitor.get_stock_price(symbol)
        if price:
            print(f"✓ {symbol}: ${price:.2f}")
        else:
            print(f"✗ Failed to fetch {symbol}")


def test_data_storage():
    """Test CSV data storage"""
    print("\nTesting data storage...")
    try:
        df = stock_monitor.load_or_create_data()
        print("✓ Data file loaded/created")
        print(f"  - Current records: {len(df)}")
        if len(df) > 0:
            print(f"  - Latest entry: {df.iloc[-1]['timestamp']}")
        return True
    except Exception as e:
        print(f"✗ Data storage error: {e}")
        return False


def test_email_config():
    """Test email configuration (doesn't send)"""
    print("\nTesting email configuration...")
    try:
        config = load_config()
        email_config = config["email"]

        required_fields = ["sender", "password", "recipient", "smtp_server", "smtp_port"]
        missing = [f for f in required_fields if not email_config.get(f)]

        if missing:
            print(f"✗ Missing email fields: {', '.join(missing)}")
            return False

        print("✓ Email config complete")
        print(f"  - Sender: {email_config['sender']}")
        print(f"  - Recipient: {email_config['recipient']}")
        print(f"  - SMTP: {email_config['smtp_server']}:{email_config['smtp_port']}")
        print("\n⚠ Note: Email sending not tested. Run the main script to test actual sending.")
        return True
    except Exception as e:
        print(f"✗ Email config error: {e}")
        return False


def main():
    print("=" * 60)
    print("Stock Monitor Bot - Test Suite")
    print("=" * 60)

    # Run tests
    config = test_config()
    if config:
        test_price_fetch()
        test_data_storage()
        test_email_config()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
