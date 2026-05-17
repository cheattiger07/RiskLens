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
        for col in cols:
            for alias in aliases:
                if alias in col:   # 🔥 FIX: substring match
                    mapping[standard] = col
                    break

    return mapping