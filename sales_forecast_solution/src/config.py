SEED = 20261022
AS_OF_DATES = ["2026-01-31", "2026-04-30", "2026-07-31", "2026-10-31",
               "2027-01-31", "2027-04-30", "2027-07-31", "2027-10-31"]
STAGES = [
    ("Prospecting", 0.05, 1),
    ("Qualification", 0.15, 2),
    ("Discovery", 0.30, 3),
    ("Proposal", 0.55, 4),
    ("Negotiation", 0.75, 5),
    ("Closed Won", 1.00, 6),
    ("Closed Lost", 0.00, 7),
]
CURRENCIES = ["USD", "INR", "EUR", "GBP"]
PRODUCTS = ["Analytics Platform", "Cloud Subscription", "Security Suite", "AI Services", "Support Package"]
REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
ACTIVITY_TYPES = ["Email", "Call", "Meeting", "Demo", "Proposal Sent"]
