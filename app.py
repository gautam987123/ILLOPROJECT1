from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from database import get_connection

from excuteroi import (
    ROI,
    fair_price,
    get_verdict,
    rateofapp,
    buy_vs_rent
)

app = Flask(__name__)
CORS(app)

DATASET_PATH = r"C:\Users\HP\Downloads\archive\Bengaluru_House_Data.csv"


def load_original_data():

    df = pd.read_csv(DATASET_PATH)

    df = df.drop_duplicates()

    df = df.drop(
        ["society", "availability"],
        axis=1,
        errors="ignore"
    )

    if "size" in df.columns:

        df["bhk"] = pd.to_numeric(
            df["size"]
            .astype(str)
            .str.split()
            .str[0],
            errors="coerce"
        )

        df = df.drop("size", axis=1)

    df["location"] = (
        df["location"]
        .fillna("other")
        .astype(str)
        .str.strip()
    )

    def convert_sqft(value):

        try:

            value = str(value)

            if "-" in value:

                values = value.split("-")

                return (
                    float(values[0]) +
                    float(values[1])
                ) / 2

            return float(value)

        except:

            return None

    df["total_sqft"] = (
        df["total_sqft"]
        .apply(convert_sqft)
    )

    return df


def load_mysql_data():

    try:

        conn = get_connection()

        query = """
            SELECT
                id,
                location,
                area_type,
                bhk,
                sqft AS total_sqft,
                bath,
                balcony,
                price,
                created_at
            FROM properties
        """

        df = pd.read_sql(
            query,
            conn
        )

        conn.close()

        return df

    except Exception as e:

        print(
            "MySQL loading error:",
            e
        )

        return pd.DataFrame(
            columns=[
                "location",
                "area_type",
                "bhk",
                "total_sqft",
                "bath",
                "balcony",
                "price"
            ]
        )


def get_combined_data():

    original = load_original_data()

    mysql_data = load_mysql_data()

    required_columns = [
        "location",
        "area_type",
        "bhk",
        "total_sqft",
        "bath",
        "balcony",
        "price"
    ]

    original = original[
        [
            column
            for column in required_columns
            if column in original.columns
        ]
    ]

    mysql_data = mysql_data[
        [
            column
            for column in required_columns
            if column in mysql_data.columns
        ]
    ]

    combined = pd.concat(
        [
            original,
            mysql_data
        ],
        ignore_index=True
    )

    combined["location"] = (
        combined["location"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    combined["price"] = pd.to_numeric(
        combined["price"],
        errors="coerce"
    )

    combined["total_sqft"] = pd.to_numeric(
        combined["total_sqft"],
        errors="coerce"
    )

    combined["bhk"] = pd.to_numeric(
        combined["bhk"],
        errors="coerce"
    )

    combined["bath"] = pd.to_numeric(
        combined["bath"],
        errors="coerce"
    )

    combined["balcony"] = pd.to_numeric(
        combined["balcony"],
        errors="coerce"
    )

    combined = combined[
        combined["price"] > 0
    ]

    combined = combined.dropna(
        subset=[
            "location",
            "price"
        ]
    )

    return combined


@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "Real Estate ML API is running!"
    })


