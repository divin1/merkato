from unittest.mock import patch

import pandas as pd

from merkato.stock_monitor import (
    check_and_record_prices,
    get_stock_price,
    save_data,
    send_price_alerts,
)


class TestStockMonitor:
    @patch("merkato.stock_monitor.yf.Ticker")
    def test_get_stock_price_success(self, mock_ticker):
        """Test successful stock price fetching"""
        mock_history = pd.DataFrame({"Close": [150.50]})
        mock_ticker.return_value.history.return_value = mock_history

        price = get_stock_price("AAPL")

        assert price == 150.50
        mock_ticker.assert_called_once_with("AAPL")
        mock_ticker.return_value.history.assert_called_once_with(period="1d")

    @patch("merkato.stock_monitor.yf.Ticker")
    def test_get_stock_price_no_data(self, mock_ticker):
        """Test stock price fetching with empty data"""
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        price = get_stock_price("INVALID")

        assert price is None

    @patch("merkato.stock_monitor.yf.Ticker")
    def test_get_stock_price_exception(self, mock_ticker):
        """Test stock price fetching with exception"""
        mock_ticker.side_effect = Exception("API Error")

        price = get_stock_price("AAPL")

        assert price is None

    def test_save_data(self, tmp_path):
        """Test saving data to CSV"""
        data_file = tmp_path / "test_data.csv"

        df = pd.DataFrame({"timestamp": ["2024-01-01 12:00:00"], "symbol": ["AAPL"], "price": [150.0]})

        with patch("merkato.stock_monitor.DATA_FILE", str(data_file)):
            save_data(df)

            # Verify file was created and contains correct data
            assert data_file.exists()
            loaded_df = pd.read_csv(data_file)
            assert len(loaded_df) == 1
            assert loaded_df.iloc[0]["symbol"] == "AAPL"

    @patch("merkato.stock_monitor.get_stock_price")
    @patch("merkato.stock_monitor.load_or_create_data")
    @patch("merkato.stock_monitor.save_data")
    def test_check_and_record_prices_with_alert(self, mock_save, mock_load, mock_get_price):
        """Test checking prices and triggering alerts"""
        # Setup
        mock_load.return_value = pd.DataFrame(columns=["timestamp", "symbol", "price"])
        mock_get_price.return_value = 95.0  # Below target

        config = {"stocks": [{"symbol": "AAPL", "target_price": 100.0}]}

        # Execute
        alerts = check_and_record_prices(config)

        # Verify
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "AAPL"
        assert alerts[0]["current_price"] == 95.0
        assert alerts[0]["target_price"] == 100.0
        mock_save.assert_called_once()

    @patch("merkato.stock_monitor.get_stock_price")
    @patch("merkato.stock_monitor.load_or_create_data")
    @patch("merkato.stock_monitor.save_data")
    def test_check_and_record_prices_no_alert(self, mock_save, mock_load, mock_get_price):
        """Test checking prices without triggering alerts"""
        # Setup
        mock_load.return_value = pd.DataFrame(columns=["timestamp", "symbol", "price"])
        mock_get_price.return_value = 105.0  # Above target

        config = {"stocks": [{"symbol": "AAPL", "target_price": 100.0}]}

        # Execute
        alerts = check_and_record_prices(config)

        # Verify
        assert len(alerts) == 0
        mock_save.assert_called_once()

    @patch("merkato.stock_monitor.send_email")
    def test_send_price_alerts(self, mock_send_email):
        """Test sending price alert emails"""
        alerts = [
            {"symbol": "AAPL", "current_price": 95.0, "target_price": 100.0},
            {"symbol": "GOOGL", "current_price": 140.0, "target_price": 150.0},
        ]

        config = {"email": {"sender": "test@example.com"}}

        send_price_alerts(alerts, config)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[0][0] == "🎯 Stock Price Alert!"
        assert "AAPL" in call_args[0][1]
        assert "GOOGL" in call_args[0][1]
        assert "$95.00" in call_args[0][1]

    @patch("merkato.stock_monitor.send_email")
    def test_send_price_alerts_no_alerts(self, mock_send_email):
        """Test that no email is sent when there are no alerts"""
        alerts = []
        config = {"email": {"sender": "test@example.com"}}

        send_price_alerts(alerts, config)

        mock_send_email.assert_not_called()
