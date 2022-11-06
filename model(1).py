"""The coolest farm game ever - Plainview, Illinois"""

from matplotlib import pyplot as plt
import requests
from datetime import date, timedelta
import matplotlib.pyplot as plt
import base64
from io import BytesIO

API_KEY_LL = "92a774402a983da8264765c990b63e3b"
API_KEY_FC = "7c911790730bde1aa1212670e8737aad"
DAYS = 30
CURRENT_DATE = date.today()


# Uses user address to return data extracted from positionstack API
def get_json_data(user_address):
  forward = "http://api.positionstack.com/v1/forward"
  url = f"{forward}?access_key={API_KEY_LL}&query={user_address}"  # Formats url with raw data
  r = requests.get(url)
  return r.json()


# Extracts latitude and longitude of an address inputted by user
def get_ll(user_address):
  lat_lon = []
  addy_data = get_json_data(user_address)
  if addy_data == {'data': []}:
    raise ValueError("Address is invalid.")
    quit()
  lat = addy_data['data'][0]['latitude']
  lon = addy_data['data'][0]['longitude']
  lat_lon.append(lat)
  lat_lon.append(lon)
  return lat_lon


def get_forecast_dict(user_address):
  lat_lon = get_ll(user_address)
  lat = lat_lon[0]
  lon = lat_lon[1]
  units = "imperial"
  forward = "https://pro.openweathermap.org/data/2.5/forecast/climate"
  url = f"{forward}?lat={lat}&lon={lon}&cnt={DAYS}&appid={API_KEY_FC}&units={units}"
  r = requests.get(url)
  return r.json()


# FILLS DICT STRUCT WITH FORECAST DATA FROM API
def add_values(forecast_list):
  forecast_values: dict[str, list[float]] = {}
  rainfall_values: list[float] = []
  temp_values: list[float] = []
  humidity_values: list[float] = []
  for i in range(len(forecast_list)):
    if 'rain' in forecast_list[i]:
      rainfall_values.append(forecast_list[i]['rain'])
    else:
      rainfall_values.append(0.0)
    temp_values.append(forecast_list[i]['temp']['day'])
    humidity_values.append(forecast_list[i]['humidity'])

  forecast_values['rainfall'] = rainfall_values
  forecast_values['temperature'] = temp_values
  forecast_values['humidity'] = humidity_values

  return forecast_values


