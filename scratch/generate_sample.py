import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range(start='2026-01-01', end='2026-08-25', freq='D')
stores = ['S001', 'S002', 'STORE_17']
products = ['P001', 'P002', 'PRODUCT_A']

records = []
for s in stores:
    st_type = 'Supermarket' if s == 'S001' else ('Urban' if s == 'S002' else 'High_Volume')
    for p in products:
        p_cat = 'Grocery' if p == 'P001' else ('Electronics' if p == 'P002' else 'Apparel')
        base_price = 100.0 if p == 'P001' else (250.0 if p == 'P002' else 45.0)
        base_units = 120 if p == 'P001' else (40 if p == 'P002' else 85)
        
        for d in dates:
            dow = d.dayofweek
            is_weekend = 1 if dow >= 5 else 0
            promo = np.random.choice([0, 1], p=[0.8, 0.2])
            disc = np.random.choice([0, 10, 15, 20], p=[0.7, 0.15, 0.1, 0.05]) if promo == 1 else 0
            
            noise = int(np.random.normal(0, 8))
            weekend_boost = 15 if is_weekend else 0
            promo_boost = 25 if promo == 1 else 0
            
            units = int(max(5, base_units + weekend_boost + promo_boost + noise))
            price = round(base_price * (1 - disc / 100.0), 2)
            inventory = int(max(0, 500 - (d.day % 15) * 20 + np.random.randint(-10, 10)))
            
            records.append({
                'date': d.strftime('%Y-%m-%d'),
                'store_id': s,
                'product_id': p,
                'units_sold': units,
                'price': base_price,
                'discount': disc,
                'promotion': promo,
                'store_type': st_type,
                'product_category': p_cat,
                'inventory': inventory
            })

df = pd.DataFrame(records)
df.to_csv('data/sample_data.csv', index=False)
df.to_csv('frontend/public/sample_data.csv', index=False)
print('Successfully generated data/sample_data.csv and frontend/public/sample_data.csv with', len(df), 'rows.')
