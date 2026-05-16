COLUMN_ALIASES = {
    "ticker": [
        "ticker",
        "symbol",
        "stock",
        "asset",
        "instrument"
    ],

    "weight": [
        "weight",
        "allocation",
        "percent",
        "qty",
        "quantity"
    ],

    "shares": [
        "shares"
    ],

    "buy_price": [
        "buy_price",
        "buyprice",
        "avg_cost",
        "average_price",
        "avg._cost",
        "cost_basis"
    ],

    "sector": [
        "sector",
        "industry"
    ]
}


def detect_schema(df):
    mapping = {}

    cols = [c.lower().strip() for c in df.columns]

    for standard, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            for col in cols:
                if alias == col:
                    mapping[standard] = col

    return mapping