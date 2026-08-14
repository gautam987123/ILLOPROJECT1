# ILLOPROJECT1 — Real Estate Intelligence Platform

A full-stack real estate platform that combines **machine learning, property data, ROI analysis, fair-price estimation, and buy-vs-rent analysis** into one application.

The project is designed as a Zillow-like real estate application focused on Bengaluru property data.

## 🚀 Live Demo

**Frontend:**
https://illoproject-1.vercel.app/

**Backend API:**
https://illoproject1.onrender.com/

**GitHub Repository:**
https://github.com/gautam987123/ILLOPROJECT1

---

## ✨ Features

### 🏠 Property Discovery

Browse properties from the Bengaluru housing dataset.

The application displays:

* Property location
* Price
* BHK
* Square footage
* Bathrooms
* Balcony
* Area type
* Featured/random properties

### 📍 Top Locations

The application analyzes locations and calculates a location score based on factors such as:

* Average property price
* Number of available properties
* Average price per square foot
* Average BHK

The locations are ranked using a weighted scoring system.

### 🤖 ML Fair Price Prediction

The application uses a **Random Forest Regressor** to estimate the fair value of a property based on factors such as:

* Location
* Area type
* BHK
* Square footage
* Bathrooms
* Balcony

The predicted price can then be compared with the property's listed price.

### 📈 ROI Analysis

The platform estimates the future value of a property and calculates its expected ROI.

Users can provide a future investment period/year and evaluate the potential return.

### 💰 Fair Price vs Listed Price

The application compares:

**Predicted/Fair Price**

vs.

**Listed Price**

It calculates the difference and provides a verdict such as:

* Underpriced
* Fairly priced
* Overpriced

### 🏘️ Buy vs Rent

Users can compare the economics of buying a property against renting it based on:

* Property price
* Monthly rent
* Investment assumptions

### 📊 Area Appreciation Score

Locations are evaluated using property-market characteristics to generate an appreciation score.

---

## 🧠 Machine Learning

The project uses:

**RandomForestRegressor**

The trained model is stored as:

```text
roimodel.pkl
```

The model's feature columns are stored in:

```text
columns.pkl
```

### Model Performance

Current model results:

| Metric |  Score |
| ------ | -----: |
| R²     | 0.6936 |
| MAE    |  31.12 |
| RMSE   |  94.28 |

---

## 🗂️ Dataset

The project uses the **Bengaluru House Data** dataset.

Main columns include:

```text
area_type
availability
location
size
society
total_sqft
bath
balcony
price
```

The dataset is cleaned and transformed before being used by the ML model and real-estate analysis functions.

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* Flask
* Flask-CORS
* Gunicorn

### Machine Learning

* scikit-learn
* pandas
* NumPy
* Random Forest

### Database

* MySQL
* Railway

### Deployment

* **Frontend:** Vercel
* **Backend:** Render
* **Database:** Railway

---

## 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │      React/Vite      │
                 │       Vercel         │
                 └──────────┬───────────┘
                            │
                            │ HTTP API
                            ▼
                 ┌──────────────────────┐
                 │      Flask API       │
                 │       Render         │
                 └───────┬───────┬──────┘
                         │       │
              ┌──────────┘       └──────────┐
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │ Random Forest   │          │   Railway MySQL │
     │ ML Model        │          │    Database     │
     └─────────────────┘          └─────────────────┘
```

---

## 📁 Project Structure

```text
ILLOPROJECT1/
│
├── app.py
├── database.py
├── roi.py
├── excuteroi.py
├── area_apprection.py
├── retain_model.py
├── testapi.py
│
├── roimodel.pkl
├── columns.pkl
├── Bengaluru_House_Data.csv
│
├── package.json
├── requirements.txt
├── .gitignore
├── .gitattributes
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    │
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
        │
        └── assets/
            ├── hero.png
            ├── house.jpg
            ├── house1.jpg
            ├── house2.jpg
            ├── house3.jpg
            ├── house4.jpg
            ├── house5.jpg
            ├── house6.jpg
            ├── house7.jpg
            ├── house8.jpg
            └── house9.jpg
```

---

## 🔌 API

### Health Check

```http
GET /
```

Returns:

```json
{
  "message": "Real Estate ML API is running!",
  "success": true
}
```

### Properties

```http
GET /properties
```

Returns property information including:

```text
location
price
sqft
bhk
bath
balcony
area_type
```

### Prediction

```http
POST /predict
```

The prediction endpoint accepts property information and returns analysis including:

```text
predicted_price
fair_price
listed_price
difference
difference_percentage
future_value
roi
verdict
```

---

## 💻 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/gautam987123/ILLOPROJECT1.git
cd ILLOPROJECT1
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

Windows:

```powershell
.venv\Scripts\activate
```

### 4. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 5. Start Flask

```bash
python app.py
```

The backend will normally run at:

```text
http://127.0.0.1:5000
```

### 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server will provide the frontend URL.

---

## 🔐 Environment Variables

For production, database credentials should be stored as environment variables rather than committed to GitHub.

Example:

```text
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
```

Never commit:

```text
.env
```

or database passwords/API keys to the repository.

---

## 📦 Deployment

### Frontend

The React/Vite frontend is deployed using:

**Vercel**

The Vercel project uses:

```text
Root Directory: frontend
```

### Backend

The Flask backend is deployed using:

**Render**

Start command:

```bash
gunicorn app:app
```

### Database

The production MySQL database is hosted on:

**Railway**

---
## 📸 Screenshots

### Homepage

## 📸 Screenshots

### Homepage

<img width="1261" height="900" alt="image" src="https://github.com/user-attachments/assets/48c84037-6342-4988-b7a4-c2d4bfb87117" />


### Property Discovery

<img width="1048" height="806" alt="image" src="https://github.com/user-attachments/assets/5d4a5956-357e-426b-ab0f-f714c4383b5d" />


### ML Price & ROI Analysis

<img width="1079" height="884" alt="image" src="https://github.com/user-attachments/assets/3ab29268-4b2e-47cd-92a3-022e71f6a8d3" />


## 🎯 Project Goal

The goal of ILLOPROJECT1 is to build a real-estate decision platform that goes beyond simply displaying property listings.

Instead of only asking:

> "How much does this house cost?"

the platform attempts to answer:

> **"Is this house actually worth the price, how much could it appreciate, and should I buy or rent?"**

---

## 🔮 Future Improvements

Potential future improvements include:

* User authentication
* Saved properties
* Advanced property filters
* Interactive Bengaluru map
* Price trend visualization
* Improved ML models
* More historical market data
* Better ROI forecasting
* Mortgage/loan calculator
* Property comparison
* Personalized recommendations
* Automated market insights
* Improved model accuracy

---

## 👨‍💻 Author

**Gautam A**

GitHub:

https://github.com/gautam987123

---

## 📄 License

This project is currently intended for educational and development purposes.
