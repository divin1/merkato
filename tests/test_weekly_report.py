from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd

from merkato.weekly_report import calculate_weekly_trends, send_weekly_report


class TestWeeklyReport:
    def test_calculate_weekly_trends_success(self):
        """Test weekly trend calculation with sufficient data"""
        now = datetime.now() + timedelta(hours=1)  # Ensure current time is ahead of data timestamps
        df = pd.DataFrame(
            {
                "timestamp": [
                    (now - timedelta(days=7)).isoformat(),
                    (now - timedelta(days=5)).isoformat(),
                    (now - timedelta(days=3)).isoformat(),
                    now.isoformat(),
                ],
                "symbol": ["AAPL", "AAPL", "AAPL", "AAPL"],
                "price": [100.0, 105.0, 102.0, 110.0],
            }
        )

        trend = calculate_weekly_trends(df, "AAPL")

        assert trend is not None
        assert trend["symbol"] == "AAPL"
        assert trend["start_price"] == 100.0
        assert trend["end_price"] == 110.0
        assert trend["change"] == 10.0
        assert trend["percent_change"] == 10.0
        assert trend["min_price"] == 100.0
        assert trend["max_price"] == 110.0

    def test_calculate_weekly_trends_price_drop(self):
        """Test weekly trend calculation with price decrease"""
        now = datetime.now() + timedelta(hours=1)  # Ensure current time is ahead of data timestamps
        df = pd.DataFrame(
            {
                "timestamp": [
                    (now - timedelta(days=7)).isoformat(),
                    now.isoformat(),
                ],
                "symbol": ["AAPL", "AAPL"],
                "price": [100.0, 90.0],
            }
        )

        trend = calculate_weekly_trends(df, "AAPL")

        assert trend is not None
        assert trend["change"] == -10.0
        assert trend["percent_change"] == -10.0

    def test_calculate_weekly_trends_insufficient_data(self):
        """Test with insufficient data (less than 2 records)"""
        df = pd.DataFrame({"timestamp": [datetime.now().isoformat()], "symbol": ["AAPL"], "price": [100.0]})

        trend = calculate_weekly_trends(df, "AAPL")

        assert trend is None

    def test_calculate_weekly_trends_old_data(self):
        """Test with data older than 7 days"""
        old_date = datetime.now() - timedelta(days=10)
        df = pd.DataFrame(
            {
                "timestamp": [
                    (old_date - timedelta(days=2)).isoformat(),
                    (old_date - timedelta(days=1)).isoformat(),
                ],
                "symbol": ["AAPL", "AAPL"],
                "price": [100.0, 105.0],
            }
        )

        trend = calculate_weekly_trends(df, "AAPL")

        # Should return None because no data in last 7 days
        assert trend is None

    def test_calculate_weekly_trends_wrong_symbol(self):
        """Test with data for different symbol"""
        now = datetime.now()
        df = pd.DataFrame(
            {
                "timestamp": [
                    (now - timedelta(days=7)).isoformat(),
                    now.isoformat(),
                ],
                "symbol": ["GOOGL", "GOOGL"],
                "price": [100.0, 110.0],
            }
        )

        trend = calculate_weekly_trends(df, "AAPL")

        assert trend is None

    @patch("merkato.weekly_report.send_email")
    @patch("merkato.weekly_report.load_or_create_data")
    def test_send_weekly_report_with_data(self, mock_load_data, mock_send_email):
        """Test sending weekly report with data"""
        now = datetime.now() + timedelta(hours=1)  # Ensure current time is ahead of data timestamps
        mock_load_data.return_value = pd.DataFrame(
            {
                "timestamp": [
                    (now - timedelta(days=7)).isoformat(),
                    now.isoformat(),
                ],
                "symbol": ["AAPL", "AAPL"],
                "price": [100.0, 110.0],
            }
        )

        config = {"stocks": [{"symbol": "AAPL"}], "email": {"sender": "test@example.com"}}

        send_weekly_report(config)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[0][0] == "📊 Weekly Stock Trends Report"
        assert "AAPL" in call_args[0][1]
        assert "$100.00" in call_args[0][1]
        assert "$110.00" in call_args[0][1]

    @patch("merkato.weekly_report.send_email")
    @patch("merkato.weekly_report.load_or_create_data")
    def test_send_weekly_report_empty_data(self, mock_load_data, mock_send_email):
        """Test weekly report with no data"""
        mock_load_data.return_value = pd.DataFrame()

        config = {"stocks": [{"symbol": "AAPL"}], "email": {"sender": "test@example.com"}}

        send_weekly_report(config)

        # Should not send email when no data
        mock_send_email.assert_not_called()

    @patch("merkato.weekly_report.send_email")
    @patch("merkato.weekly_report.load_or_create_data")
    def test_send_weekly_report_multiple_stocks(self, mock_load_data, mock_send_email):
        """Test weekly report with multiple stocks"""
        now = datetime.now() + timedelta(hours=1)  # Ensure current time is ahead of data timestamps
        mock_load_data.return_value = pd.DataFrame(
            {
                "timestamp": [
                    (now - timedelta(days=7)).isoformat(),
                    now.isoformat(),
                    (now - timedelta(days=7)).isoformat(),
                    now.isoformat(),
                ],
                "symbol": ["AAPL", "AAPL", "GOOGL", "GOOGL"],
                "price": [100.0, 110.0, 150.0, 145.0],
            }
        )

        config = {"stocks": [{"symbol": "AAPL"}, {"symbol": "GOOGL"}], "email": {"sender": "test@example.com"}}

        send_weekly_report(config)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        body = call_args[0][1]

        # Check both stocks are in the email
        assert "AAPL" in body
        assert "GOOGL" in body
        assert "$110.00" in body  # AAPL end price
        assert "$145.00" in body  # GOOGL end price