class Model:
  """Mathematical model of relationship between variables."""
  rainfall: float  # daily rainfall in inches
  temperature: float  # temperature in fahrenheit
  humidity: float  # humidity
  ideal_temperature: int  #ideal temperature based on selected plant
  ideal_humidity: int  #ideal humidity based on selected plant
  ideal_rain: int  #ideal DAILY rain based on selected plant
  global user_choice

  def __init__(self, rainfall: float, temp: float, humidity: float,
               user_choice: str):
    """Assigns given values to variables."""
    self.rainfall = rainfall
    self.temperature = temp
    self.humidity = humidity
    self.user_choice = user_choice
    if self.user_choice.lower() == "kale":
      self.ideal_temperature = 60
      self.ideal_humidity = 85
      self.ideal_rain = 1.2
    elif self.user_choice.lower() == "zucchini":
      self.ideal_temperature = 75
      self.ideal_humidity = 75
      self.ideal_rain = 1
    elif self.user_choice.lower() == "eggplant":
      self.ideal_temperature = 85
      self.ideal_humidity = 65
      self.ideal_rain = 1
    else:
      raise ValueError("Invalid Plant Selected")

  def calculate(self) -> float:
    """Math equation that combines variables and results a crop yield percentage."""

    # MATH MODEL KEY:
    # Gives each variable a score 0-1 (0-100%)
    # Outputs a 1 if in ideal range
    # Output becomes smaller, as variable becomes further out of ideal range
    # Then averages the scores for a final score

    rainfall_score: float
    if self.rainfall == self.ideal_rain:
      rainfall_score = 1
    elif self.rainfall < 0 or self.rainfall > 3:
      rainfall_score = 0
    elif self.rainfall < self.ideal_rain:
      rainfall_score = 1 - (
        (self.ideal_rain - self.rainfall) / self.ideal_rain)
    elif self.rainfall > self.ideal_rain:
      rainfall_score = 1 - (
        (self.rainfall - self.ideal_rain) / self.ideal_rain)

    temperature_score: float  # Ideal crop temperature assigned above
    if self.temperature == self.ideal_temperature:  # IDEAL TEMP
      temperature_score = 1
    elif self.temperature < 0 or self.temperature > 120:  # EXCEEDS BOUNDS
      temperature_score = 0
    elif self.temperature < self.ideal_temperature:  # UNDER IDEAL
      temperature_score = 1 - (
        (self.ideal_temperature - self.temperature) / self.ideal_temperature)
    elif self.temperature > self.ideal_temperature:  # OVER IDEAL
      temperature_score = 1 - (
        (self.temperature - self.ideal_temperature) / self.ideal_temperature)

    humidity_score: float  # % humidity that is ideal assigned above
    if self.humidity == self.ideal_humidity:  # IDEAL
      humidity_score = 1
    elif self.humidity < 0 or self.humidity > 100:  # EXCEEDS BOUNDS
      humidity_score = 0
    elif self.humidity < self.ideal_humidity:
      humidity_score = 1 - (
        (self.ideal_humidity - self.humidity) / self.ideal_humidity)
    elif self.humidity > self.ideal_humidity:  # OVER IDEAL
      humidity_score = 1 - (
        (self.humidity - self.ideal_humidity) / self.ideal_humidity)

    score: float = ((rainfall_score * 5) + (temperature_score * 3) +
                    (humidity_score * 2)) / 10
    return score


def main(address: str, plant: str):
  """Creates and runs model."""
  user_address: str = address
  user_choice: str = plant

  # USE ADDRESS TO GET WEATHER DATA
  forecast_raw = get_forecast_dict(user_address)
  forecast_list_raw = forecast_raw['list']
  forecast_values = add_values(forecast_list_raw)

  # CHECKS OUTPUT FOR NEXT 7 DAYS
  attempts: dict[int, Model] = {}
  for i in range(DAYS):
    attempts[i + 1] = Model(forecast_values['rainfall'][i],
                            forecast_values['temperature'][i],
                            forecast_values['humidity'][i],
                            user_choice).calculate()

  # OUTPUTS HIGHEST DAY
  max: float = 0.0
  max_day: float = 0.0
  x_values: list[str] = []
  for day in attempts:
    x_values.append(day)
    if attempts[day] > max:
      max = attempts[day]
      max_day = day
  
  result_date = (CURRENT_DATE + timedelta(days=max_day)).strftime("%B %d, %Y")
  return_statement: dict[str, float] = {}
  return_statement['plant_days'] = result_date
  return_statement['success_rate'] = int(round(max, 2) * 100)
  return return_statement

  # GRAPH
#   y_values: list[float] = []
#   for success in attempts.values():
#     y_values.append(success)
#   print(
#     f"We recommend planting on day {CURRENT_DATE + timedelta(days=max_day)} as it has the highest success rate of {round(max,3)*100}%."
#   )
#   plt.scatter(x_values, y_values, color="darkgreen")
#   plt.title(
#     f"Percentage of {user_choice.capitalize()} Success for Each Day in the Next 2 Weeks",
#     fontname="Arial",
#     fontsize=15)
#   plt.xlabel("Day", fontname="Arial", fontsize=10)
#   plt.ylabel("Percentage of Success", fontname="Arial", fontsize=10)
#   plt.scatter(max_day, max, c="lime")
#   plt.super.save("graph.png")
#   plt.show()



# fig = plt.figure()
# #plot sth

# # plt.savefig("graph" + str(GraphNum))