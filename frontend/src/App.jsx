import { useEffect, useState } from "react";
import "./App.css";

import house1 from "./assets/house1.jpg";
import house2 from "./assets/house2.jpg";
import house3 from "./assets/house3.jpg";
import house4 from "./assets/house4.jpg";
import house5 from "./assets/house5.jpg";
import house6 from "./assets/house6.jpg";
import house7 from "./assets/house7.jpg";
import house8 from "./assets/house8.jpg";
import house9 from "./assets/house9.jpg";

const API_URL = "http://127.0.0.1:5000";

const houseImages = [
  house1,
  house2,
  house3,
  house4,
  house5,
  house6,
  house7,
  house8,
];

// =====================================================
// IMAGE ASSIGNMENT
// =====================================================

const getPropertyImage = (property, index) => {
  const areaType = String(property.area_type || "")
    .trim()
    .toLowerCase();

  // Plot Area ALWAYS gets house9
  if (areaType === "plot area" || areaType.includes("plot")) {
    return house9;
  }

  // Other properties cycle through house1 -> house8
  return houseImages[index % houseImages.length];
};

// =====================================================
// PRICE FORMAT
// =====================================================

const formatPrice = (price) => {
  const value = Number(price);

  if (!Number.isFinite(value)) {
    return "₹0 L";
  }

  if (value >= 100) {
    return `₹${(value / 100).toFixed(2)} Cr`;
  }

  return `₹${value.toFixed(2)} L`;
};

// =====================================================
// APP
// =====================================================

