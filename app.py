import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API_KEY in your script
API_KEY = os.getenv('API_KEY')

# Function to fetch data from USDA API and calculate detailed macros
def fetch_from_usda(food, quantity):
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food}&api_key={API_KEY}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()

        data = response.json()
        if data.get('foods'):
            food_data = data['foods'][0]
            
            nutrients = {nutrient['nutrientId']: nutrient['value'] for nutrient in food_data.get('foodNutrients', [])}
            
            carbs = nutrients.get(1005, 0) / 100 * quantity
            protein = nutrients.get(1003, 0) / 100 * quantity
            fat = nutrients.get(1004, 0) / 100 * quantity
            calories = nutrients.get(1008, 0) / 100 * quantity  # Caloric value
            fiber = nutrients.get(1079, 0) / 100 * quantity  # Dietary fiber
            
            return {
                "carbs": carbs,
                "protein": protein,
                "fat": fat,
                "calories": calories,
                "fiber": fiber,
                "quantity": quantity,
                "food_description": food_data.get('description', 'N/A')
            }
        else:
            print("No foods found in the USDA database.")
    except requests.RequestException as e:
        print(f"Error fetching data from the USDA API: {e}")
    
    return None

# Main loop to get input and display results
while True:
    food = input("Enter the food item: ")
    quantity_str = input("Enter the quantity (in grams): ")

    try:
        quantity = float(quantity_str)
        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
    except ValueError as e:
        print(f"Invalid quantity input: {e}")
        continue

    macros = fetch_from_usda(food, quantity)
    if macros:
        print(f"\nNutrition for {macros['food_description']} ({macros['quantity']}g):")
        print(f"  Carbohydrates: {macros['carbs']}g")
        print(f"  Protein: {macros['protein']}g")
        print(f"  Fat: {macros['fat']}g")
        print(f"  Calories: {macros['calories']} kcal")
        print(f"  Dietary Fiber: {macros['fiber']}g\n")
    else:
        print("Food item not found in the USDA API. Please try again.")