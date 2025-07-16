import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

class MicroMobilityDataGenerator:
    def __init__(self, start_date='2024-01-01', end_date='2024-12-31', num_stations=50, city_name='Delhi'):
        self.start_date = start_date
        self.end_date = end_date
        self.num_stations = num_stations
        self.city_name = city_name
        
        # Delhi-specific station locations (lat, lon)
        self.station_locations = self._generate_station_locations()
        
        # Define demand patterns
        self.base_patterns = {
            'business_district': {'peak_hours': [8, 9, 17, 18], 'base_demand': 25},
            'residential': {'peak_hours': [7, 8, 18, 19], 'base_demand': 15},
            'tourist': {'peak_hours': [10, 11, 14, 15], 'base_demand': 20},
            'transport_hub': {'peak_hours': [6, 7, 8, 17, 18, 19], 'base_demand': 30},
            'educational': {'peak_hours': [8, 9, 16, 17], 'base_demand': 18}
        }
        
    def _generate_station_locations(self):
        """Generate realistic station locations for Delhi"""
        # Delhi coordinates: roughly 28.4°N to 28.9°N, 76.8°E to 77.3°E
        locations = []
        
        # Define major areas in Delhi with their coordinates
        major_areas = [
            {'name': 'Connaught Place', 'lat': 28.6315, 'lon': 77.2167, 'type': 'business_district'},
            {'name': 'India Gate', 'lat': 28.6129, 'lon': 77.2295, 'type': 'tourist'},
            {'name': 'Red Fort', 'lat': 28.6562, 'lon': 77.2410, 'type': 'tourist'},
            {'name': 'Karol Bagh', 'lat': 28.6519, 'lon': 77.1909, 'type': 'business_district'},
            {'name': 'Lajpat Nagar', 'lat': 28.5677, 'lon': 77.2353, 'type': 'residential'},
            {'name': 'Dwarka', 'lat': 28.5921, 'lon': 77.0460, 'type': 'residential'},
            {'name': 'Gurgaon Border', 'lat': 28.4595, 'lon': 77.0266, 'type': 'transport_hub'},
            {'name': 'Delhi University', 'lat': 28.6857, 'lon': 77.2085, 'type': 'educational'},
            {'name': 'JNU', 'lat': 28.5383, 'lon': 77.1641, 'type': 'educational'},
            {'name': 'Chandni Chowk', 'lat': 28.6506, 'lon': 77.2334, 'type': 'business_district'}
        ]
        
        # Generate stations around these major areas
        for i in range(self.num_stations):
            base_area = random.choice(major_areas)
            
            # Add some randomness around the base location
            lat_offset = random.uniform(-0.02, 0.02)
            lon_offset = random.uniform(-0.02, 0.02)
            
            locations.append({
                'station_id': i,
                'name': f"Station_{i}_{base_area['name'].replace(' ', '_')}",
                'latitude': base_area['lat'] + lat_offset,
                'longitude': base_area['lon'] + lon_offset,
                'area_type': base_area['type'],
                'base_area': base_area['name']
            })
        
        return locations
    
    def generate_trip_data(self):
        """Generate realistic trip data with patterns"""
        print(f"🚀 Generating trip data from {self.start_date} to {self.end_date}...")
        
        date_range = pd.date_range(self.start_date, self.end_date, freq='H')
        
        trips = []
        total_records = len(date_range) * self.num_stations
        processed = 0
        
        for timestamp in date_range:
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            month = timestamp.month
            
            # Progress indicator
            if processed % 10000 == 0:
                progress = (processed / total_records) * 100
                print(f"Progress: {progress:.1f}% ({processed}/{total_records} records)")
            
            # Calculate environmental factors
            weather_factor = self._get_weather_factor(timestamp)
            seasonal_factor = self._get_seasonal_factor(timestamp)
            event_factor = self._get_event_factor(timestamp)
            
            # Generate trips for each station
            for station_info in self.station_locations:
                station_id = station_info['station_id']
                area_type = station_info['area_type']
                
                # Calculate base demand for this station type
                base_demand = self._calculate_base_demand(hour, day_of_week, area_type)
                
                # Apply all factors
                final_demand = base_demand * weather_factor * seasonal_factor * event_factor
                
                # Add some randomness and ensure non-negative
                demand = max(0, int(np.random.poisson(final_demand)))
                
                trips.append({
                    'timestamp': timestamp,
                    'station_id': station_id,
                    'station_name': station_info['name'],
                    'latitude': station_info['latitude'],
                    'longitude': station_info['longitude'],
                    'area_type': area_type,
                    'trip_count': demand,
                    'hour': hour,
                    'day_of_week': day_of_week,
                    'month': month,
                    'is_weekend': day_of_week >= 5,
                    'is_holiday': self._is_holiday(timestamp),
                    'weather_factor': weather_factor,
                    'seasonal_factor': seasonal_factor,
                    'event_factor': event_factor
                })
                
                processed += 1
        
        print(f"✅ Generated {len(trips)} trip records!")
        return pd.DataFrame(trips)
    
    def _calculate_base_demand(self, hour, day_of_week, area_type):
        """Calculate base demand based on time patterns and area type"""
        pattern = self.base_patterns[area_type]
        base = pattern['base_demand']
        
        # Peak hour multiplier
        if hour in pattern['peak_hours']:
            multiplier = 1.5
        elif hour in [hour + 1 for hour in pattern['peak_hours']] or hour in [hour - 1 for hour in pattern['peak_hours']]:
            multiplier = 1.2
        elif 6 <= hour <= 22:  # Normal day hours
            multiplier = 1.0
        else:  # Night hours
            multiplier = 0.3
        
        # Weekend adjustment
        if day_of_week >= 5:  # Weekend
            if area_type in ['business_district', 'educational']:
                multiplier *= 0.6  # Less demand on weekends
            elif area_type == 'tourist':
                multiplier *= 1.3  # More demand on weekends
        
        return base * multiplier
    
    def _get_weather_factor(self, timestamp):
        """Simulate weather impact on demand"""
        # Simulate Delhi weather patterns
        month = timestamp.month
        
        # Temperature effect (Delhi gets very hot in summer)
        if month in [5, 6, 7]:  # Hot months
            temp_factor = 0.7
        elif month in [12, 1, 2]:  # Cold months
            temp_factor = 0.8
        else:  # Pleasant months
            temp_factor = 1.0
        
        # Rain effect (monsoon season)
        if month in [7, 8, 9]:  # Monsoon
            rain_chance = 0.3
            if random.random() < rain_chance:
                rain_factor = 0.4  # Heavy rain reduces demand
            else:
                rain_factor = 1.0
        else:
            rain_factor = 1.0
        
        # Air quality effect (Delhi pollution)
        if month in [10, 11, 12, 1]:  # High pollution months
            aqi_factor = 0.9
        else:
            aqi_factor = 1.0
        
        return temp_factor * rain_factor * aqi_factor
    
    def _get_seasonal_factor(self, timestamp):
        """Seasonal demand variations"""
        month = timestamp.month
        
        # Delhi seasonal patterns
        if month in [10, 11, 3, 4]:  # Pleasant weather
            return 1.2
        elif month in [5, 6]:  # Very hot
            return 0.8
        elif month in [7, 8]:  # Monsoon
            return 0.9
        else:  # Winter
            return 1.0
    
    def _get_event_factor(self, timestamp):
        """Simulate special events impact"""
        # Random events that increase demand
        if random.random() < 0.05:  # 5% chance of special event
            return random.uniform(1.2, 1.8)
        else:
            return 1.0
    
    def _is_holiday(self, timestamp):
        """Check if date is a holiday (simplified)"""
        # Major Indian holidays (simplified)
        holidays = [
            (1, 26),   # Republic Day
            (8, 15),   # Independence Day
            (10, 2),   # Gandhi Jayanti
            (12, 25),  # Christmas
        ]
        
        return (timestamp.month, timestamp.day) in holidays
    
    def generate_weather_data(self, trip_data):
        """Generate corresponding weather data"""
        print("🌤️ Generating weather data...")
        
        weather_data = []
        
        for _, row in trip_data.iterrows():
            timestamp = row['timestamp']
            month = timestamp.month
            
            # Delhi weather simulation
            if month in [5, 6, 7]:  # Hot months
                temp = random.uniform(35, 45)
                humidity = random.uniform(30, 60)
            elif month in [12, 1, 2]:  # Cold months
                temp = random.uniform(8, 20)
                humidity = random.uniform(50, 80)
            else:  # Pleasant months
                temp = random.uniform(20, 35)
                humidity = random.uniform(40, 70)
            
            # Wind and precipitation
            wind_speed = random.uniform(5, 25)
            
            if month in [7, 8, 9]:  # Monsoon
                precipitation = random.uniform(0, 20) if random.random() < 0.4 else 0
            else:
                precipitation = random.uniform(0, 2) if random.random() < 0.1 else 0
            
            weather_data.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(wind_speed, 1),
                'precipitation': round(precipitation, 1),
                'aqi': random.randint(50, 300),  # Delhi AQI
                'weather_condition': self._get_weather_condition(temp, precipitation)
            })
        
        return pd.DataFrame(weather_data)
    
    def _get_weather_condition(self, temp, precipitation):
        """Determine weather condition"""
        if precipitation > 5:
            return 'rainy'
        elif temp > 35:
            return 'hot'
        elif temp < 15:
            return 'cold'
        else:
            return 'pleasant'
    
    def generate_events_data(self, trip_data):
        """Generate events data"""
        print("🎉 Generating events data...")
        
        events_data = []
        unique_dates = trip_data['timestamp'].dt.date.unique()
        
        for date in unique_dates:
            # Random events
            if random.random() < 0.1:  # 10% chance of event
                event_types = ['concert', 'festival', 'sports', 'conference', 'exhibition']
                
                events_data.append({
                    'date': date,
                    'event_type': random.choice(event_types),
                    'event_name': f"Delhi {random.choice(event_types).title()} Event",
                    'expected_attendance': random.randint(1000, 50000),
                    'location': random.choice([loc['base_area'] for loc in self.station_locations])
                })
        
        return pd.DataFrame(events_data)
    
    def save_data(self, trip_data, weather_data, events_data):
        """Save all generated data"""
        print("💾 Saving data...")
        
        # Create directories if they don't exist
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/processed', exist_ok=True)
        
        # Save trip data
        trip_data.to_csv('data/raw/trip_data.csv', index=False)
        print(f"✅ Saved trip data: {len(trip_data)} records")
        
        # Save weather data
        weather_data.to_csv('data/raw/weather_data.csv', index=False)
        print(f"✅ Saved weather data: {len(weather_data)} records")
        
        # Save events data
        events_data.to_csv('data/raw/events_data.csv', index=False)
        print(f"✅ Saved events data: {len(events_data)} records")
        
        # Save station information
        stations_df = pd.DataFrame(self.station_locations)
        stations_df.to_csv('data/raw/stations.csv', index=False)
        print(f"✅ Saved stations data: {len(stations_df)} records")
        
        # Create data summary
        summary = {
            'generation_date': datetime.now().isoformat(),
            'date_range': f"{self.start_date} to {self.end_date}",
            'num_stations': self.num_stations,
            'total_trip_records': len(trip_data),
            'total_weather_records': len(weather_data),
            'total_events': len(events_data),
            'city': self.city_name
        }
        
        with open('data/raw/data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("🎉 All data saved successfully!")
        return summary

# Main execution function
def main():
    """Main function to generate all data"""
    print("🚀 Starting Micro-Mobility Data Generation...")
    
    # Initialize generator
    generator = MicroMobilityDataGenerator(
        start_date='2024-01-01',
        end_date='2024-12-31',
        num_stations=50,
        city_name='Delhi'
    )
    
    # Generate data
    trip_data = generator.generate_trip_data()
    weather_data = generator.generate_weather_data(trip_data)
    events_data = generator.generate_events_data(trip_data)
    
    # Save data
    summary = generator.save_data(trip_data, weather_data, events_data)
    
    print("\n📊 Data Generation Summary:")
    print(f"Date Range: {summary['date_range']}")
    print(f"Stations: {summary['num_stations']}")
    print(f"Trip Records: {summary['total_trip_records']:,}")
    print(f"Weather Records: {summary['total_weather_records']:,}")
    print(f"Events: {summary['total_events']}")
    print(f"City: {summary['city']}")
    
    print("\n✅ Data generation complete! Ready for analysis.")

if __name__ == "__main__":
    main()