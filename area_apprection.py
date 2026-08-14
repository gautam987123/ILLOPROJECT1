from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "Bengaluru_House_Data.csv")
avg_price=df.groupby('location')['price'].mean()
number_avail=df.groupby('location').size().sort_values(ascending=False)
def convert_sqft(x):
    if '-' in str(x):
        vals = str(x).split('-')
        return (float(vals[0]) + float(vals[1])) / 2
    try:
        return float(x)
    except:
        return None
df['total_sqft'] = df['total_sqft'].apply(convert_sqft)
df['total_sqft'] = pd.to_numeric(df['total_sqft'], errors='coerce')
df['price_per_sqft'] = df['price']*100000 / df['total_sqft']
df['bhk']=pd.to_numeric(df['size'].str.split().str[0])
avg_bhk=df.groupby('location')['bhk'].mean()
avg_psf = df.groupby('location')['price_per_sqft'].mean()
score_df=pd.DataFrame({'avgprice':avg_price,'avl':number_avail,'price':avg_psf,'bhk':avg_bhk})
for col in score_df.columns:
    score_df[col+'score']=((score_df[col]-score_df[col].min())/(score_df[col].max()-score_df[col].min()))*10
score_df['final_score']=score_df['pricescore']*0.4+score_df['avlscore']*0.3+score_df['avgpricescore']*0.2+score_df['bhkscore']*0.1
score_df_sorted = score_df.sort_values(by='final_score', ascending=False)
print(score_df_sorted.head(10))
def user_input(location):
    return score_df.loc[location, 'final_score']

def give_rate_roi(location, row):
    if location in score_df.index:
        base_score = score_df.loc[location, 'final_score']

        # detect area_type from encoded columns
        if row.get("area_type_Plot Area", 0) == 1:
            multiplier = 1.2
        elif row.get("area_type_Carpet Area", 0) == 1:
            multiplier = 1.1
        elif row.get("area_type_Built-up Area", 0) == 1:
            multiplier = 1.0
        else:
            multiplier = 0.9

        score = base_score * multiplier
        rate = 0.03 + (score * 0.01)

        return min(rate, 0.12)
    else:
        return 0.05