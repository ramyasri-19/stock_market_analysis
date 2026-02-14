📊 Stock Market Analytics Dashboard

Financial Data Visualization Application Built with Streamlit

🚀 Overview

The Stock Market Analytics Dashboard is an interactive financial data visualization application designed to perform in-depth stock analysis and multi-ticker comparison using advanced technical indicators and dynamic visualizations.

This project demonstrates strong capabilities in:

Data Cleaning & Transformation

Financial Data Analysis

Time Series Processing

Technical Indicator Implementation

Interactive Dashboard Development

Business-Ready Visualization Design

It is built with a modular, scalable architecture suitable for real-world financial analytics use cases.

🧠 Business Problem

Investors and analysts require consolidated, interactive, and technically enriched dashboards to:

Monitor stock performance

Analyze market trends

Compare multiple equities

Identify trading signals using technical indicators

Understand institutional ownership patterns

This application provides a centralized analytical interface to support data-driven decision-making.


✨ Key Features
🔹 1. Individual Stock Analysis

KPI Metrics:

Open Price

Dollar Change

Percentage Change

Trading Volume

Advanced Visualizations:

Interactive Candlestick Chart

Volume Analysis with annotations

Time-range filtering (1M, 3M, 6M, 1Y, 10Y)

Executive & Ownership Insights:

Key Executives

Top Institutional Holders

Top Mutual Fund Holders


🔹 2. Multi-Ticker Comparison

Multi-stock selection

Custom date range filtering

Comparative analytics using:

Line Chart

Candlestick Chart

Stacked Volume Chart

Box Plot (Distribution Analysis)

Percent Change Chart

Multi-Series Time Series Analysis

Automatic detection of significant price movements



📈 Technical Indicators Implemented

This project includes advanced financial indicator implementations from scratch:

Moving Averages (20-Day & 50-Day)

Relative Strength Index (RSI)

Bollinger Bands

Volume Weighted Average Price (VWAP)

Stochastic Oscillator

Average True Range (ATR)

On-Balance Volume (OBV)

Rate of Change (ROC)

Rolling Average Volume

All indicators are calculated dynamically using Pandas operations without external finance libraries.


🛠️ Tech Stack
Layer	Technology
Frontend	Streamlit
Data Processing	Pandas, NumPy
Visualization	Plotly (Graph Objects & Express)
UI Components	streamlit-option-menu, streamlit-pills
Data Source	Excel (Multi-sheet structured financial dataset)


🏗️ Architecture Overview
Excel Data (Multi-Sheet)
        ↓
Data Loading & Caching Layer
        ↓
Data Filtering & Transformation
        ↓
Technical Indicator Computation
        ↓
Interactive Plotly Visualizations
        ↓
Streamlit UI Rendering


📂 Project Structure
📦 stock-market-dashboard
 ┣ 📜 app.py
 ┣ 📊 Stock_Data.xlsx
 ┣ 📜 README.md


⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/<your-username>/stock-market-dashboard.git
cd stock-market-dashboard

2️⃣ Install Dependencies
pip install -r requirements.txt

Or manually:

pip install streamlit pandas numpy plotly streamlit-option-menu streamlit-pills openpyxl

3️⃣ Run Application
streamlit run app.py


📊 Data Structure

The application expects an Excel file with the following sheets:

Stock Data

Key Executives

Top Institutional Holders

Top Mutual Fund Holders

Ensure Stock_Data.xlsx is present in the root directory.


📌 Engineering Highlights

Efficient data caching using @st.cache_data

Optimized Pandas transformations for rolling computations

Dynamic time-window filtering

Modular filtering logic for scalability

Professional dashboard UI/UX layout

Annotation-driven storytelling in visualizations

Separation of analysis and comparison workflows