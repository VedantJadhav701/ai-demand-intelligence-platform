"""
Generator script for 120-day sample sales dataset.
"""

import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range(start="2025-10-01", end="2026-01-31", freq="D")
stores = ["STORE_01", "STORE_02"]
products = ["PROD_01", "PROD_02"]

rows = []
for d in dates:
    is_wknd = 1 if d.dayofweek >= 5 else 0
    is_hol = (
        1 if d.strftime("%Y-%m-%d") in ["2025-11-27", "2025-12-25", "2026-01-01"] else 0
    )
    for s in stores:
        s_mult = 1.2 if s == "STORE_01" else 0.9
        stype = "Supermarket" if s == "STORE_01" else "Hypermarket"
        reg = "North" if s == "STORE_01" else "South"
        for p in products:
            p_mult = 1.5 if p == "PROD_01" else 1.0
            pcat = "Electronics" if p == "PROD_01" else "Apparel"
            base_price = 20.0 if p == "PROD_01" else 15.0

            promo = 1 if np.random.rand() > 0.8 else 0
            disc = 0.1 if promo else 0.0
            price = base_price * (1 - disc)

            base_units = int(
                80 * s_mult * p_mult
                + is_wknd * 25
                + promo * 30
                + is_hol * 40
                + np.random.randint(-10, 15)
            )
            units_sold = max(5, base_units)
            revenue = round(units_sold * price, 2)
            inventory = max(50, 500 - units_sold * 2 + np.random.randint(-20, 20))

            rows.append(
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "store_id": s,
                    "product_id": p,
                    "units_sold": units_sold,
                    "revenue": revenue,
                    "price": price,
                    "discount": disc,
                    "promotion": promo,
                    "holiday": is_hol,
                    "store_type": stype,
                    "product_category": pcat,
                    "inventory": inventory,
                    "region": reg,
                }
            )

df = pd.DataFrame(rows)
df.to_csv("data/raw/sample_sales_data.csv", index=False)
print(f"Successfully generated {len(df)} rows of sales data!")
