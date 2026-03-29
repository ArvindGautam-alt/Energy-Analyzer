# Energy Consumption Analytics & Forecasting

This project demonstrates a complete end-to-end data analytics pipeline predicting energy consumption based on historical usage and weather patterns. It is designed to be a comprehensive 3rd-year university analytic project.

## Features
- **Synthetic Data Generation**: Simulates realistic hourly energy demand (with time-of-day, day-of-week, and seasonal variations) alongside weather data.
- **Exploratory Data Analysis (EDA)**: A Jupyter Notebook showcasing data cleaning, merging, and descriptive statistics.
- **Machine Learning**: A Random Forest regression model to forecast future energy consumption.
- **Interactive Dashboard**: A Streamlit web application providing a modern, interactive interface for presenting the findings and running forecasts.

## Getting Started

### 1. Setup Environment
Install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Generate Data
Run the data generator to create `data/energy_data.csv` and `data/weather_data.csv`:
```bash
python data_generator.py
```

### 3. Explore the Notebook
Start Jupyter Server to walk through the analysis, visualization, and model building process:
```bash
jupyter notebook Energy_Analytics_Project.ipynb
```

### 4. Launch the Dashboard
Run the Streamlit app to view the interactive presentation dashboard:
```bash
streamlit run app.py
```