function App() {
  const [form, setForm] = useState({
    location: "",
    area_type: "Super built-up Area",
    bhk: "",
    sqft: "",
    bath: "",
    balcony: "",
    years: 5,
    listed_price: "",
    monthly_rent: "",
  });

  const [result, setResult] = useState(null);

  const [properties, setProperties] = useState([]);

  const [topLocations, setTopLocations] = useState([]);

  const [averagePrice, setAveragePrice] = useState(0);

  const [loading, setLoading] = useState(false);

  const [propertiesLoading, setPropertiesLoading] = useState(true);

  const [error, setError] = useState("");

  const [saveMessage, setSaveMessage] = useState("");

  // ===================================================
  // HANDLE FORM CHANGE
  // ===================================================

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setError("");
    setSaveMessage("");
  };

  // ===================================================
  // LOAD 7 RANDOM PROPERTIES
  // ===================================================

  const loadProperties = async () => {
    try {
      setPropertiesLoading(true);

      const response = await fetch(`${API_URL}/properties`);

      if (!response.ok) {
        throw new Error("Failed to load properties");
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.error || "Could not load properties"
        );
      }

      // Take random properties from the database
      // and display ONLY 7.
      const randomProperties = [...(data.properties || [])]
        .sort(() => Math.random() - 0.5)
        .slice(0, 7);

      // Assign images HERE.
      // This means images don't change during
      // normal React re-renders.
      const propertiesWithImages = randomProperties.map(
        (property, index) => ({
          ...property,
          image: getPropertyImage(property, index),
        })
      );

      setProperties(propertiesWithImages);
    } catch (err) {
      console.error("Properties error:", err);
      setProperties([]);
    } finally {
      setPropertiesLoading(false);
    }
  };

  // ===================================================
  // TOP LOCATIONS
  // ===================================================

  const loadTopLocations = async () => {
    try {
      const response = await fetch(
        `${API_URL}/top-locations`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (data.success) {
        setTopLocations(data.locations || []);
      }
    } catch (err) {
      console.error("Top locations error:", err);
    }
  };

  // ===================================================
  // OVERALL AVERAGE
  // ===================================================

  const loadAveragePrice = async () => {
    try {
      const response = await fetch(
        `${API_URL}/average-price`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (data.success) {
        setAveragePrice(
          Number(data.average_price) || 0
        );
      }
    } catch (err) {
      console.error("Average price error:", err);
    }
  };

  // ===================================================
  // INITIAL LOAD
  // ===================================================

  useEffect(() => {
    loadProperties();
    loadTopLocations();
    loadAveragePrice();
  }, []);

  // ===================================================
  // FORM VALIDATION
  // ===================================================

  const validateForm = () => {
    if (!form.location.trim()) {
      return "Please enter a location.";
    }

    if (!form.bhk || Number(form.bhk) <= 0) {
      return "Enter a valid BHK.";
    }

    if (!form.sqft || Number(form.sqft) <= 0) {
      return "Enter a valid area.";
    }

    if (!form.bath || Number(form.bath) <= 0) {
      return "Enter the number of bathrooms.";
    }

    if (
      form.balcony === "" ||
      Number(form.balcony) < 0
    ) {
      return "Enter a valid balcony count.";
    }

    if (
      !form.listed_price ||
      Number(form.listed_price) <= 0
    ) {
      return "Enter the listed price.";
    }

    if (
      form.monthly_rent === "" ||
      Number(form.monthly_rent) < 0
    ) {
      return "Enter a valid monthly rent.";
    }

    return "";
  };

  // ===================================================
  // ANALYZE PROPERTY
  // ===================================================

  const handleAnalyze = async (e) => {
    e.preventDefault();

    setError("");
    setSaveMessage("");
    setResult(null);

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const payload = {
        location: form.location.trim(),
        area_type: form.area_type,
        bhk: Number(form.bhk),
        sqft: Number(form.sqft),
        bath: Number(form.bath),
        balcony: Number(form.balcony),
        years: Number(form.years),
        listed_price: Number(form.listed_price),
        monthly_rent: Number(form.monthly_rent),
      };

      // ===============================================
      // PREDICT
      // ===============================================

      const predictResponse = await fetch(
        `${API_URL}/predict`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const prediction = await predictResponse.json();

      if (
        !predictResponse.ok ||
        !prediction.success
      ) {
        throw new Error(
          prediction.error || "Prediction failed."
        );
      }

      setResult(prediction);

      // ===============================================
      // SAVE PROPERTY
      // ===============================================

      const saveResponse = await fetch(
        `${API_URL}/properties`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            location: payload.location,
            area_type: payload.area_type,
            bhk: payload.bhk,
            sqft: payload.sqft,
            bath: payload.bath,
            balcony: payload.balcony,
            price: payload.listed_price,
          }),
        }
      );

      const saved = await saveResponse.json();

      if (
        !saveResponse.ok ||
        !saved.success
      ) {
        throw new Error(
          saved.error ||
          "Property could not be saved."
        );
      }

      setSaveMessage(
        "Property analyzed & saved ✓"
      );

      // Refresh market/property data
      await loadProperties();
      await loadTopLocations();
      await loadAveragePrice();

    } catch (err) {
      console.error(err);

      setError(
        err.message || "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  // ===================================================
  // VERDICT STYLE
  // ===================================================

  const getVerdictClass = (verdict) => {
    const value = String(
      verdict || ""
    ).toLowerCase();

    if (value.includes("under")) {
      return "good";
    }

    if (value.includes("fair")) {
      return "fair";
    }

    if (value.includes("over")) {
      return "bad";
    }

    return "neutral";
  };

  // ===================================================
  // GRAPH MAX
  // ===================================================

  const maxLocationPrice =
    topLocations.length > 0
      ? Math.max(
          ...topLocations.map(
            (item) =>
              Number(item.average_price) || 0
          )
        )
      : 0;

  // ===================================================
  // JSX
  // ===================================================

  return (
    <div className="app">

      {/* ============================================ */}
      {/* NAVBAR */}
      {/* ============================================ */}

      <nav className="navbar">

        <div className="brand">
          <span className="brand-dot">●</span>
          illo
        </div>

        <div className="nav-tag">
          REAL ESTATE INTELLIGENCE
        </div>

      </nav>


      {/* ============================================ */}
      {/* HERO */}
      {/* ============================================ */}

      <section className="hero">

        <div className="hero-left">

          <div className="eyebrow">
            🏠 SMART PROPERTY ANALYSIS
          </div>

          <h1>
            Find out if that
            <span>
              property is actually worth it.
            </span>
          </h1>

          <p className="hero-text">
            AI-powered property valuation,
            ROI prediction and buy-vs-rent
            analysis for Bengaluru real estate.
          </p>

          <div className="hero-stats">

            <div>
              <strong>ML</strong>
              <span>PRICE MODEL</span>
            </div>

            <div>
              <strong>ROI</strong>
              <span>FUTURE VALUE</span>
            </div>

            <div>
              <strong>7</strong>
              <span>FEATURED</span>
            </div>

          </div>

        </div>


        {/* ========================================== */}
        {/* ANALYZER CARD */}
        {/* ========================================== */}

        <div className="analyzer-card">

          <div className="card-heading">

            <div>
              <span>PROPERTY CHECK</span>

              <h2>
                Analyze a property
              </h2>
            </div>

            <div className="live-pill">
              ● LIVE
            </div>

          </div>


          <form onSubmit={handleAnalyze}>

            {/* LOCATION */}

            <div className="field full">

              <label>Location</label>

              <input
                type="text"
                name="location"
                value={form.location}
                onChange={handleChange}
                placeholder="Whitefield, JP Nagar, Cubbon Road..."
              />

            </div>


            {/* AREA TYPE */}

            <div className="field full">

              <label>Area type</label>

              <select
                name="area_type"
                value={form.area_type}
                onChange={handleChange}
              >

                <option>
                  Super built-up Area
                </option>

                <option>
                  Built-up Area
                </option>

                <option>
                  Plot Area
                </option>

                <option>
                  Carpet Area
                </option>

              </select>

            </div>


            {/* INPUT GRID */}

            <div className="form-grid">

              <div className="field">

                <label>BHK</label>

                <input
                  type="number"
                  name="bhk"
                  value={form.bhk}
                  onChange={handleChange}
                  min="1"
                  placeholder="3"
                />

              </div>


              <div className="field">

                <label>Area (sqft)</label>

                <input
                  type="number"
                  name="sqft"
                  value={form.sqft}
                  onChange={handleChange}
                  min="1"
                  placeholder="1500"
                />

              </div>


              <div className="field">

                <label>Bathrooms</label>

                <input
                  type="number"
                  name="bath"
                  value={form.bath}
                  onChange={handleChange}
                  min="1"
                  placeholder="2"
                />

              </div>


              <div className="field">

                <label>Balcony</label>

                <input
                  type="number"
                  name="balcony"
                  value={form.balcony}
                  onChange={handleChange}
                  min="0"
                  placeholder="1"
                />

              </div>


              <div className="field">

                <label>Years ahead</label>

                <input
                  type="number"
                  name="years"
                  value={form.years}
                  onChange={handleChange}
                  min="1"
                  max="50"
                />

              </div>


              <div className="field">

                <label>Listed price ₹L</label>

                <input
                  type="number"
                  name="listed_price"
                  value={form.listed_price}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
                  placeholder="80"
                />

              </div>


              <div className="field full">

                <label>Monthly rent ₹</label>

                <input
                  type="number"
                  name="monthly_rent"
                  value={form.monthly_rent}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
                  placeholder="25000"
                />

              </div>

            </div>


            {/* ERROR */}

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}


            {/* SUCCESS */}

            {saveMessage && (
              <div className="success-message">
                {saveMessage}
              </div>
            )}


            {/* BUTTON */}

            <button
              className="analyze-button"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Analyze Property →"}
            </button>

            <p className="button-note">
              Prediction + automatic save
            </p>

          </form>

        </div>

      </section>


      {/* ============================================ */}
      {/* RESULT */}
      {/* ============================================ */}

      {result && (

        <section className="result-section">

          <div className="section-label">
            YOUR PROPERTY RESULT
          </div>

          <div className="result-grid">

            <div className="result-card highlight">

              <span>FAIR PRICE</span>

              <strong>
                {formatPrice(
                  result.fair_price
                )}
              </strong>

              <small>
                ML estimated value
              </small>

            </div>


            <div className="result-card">

              <span>LISTED PRICE</span>

              <strong>
                {formatPrice(
                  result.listed_price
                )}
              </strong>

              <small>
                Seller asking price
              </small>

            </div>


            <div className="result-card">

              <span>FUTURE VALUE</span>

              <strong>
                {formatPrice(
                  result.future_value
                )}
              </strong>

              <small>
                Based on your timeline
              </small>

            </div>


            <div className="result-card">

              <span>EXPECTED ROI</span>

              <strong>
                {Number(
                  result.roi || 0
                ).toFixed(2)}
                %
              </strong>

              <small>
                Estimated appreciation
              </small>

            </div>

          </div>


          {/* VERDICT */}

          <div className="verdict-card">

            <div>

              <span>VERDICT</span>

              <h2
                className={getVerdictClass(
                  result.verdict
                )}
              >
                {result.verdict}
              </h2>

            </div>

            <div className="difference">

              <span>PRICE DIFFERENCE</span>

              <strong>
                {Number(
                  result.difference_percentage || 0
                ).toFixed(2)}
                %
              </strong>

            </div>

          </div>

        </section>

      )}


      {/* ============================================ */}
      {/* MARKET */}
      {/* ============================================ */}

      <section className="market-section">

        <div className="section-header">

          <div>

            <div className="section-label">
              BENGALURU MARKET
            </div>

            <h2>
              What's happening around the city?
            </h2>

          </div>

          <div className="average-box">

            <span>
              OVERALL AVG PRICE
            </span>

            <strong>
              {formatPrice(
                averagePrice
              )}
            </strong>

          </div>

        </div>


        {/* LOCATION GRAPH */}

        <div className="graph-card">

          <div className="graph-header">

            <div>

              <h3>
                Top 10 locations
              </h3>

              <p>
                Average property price
              </p>

            </div>

          </div>


          {topLocations.length === 0 ? (

            <div className="empty-graph">
              No location data available.
            </div>

          ) : (

            <div className="location-chart">

              {topLocations.map(
                (item, index) => {

                  const price =
                    Number(
                      item.average_price
                    ) || 0;

                  const percentage =
                    maxLocationPrice > 0
                      ? (price / maxLocationPrice) *
                        100
                      : 0;

                  return (

                    <div
                      className="chart-row"
                      key={item.location}
                    >

                      <div className="chart-name">

                        <span>
                          {index + 1}
                        </span>

                        <strong>
                          {item.location}
                        </strong>

                      </div>


                      <div className="chart-bar-container">

                        <div
                          className="chart-bar"
                          style={{
                            width:
                              `${percentage}%`,
                          }}
                        />

                      </div>


                      <div className="chart-price">

                        {formatPrice(price)}

                      </div>

                    </div>

                  );
                }
              )}

            </div>

          )}

        </div>

      </section>


      {/* ============================================ */}
      {/* PROPERTIES */}
      {/* ============================================ */}

      <section className="properties-section">

        <div className="section-header">

          <div>

            <div className="section-label">
              PROPERTY DISCOVERY
            </div>

            <h2>
              Featured Properties
            </h2>

            <p>
              Random picks from the property database.
            </p>

          </div>


          <div className="property-count">

            7

            <span>
              PROPERTIES
            </span>

          </div>

        </div>


        {propertiesLoading ? (

          <div className="properties-loading">

            <div className="loader">
              ◌
            </div>

            <p>
              Finding properties...
            </p>

          </div>

        ) : properties.length === 0 ? (

          <div className="empty-properties">

            <div className="empty-icon">
              🏠
            </div>

            <h3>
              No properties found
            </h3>

            <p>
              Your property database is empty.
            </p>

          </div>

        ) : (

          <div className="property-grid">

            {properties.map(
              (property, index) => (

                <article
                  className="property-card"
                  key={
                    property.id ||
                    `${property.location}-${index}`
                  }
                >

                  {/* IMAGE */}

                  <div className="property-image-wrap">

                    <img
                      src={property.image}
                      alt={`${property.bhk || ""} BHK property`}
                      className="property-image"
                    />

                    <div className="image-tag">
                      {property.area_type}
                    </div>

                  </div>


                  {/* DETAILS */}

                  <div className="property-content">

                    <div className="property-top">

                      <div>

                        <h3>
                          {property.bhk || "—"} BHK
                        </h3>

                        <p>
                          📍 {property.location}
                        </p>

                      </div>

                      <strong>
                        {formatPrice(
                          property.price
                        )}
                      </strong>

                    </div>


                    <div className="property-details">

                      <span>
                        📐 {property.sqft || "—"} sqft
                      </span>

                      <span>
                        🛁 {property.bath || "—"} bath
                      </span>

                      <span>
                        🌿 {property.balcony ?? "—"} balcony
                      </span>

                    </div>


                    <div className="property-footer">

                      <span>
                        Featured property
                      </span>

                      <span className="view-label">
                        VIEW →
                      </span>

                    </div>

                  </div>

                </article>

              )
            )}

          </div>

        )}

      </section>


      {/* ============================================ */}
      {/* FOOTER */}
      {/* ============================================ */}

      <footer className="footer">

        <div className="brand">

          <span className="brand-dot">
            ●
          </span>

          illo

        </div>

        <span>
          Bengaluru Real Estate Intelligence
        </span>

      </footer>

    </div>
  );
}

export default App;