from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from area_apprection import give_rate_roi
import joblib
from sklearn.preprocessing import LabelEncoder
import pandas as pd
df=pd.read_csv(r"C:\Users\HP\Downloads\archive\Bengaluru_House_Data.csv")
df = df.drop_duplicates()

df = df.drop("society", axis=1)
df=df.drop("availability",axis=1)
df['bhk'] = pd.to_numeric(
    df['size'].str.split().str[0],

    errors='coerce'
)
df=df.drop('size',axis=1)
df['location'] = df['location'].fillna('other')
loc_counts = df['location'].value_counts()
top_locations = loc_counts[loc_counts > 10].index

df['location'] = df['location'].apply(
    lambda x: x if x in top_locations else 'other'
)

df = pd.get_dummies(df, columns=['location'], drop_first=True)
df = pd.get_dummies(df, columns=['area_type'], drop_first=True)

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
df = df.dropna(subset=['total_sqft'])
df = df.dropna()

rf=RandomForestRegressor(n_estimators=200,random_state=42)
x = df.drop(columns=['price', 'price_per_sqft'], errors='ignore')
y=df['price']
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.1,random_state=42)
rf.fit(x_train,y_train)
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

pred = rf.predict(x_test)

print("R2:", r2_score(y_test, pred))
print("MAE:", mean_absolute_error(y_test, pred))
print("RMSE:", mean_squared_error(y_test, pred) ** 0.5)
joblib.dump(rf,"roimodel.pkl")
joblib.dump(x.columns, "columns.pkl")

