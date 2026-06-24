"""
load_data.py
Phase 1: Load and clean the data.

Two jobs:
1. load_tickets / clean_tickets -> the ANALYTICS data (real customer support data).
   Computes response time and keeps the columns that carry real relationships.
2. load_complaints -> the NLP-TRAINING data (real CFPB complaint narratives).
"""

import pandas as pd


def load_tickets(path="data/tickets.csv"):
    """Load the raw analytics data from a CSV file."""
    return pd.read_csv(path)


def clean_tickets(df):
    """
    Clean the analytics data and compute response time.

    Returns two tables:
    - all_tickets:    every valid ticket (used for categorising + category tests)
    - rated_tickets:  tickets that have a CSAT score (used for satisfaction analysis)
    """
    df = df.copy()

    # Friendlier column names for the dashboard.
    df = df.rename(columns={
        "channel_name": "Channel",
        "category": "Category",
        "Sub-category": "Sub Category",
        "Product_category": "Product Category",
        "Item_price": "Item Price",
        "Tenure Bucket": "Agent Tenure",
        "Agent Shift": "Agent Shift",
        "CSAT Score": "CSAT Score",
    })

    # The two time columns are timestamps. Convert them so we can subtract.
    df["Issue_reported at"] = pd.to_datetime(df["Issue_reported at"], errors="coerce", dayfirst=True)
    df["issue_responded"] = pd.to_datetime(df["issue_responded"], errors="coerce", dayfirst=True)

    # Response time in hours = when responded minus when reported.
    df["Response Hours"] = (
        (df["issue_responded"] - df["Issue_reported at"]).dt.total_seconds() / 3600
    )

    # Drop impossible values: negative response time, or absurdly large (data errors).
    df = df[(df["Response Hours"] >= 0) & (df["Response Hours"] < 1000)]

    # rated_tickets = those with a satisfaction score (for CSAT analysis).
    rated = df[df["CSAT Score"].notna()].copy()

    return df, rated


def load_complaints(path="data/complaints.csv"):
    """
    Load and clean the CFPB complaint data for NLP TRAINING only.
    Real human-written complaint text with verified category labels.
    """
    df = pd.read_csv(path)
    keep = ["product_5", "narrative"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df = df.rename(columns={"product_5": "Category", "narrative": "Complaint Text"})
    df = df.dropna()
    return df


# Runs only when you execute this file directly (for testing).
if __name__ == "__main__":
    raw = load_tickets()
    print("Columns in the data:")
    print(list(raw.columns))
    print()

    all_tickets, rated_tickets = clean_tickets(raw)

    print(f"Total valid tickets:        {len(all_tickets)}")
    print(f"Tickets with CSAT score:    {len(rated_tickets)}")
    print()
    print("Sample response times (hours):")
    print(all_tickets["Response Hours"].head(5).round(1).tolist())
    print()
    print("CSAT score spread:")
    print(rated_tickets["CSAT Score"].value_counts().sort_index().to_dict())