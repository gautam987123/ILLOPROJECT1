import joblib
import numpy as np
from area_apprection import give_rate_roi
rf=joblib.load('roimodel.pkl')
model_columns= joblib.load("columns.pkl")

known_locations = [
    col.replace("location_", "")
    for col in model_columns
    if col.startswith("location_")
]

def prepare_input(location, area_type, bhk, sqft, bath, balcony):


    if location not in known_locations:
        print("⚠️ Unknown location. Using 'other' category.")
        location = "other"

    data=dict.fromkeys(model_columns,0)
    data['bhk']=bhk
    data['total_sqft']=sqft
    data['bath']=bath
    data['balcony']=balcony
    area_col = f"area_type_{area_type}"
    if area_col in model_columns:
        data[area_col] = 1
    loc_col=f"location_{location}"
    if loc_col in model_columns:
        data[loc_col]=1
    return [data[col] for col in model_columns]
def rateofapp(location, row_dict):
    return give_rate_roi(location, row_dict)
def ROI(location, area_type, bhk, sqft, bath, balcony, years):
    data=prepare_input(location, area_type, bhk, sqft, bath, balcony)
    pred_price=rf.predict([data])[0]
    row_dict = dict(zip(model_columns,data))
    rate = rateofapp(location, row_dict)
    fv=pred_price*((1+rate)**years)
    roi_value = ((fv - pred_price) / pred_price) * 100

    return pred_price, fv, roi_value
def fair_price(location, area_type, bhk, sqft, bath, balcony, listed_price):
    data = prepare_input(
        location,
        area_type,
        bhk,
        sqft,
        bath,
        balcony
    )

    predicted_price = rf.predict([data])[0]

    difference = listed_price - predicted_price

    percentage_difference = (
        difference / predicted_price
    ) * 100

    return predicted_price, difference, percentage_difference
def get_verdict(percentage_difference):

    if percentage_difference > 10:
        return "Overpriced"

    elif percentage_difference < -10:
        return "Underpriced"

    else:
        return "Fair Price"

def buy_vs_rent(house_price_lakh, monthly_rent, years,
                down_payment_percent, interest_rate, loan_years,
                appreciation_rate):


    house_price = house_price_lakh * 100000


    down_payment = house_price * (down_payment_percent / 100)


    loan_amount = house_price - down_payment

    # Monthly interest
    monthly_rate = interest_rate / 100 / 12

    total_payments = loan_years * 12


    emi = (
        loan_amount * monthly_rate *
        (1 + monthly_rate) ** total_payments
    ) / (
        (1 + monthly_rate) ** total_payments - 1
    )

    payments = min(years * 12, total_payments)

    total_emi = emi * payments

    balance = loan_amount

    for i in range(payments):
        interest = balance * monthly_rate
        principal = emi - interest
        balance -= principal

    remaining_loan = max(balance, 0)

    # Future property value
    future_value = house_price * (
        (1 + appreciation_rate) ** years
    )



    total_rent = monthly_rent * 12 * years

    # ---------------- BUY NET COST ----------------

    equity = future_value - remaining_loan

    net_buy_cost = down_payment + total_emi - equity

    return (
        down_payment,
        emi,
        total_emi,
        remaining_loan,
        future_value,
        equity,
        total_rent,
        net_buy_cost
    )
def main():



    location = "JP Nagar"
    area_type = "Plot Area"
    bhk = 2
    sqft = 1200
    bath = 2
    balcony = 1

    years = 10
    listed_price = 80

    # Buy vs Rent inputs
    house_price = 80          # lakh
    monthly_rent = 25000      # rupees
    down_payment_percent = 20
    interest_rate = 8.5
    loan_years = 20

    # ---------------- ROI ----------------

    pred_price, future_value, roi = ROI(
        location,
        area_type,
        bhk,
        sqft,
        bath,
        balcony,
        years
    )

    print("\n--- INPUT ---")
    print(
        location,
        area_type,
        bhk,
        sqft,
        bath,
        balcony,
        years
    )

    print("\n--- OUTPUT ---")
    print("Predicted Price:", pred_price)
    print("Future Value:", future_value)
    print("ROI %:", roi)

    # ---------------- FAIR PRICE ----------------

    fair, difference, percentage = fair_price(
        location,
        area_type,
        bhk,
        sqft,
        bath,
        balcony,
        listed_price
    )

    verdict = get_verdict(percentage)

    print("\n--- FAIR PRICE ANALYSIS ---")
    print("Listed Price:", listed_price)
    print("Fair Price:", fair)
    print("Difference:", difference)
    print("Difference %:", percentage)
    print("Verdict:", verdict)

    # ---------------- BUY VS RENT ----------------

    appreciation_rate = 0.07

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

    print("\n--- BUY VS RENT ---")
    print("House Price:", house_price, "Lakh")
    print("Monthly Rent: ₹", monthly_rent)
    print("Period:", years, "years")

    print("\n--- BUYING ---")
    print("Down Payment: ₹", down_payment)
    print("Monthly EMI: ₹", emi)
    print("Total EMI Paid: ₹", total_emi)
    print("Remaining Loan: ₹", remaining_loan)
    print("Future Property Value: ₹", buy_future_value)
    print("Your Equity: ₹", equity)

    print("\n--- RENTING ---")
    print("Total Rent: ₹", total_rent)

    print("\n--- COMPARISON ---")
    print("Net Cost of Buying: ₹", net_buy_cost)

    if net_buy_cost < total_rent:
        print("Recommendation: BUY")
    else:
        print("Recommendation: RENT")


main()