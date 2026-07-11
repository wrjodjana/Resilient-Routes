import pandas as pd
df = pd.read_csv('bridges.csv')
df_filtered = df[['LATITUDE', 'LONGITUDE', 'LOCATION_009', 'STRUCTURE_NUMBER_008']]
df_filtered.columns = ['lat', 'lng', 'location', 'id']
df_filtered.to_json('bridges.json', orient='records')