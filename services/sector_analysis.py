def sector_breakdown(df, schema):
    sector_col = schema.get("sector")
    weight_col = schema.get("weight")

    if not sector_col or not weight_col:
        return None

    breakdown = df.groupby(sector_col)[weight_col].sum()

    return breakdown