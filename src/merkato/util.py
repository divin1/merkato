import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv

# Configuration
DATA_FILE = "data/stock_data.csv"
CONFIG_FILE = "config.json"


# Utility functions
def load_config():
    """Load configuration from config.json and environment variables"""
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    # Set email settings from environment variables (for GitHub Actions)
    load_dotenv()

    if (
        not os.getenv("EMAIL_SENDER")
        or not os.getenv("EMAIL_PASSWORD")
        or not os.getenv("EMAIL_RECIPIENT")
        or not os.getenv("EMAIL_SMTP_SERVER")
        or not os.getenv("EMAIL_SMTP_PORT")
    ):
        raise ValueError("Email configuration environment variables are not fully set.")

    config.setdefault("email", {})
    config["email"]["sender"] = os.getenv("EMAIL_SENDER")
    config["email"]["password"] = os.getenv("EMAIL_PASSWORD")
    config["email"]["recipient"] = os.getenv("EMAIL_RECIPIENT")
    config["email"]["smtp_server"] = os.getenv("EMAIL_SMTP_SERVER")
    config["email"]["smtp_port"] = int(os.getenv("EMAIL_SMTP_PORT"))

    return config


def load_or_create_data():
    """Load existing data or create new DataFrame"""
    # Ensure data directory exists
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["timestamp", "symbol", "price"])


def send_email(subject, body, config):
    """Send email notification"""
    sender_email = config["email"]["sender"]
    sender_password = config["email"]["password"]
    recipient_email = config["email"]["recipient"]
    smtp_server = config["email"]["smtp_server"]
    smtp_port = config["email"]["smtp_port"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")
