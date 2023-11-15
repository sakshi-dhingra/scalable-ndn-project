import random

class SensorData:
    def __init__(self):
        self.data = {
            "heartrate": 0,
            "blood_pressure_systolic": 0,
            "blood_pressure_diastolic": 0,
            "body_temperature": 0.0,
            "respiratory_rate": 0,
            "blood_oxygen_level": 0.0,
            "glucose_level": 0.0,
            "cholesterol_level": 0.0,
        }

    def generate_random_data(self):
        self.data["heartrate"] = random.randint(60, 100)
        self.data["blood_pressure_systolic"] = random.randint(90, 120)
        self.data["blood_pressure_diastolic"] = random.randint(60, 80)
        self.data["body_temperature"] = round(random.uniform(36.0, 37.5), 1)
        self.data["respiratory_rate"] = random.randint(12, 20)
        self.data["blood_oxygen_level"] = round(random.uniform(95.0, 100.0), 1)
        self.data["glucose_level"] = round(random.uniform(70.0, 140.0), 1)
        self.data["cholesterol_level"] = round(random.uniform(120.0, 240.0), 1)

    def get_data(self, data_id=None):
        self.generate_random_data()
        if data_id in self.data:
            return self.data[data_id]
        else:
            return f"No data available for {data_id}"

# Example Usage
sensor_data = SensorData()

# Get all sensor data
all_sensor_data = sensor_data.get_data()
print("All Sensor Data:", all_sensor_data)

print(sensor_data.get_data("heartrate"))