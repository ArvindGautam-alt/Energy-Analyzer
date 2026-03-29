import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_datasets(start_date='2023-01-01', days=365):
    """Generates synthetic hourly energy consumption for multiple houses and weather data."""
    print(f"Generating synthetic data for {days} days starting from {start_date}...")
    
    # 1. Date Range
    start_dt = pd.to_datetime(start_date)
    date_rng = pd.date_range(start=start_dt, periods=days*24, freq='h')
    
    # 2. Weather Data Simulation
    np.random.seed(42)
    days_arr = date_rng.dayofyear
    daily_temp_base = 15 + 10 * np.sin(2 * np.pi * (days_arr - 100) / 365)
    hours_arr = date_rng.hour
    daily_temp_var = 5 * np.sin(np.pi * (hours_arr - 6) / 12)
    
    temperature = daily_temp_base + daily_temp_var + np.random.normal(0, 2, len(date_rng))
    humidity = np.clip(60 + 20 * np.sin(2 * np.pi * days_arr / 365) + np.random.normal(0, 10, len(date_rng)), 20, 100)
    
    weather_df = pd.DataFrame({
        'timestamp': date_rng,
        'temperature_c': np.round(temperature, 1),
        'humidity_percent': np.round(humidity, 1)
    })
    
    weather_df['condition'] = np.where(weather_df['temperature_c'] < 0, 'Snow',
                              np.where((weather_df['humidity_percent'] > 85) & (np.random.rand(len(date_rng)) > 0.6), 'Rain', 'Clear'))
    
    # 3. Energy Consumption Simulation (Multiple Houses)
    houses = ['House A', 'House B', 'House C', 'House D', 'House E']
    all_energy_data = []
    
    for house in houses:
        # Each house has slightly different base load and behaviors
        base_multiplier = np.random.uniform(0.7, 1.3)
        base_load = 50.0 * base_multiplier
        
        tod_effect = np.where((hours_arr >= 17) & (hours_arr <= 21), 30 * base_multiplier, 
                     np.where((hours_arr >= 8) & (hours_arr <= 16), 15 * base_multiplier, 0))
        
        dow_arr = date_rng.dayofweek
        dow_effect = np.where(dow_arr >= 5, -10 * base_multiplier, 5 * base_multiplier)
        
        heating_load = np.maximum(0, 15 - temperature) * 3 * base_multiplier
        cooling_load = np.maximum(0, temperature - 22) * 4 * base_multiplier
        
        noise = np.random.normal(0, 5, len(date_rng))
        
        energy_kwh = base_load + tod_effect + dow_effect + heating_load + cooling_load + noise
        energy_kwh = np.maximum(energy_kwh, 10) 
        
        house_df = pd.DataFrame({
            'timestamp': date_rng,
            'house_id': house,
            'energy_consumption_kwh': np.round(energy_kwh, 2)
        })
        
        mask = np.random.rand(len(house_df)) < 0.01
        house_df.loc[mask, 'energy_consumption_kwh'] = np.nan
        house_df['price_per_kwh'] = np.where((hours_arr >= 16) & (hours_arr <= 20), 0.25, 0.12)
        
        all_energy_data.append(house_df)
        
    energy_df = pd.concat(all_energy_data, ignore_index=True)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    energy_df.to_csv('data/energy_data.csv', index=False)
    weather_df.to_csv('data/weather_data.csv', index=False)
    
    print(f"Successfully generated {len(energy_df)} rows of multi-house data.")
    print("Files saved to 'data/' directory: 'energy_data.csv', 'weather_data.csv'")

if __name__ == "__main__":
    generate_datasets()
