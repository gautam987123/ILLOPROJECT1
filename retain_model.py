from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

import pandas as pd
import joblib

from database import get_connection


# =========================================================
# 1. LOAD ORIGINAL DATASET
# =========================================================

df = pd.read_csv(
    r"C:\Users\HP\Downloads\archive\Bengaluru_House_Data.csv"
)

print("Original records:", len(df))


# =========================================================
# 2. LOAD USER-ADDED DATA FROM MYSQL
# =========================================================

conn = get_connection()

new_data = pd.read_sql(
    """
    SELECT
        location,
        area_type,
        bhk,
        sqft AS total_sqft,
        bath,
        balcony,
        price
    FROM properties
    """,
    conn
)

conn.close()

print("User-added records:", len(new_data))


# =========================================================
# 3. PREPARE ORIGINAL DATASET
# =========================================================

df = df.drop_duplicates()

df = df.drop(
    "society",
    axis=1,
    errors="ignore"
)

df = df.drop(
    "availability",
    axis=1,
    errors="ignore"
)


# =========================================================
# 4. CREATE BHK FOR ORIGINAL DATASET
# =========================================================

df["bhk"] = pd.to_numeric(
    df["size"]
    .astype(str)
    .str.split()
    .str[0],
    errors="coerce"
)

df = df.drop(
    "size",
    axis=1
)


# =========================================================
# 5. COMBINE ORIGINAL DATA + MYSQL DATA
# =========================================================

df = pd.concat(
    [df, new_data],
    ignore_index=True
)

df = df.drop_duplicates()

print("Combined records:", len(df))


# =========================================================
# 6. CLEAN LOCATION
# =========================================================

df["location"] = (
    df["location"]
    .astype(str)
    .str.strip()
)

df["location"] = df["location"].replace(
    ["nan", "", "None"],
    "other"
)

# IMPORTANT:
# We DO NOT remove locations with few records.
#
# Therefore:
# JP Nagar        stays JP Nagar
# Whitefield      stays Whitefield
# Kengeri         stays Kengeri
# Kumvepunagar    stays Kumvepunagar
# New Area XYZ    stays New Area XYZ

print(
    "Unique locations:",
    df["location"].nunique()
)


# =========================================================
# 7. CLEAN AREA TYPE
# =========================================================

df["area_type"] = (
    df["area_type"]
    .astype(str)
    .str.strip()
)

df["area_type"] = df["area_type"].replace(
    ["nan", "", "None"],
    "other"
)


# =========================================================
# 8. CONVERT SQFT
# =========================================================

def convert_sqft(x):

    if "-" in str(x):

        vals = str(x).split("-")

        try:
            return (
                float(vals[0]) +
                float(vals[1])
            ) / 2

        except:
            return None

    try:
        return float(x)

    except:
        return None


df["total_sqft"] = (
    df["total_sqft"]
    .apply(convert_sqft)
)

df["total_sqft"] = pd.to_numeric(
    df["total_sqft"],
    errors="coerce"
)


# =========================================================
# 9. CLEAN MISSING VALUES
# =========================================================

df = df.dropna(
    subset=[
        "location",
        "area_type",
        "bhk",
        "total_sqft",
        "bath",
        "balcony",
        "price"
    ]
)


# =========================================================
# 10. ONE-HOT ENCODE LOCATION
# =========================================================

df = pd.get_dummies(
    df,
    columns=["location"],
    drop_first=True
)


# =========================================================
# 11. ONE-HOT ENCODE AREA TYPE
# =========================================================

df = pd.get_dummies(
    df,
    columns=["area_type"],
    drop_first=True
)


# =========================================================
# 12. FEATURES AND TARGET
# =========================================================

x = df.drop(
    columns=[
        "price",
        "price_per_sqft"
    ],
    errors="ignore"
)

y = df["price"]


# =========================================================
# 13. TRAIN / TEST SPLIT
# =========================================================

x_train, x_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.1,
    random_state=42
)


# =========================================================
# 14. TRAIN RANDOM FOREST
# =========================================================

rf = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

rf.fit(
    x_train,
    y_train
)


# =========================================================
# 15. EVALUATE MODEL
# =========================================================

pred = rf.predict(x_test)

r2 = r2_score(
    y_test,
    pred
)

mae = mean_absolute_error(
    y_test,
    pred
)

rmse = mean_squared_error(
    y_test,
    pred
) ** 0.5


print("\n================================")
print("NEW MODEL EVALUATION")
print("================================")

print("R2:", r2)
print("MAE:", mae)
print("RMSE:", rmse)


# =========================================================
# 16. SAVE NEW MODEL
# =========================================================

joblib.dump(
    rf,
    "roimodel.pkl"
)

joblib.dump(
    x.columns.tolist(),
    "columns.pkl"
)


# =========================================================
# 17. COMPLETE
# =========================================================

print("\n================================")
print("MODEL RETRAINING COMPLETE")
print("================================")

print(
    "Total training records:",
    len(x)
)

print(
    "Total features:",
    len(x.columns)
)

print(
    "Unique locations:",
    df["location_"].nunique()
    if "location_" in df.columns
    else "Check encoded columns"
)

print("New model saved as: roimodel.pkl")
print("New columns saved as: columns.pkl")