@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "No data received"
            }), 400

        location = str(
            data["location"]
        ).strip()

        area_type = str(
            data["area_type"]
        ).strip()

        bhk = int(
            float(data["bhk"])
        )

        sqft = float(
            data["sqft"]
        )

        bath = int(
            float(data["bath"])
        )

        balcony = int(
            float(data["balcony"])
        )

        years = int(
            float(data["years"])
        )

        listed_price = float(
            data["listed_price"]
        )

        monthly_rent = float(
            data["monthly_rent"]
        )

        if not location:

            return jsonify({
                "error": "Location cannot be empty"
            }), 400

        if bhk <= 0:

            return jsonify({
                "error": "BHK must be greater than 0"
            }), 400

        if sqft <= 0:

            return jsonify({
                "error": "Area must be greater than 0"
            }), 400

        if bath < 0:

            return jsonify({
                "error": "Bathroom value is invalid"
            }), 400

        if balcony < 0:

            return jsonify({
                "error": "Balcony value is invalid"
            }), 400

        if years <= 0:

            return jsonify({
                "error": "Investment period must be greater than 0"
            }), 400

        if listed_price <= 0:

            return jsonify({
                "error": "Listed price must be greater than 0"
            }), 400

        if monthly_rent < 0:

            return jsonify({
                "error": "Monthly rent cannot be negative"
            }), 400


        predicted_price, future_value, roi = ROI(

            location,
            area_type,
            bhk,
            sqft,
            bath,
            balcony,
            years

        )


        fair, difference, percentage = fair_price(

            location,
            area_type,
            bhk,
            sqft,
            bath,
            balcony,
            listed_price

        )


        verdict = get_verdict(
            percentage
        )


        row_dict = {

            "area_type_Plot Area":
                1 if area_type == "Plot Area" else 0,

            "area_type_Carpet Area":
                1 if area_type == "Carpet Area" else 0,

            "area_type_Built-up Area":
                1 if area_type == "Built-up Area" else 0

        }


        try:

            appreciation_rate = rateofapp(
                location,
                row_dict
            )

        except Exception:

            appreciation_rate = 0


        house_price = listed_price

        down_payment_percent = 20

        interest_rate = 8.5

        loan_years = 20


        try:

            result = buy_vs_rent(

                house_price,

                monthly_rent,

                years,

                down_payment_percent,

                interest_rate,

                loan_years,

                appreciation_rate

            )

            (
                down_payment,
                emi,
                total_emi,
                remaining_loan,
                buy_future_value,
                equity,
                total_rent,
                net_buy_cost

            ) = result


            if net_buy_cost < total_rent:

                recommendation = "BUY"

            else:

                recommendation = "RENT"


        except Exception:

            down_payment = 0
            emi = 0
            total_emi = 0
            remaining_loan = 0
            buy_future_value = 0
            equity = 0
            total_rent = 0
            net_buy_cost = 0
            recommendation = "N/A"


        property_id = None

        try:

            conn = get_connection()

            cursor = conn.cursor()

            query = """
                INSERT INTO properties
                (
                    location,
                    area_type,
                    bhk,
                    sqft,
                    bath,
                    balcony,
                    price
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    location,
                    area_type,
                    bhk,
                    sqft,
                    bath,
                    balcony,
                    listed_price
                )
            )

            conn.commit()

            property_id = cursor.lastrowid

            cursor.close()
            conn.close()

        except Exception as db_error:

            print(
                "DATABASE SAVE ERROR:",
                db_error
            )


        return jsonify({

            "success": True,

            "message":
                "Property analyzed successfully",

            "property_id":
                property_id,

            "predicted_price":
                float(predicted_price),

            "future_value":
                float(future_value),

            "roi":
                float(roi),

            "listed_price":
                float(listed_price),

            "fair_price":
                float(fair),

            "difference":
                float(difference),

            "difference_percentage":
                float(percentage),

            "verdict":
                verdict,

            "buy_vs_rent": {

                "down_payment":
                    float(down_payment),

                "emi":
                    float(emi),

                "total_emi":
                    float(total_emi),

                "remaining_loan":
                    float(remaining_loan),

                "future_property_value":
                    float(buy_future_value),

                "equity":
                    float(equity),

                "total_rent":
                    float(total_rent),

                "net_buy_cost":
                    float(net_buy_cost),

                "recommendation":
                    recommendation

            }

        })


    except KeyError as e:

        return jsonify({

            "error":
                f"Missing field: {e.args[0]}"

        }), 400


    except ValueError as e:

        return jsonify({

            "error":
                f"Invalid input: {str(e)}"

        }), 400


    except Exception as e:

        print(
            "PREDICTION ERROR:",
            e
        )

        return jsonify({

            "error":
                str(e)

        }), 500


@app.route(
    "/properties",
    methods=["POST"]
)
def save_property():

    try:

        data = request.get_json()

        location = data["location"]

        area_type = data["area_type"]

        bhk = int(
            float(data["bhk"])
        )

        sqft = float(
            data["sqft"]
        )

        bath = int(
            float(data["bath"])
        )

        balcony = int(
            float(data["balcony"])
        )

        price = float(
            data["price"]
        )

        conn = get_connection()

        cursor = conn.cursor()

        query = """
            INSERT INTO properties
            (
                location,
                area_type,
                bhk,
                sqft,
                bath,
                balcony,
                price
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            query,
            (
                location,
                area_type,
                bhk,
                sqft,
                bath,
                balcony,
                price
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({

            "success": True,

            "message":
                "Property saved successfully"

        })

    except Exception as e:

        print(
            "SAVE PROPERTY ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


@app.route(
    "/properties",
    methods=["GET"]
)
def get_properties():

    try:

        df = get_combined_data()

        df["price"] = pd.to_numeric(
            df["price"],
            errors="coerce"
        )

        df["total_sqft"] = pd.to_numeric(
            df["total_sqft"],
            errors="coerce"
        )

        df = df[
            (df["price"] > 0) &
            (df["total_sqft"] > 0)
        ]

        count = min(
            20,
            len(df)
        )

        selected = df.sample(
            n=count
        )

        properties = []

        for index, row in selected.iterrows():

            properties.append({

                "id":
                    int(index),

                "location":
                    str(row["location"]),

                "area_type":
                    str(row["area_type"]),

                "bhk":
                    int(row["bhk"])
                    if pd.notna(row["bhk"])
                    else 0,

                "sqft":
                    round(
                        float(row["total_sqft"])
                    ),

                "bath":
                    int(row["bath"])
                    if pd.notna(row["bath"])
                    else 0,

                "balcony":
                    int(row["balcony"])
                    if pd.notna(row["balcony"])
                    else 0,

                "price":
                    round(
                        float(row["price"]),
                        2
                    )

            })

        return jsonify({

            "success": True,

            "properties":
                properties

        })

    except Exception as e:

        print(
            "FEATURED PROPERTIES ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


@app.route(
    "/top-locations",
    methods=["GET"]
)
def top_locations():

    try:

        df = get_combined_data()

        location_stats = (
            df
            .groupby("location")["price"]
            .mean()
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        locations = []

        for location, average_price in location_stats.items():

            locations.append({

                "location":
                    str(location),

                "average_price":
                    round(
                        float(
                            average_price
                        ),
                        2
                    )

            })

        return jsonify({

            "success": True,

            "locations":
                locations

        })

    except Exception as e:

        print(
            "TOP LOCATIONS ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


@app.route(
    "/average-price",
    methods=["GET"]
)
def average_price():

    try:

        df = get_combined_data()

        average = df["price"].mean()

        return jsonify({

            "success": True,

            "average_price":
                round(
                    float(average),
                    2
                )

        })

    except Exception as e:

        print(
            "AVERAGE PRICE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )