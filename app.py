import os
import requests
import csv
import json
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

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

# Function to display a command-line menu
def display_menu():
    print("\n--- Nutrition App Menu ---")
    print("1. Search for a single food item")
    print("2. Search for multiple food items and calculate combined macros")
    print("3. Save results to a file (CSV or JSON)")
    print("4. Enter personal details for recommended daily intake comparison")
    print("5. Exit")

# Function to save results to a file
def save_results(results):
    print("How would you like to save the file?")
    file_format = input("Enter 'csv' or 'json': ").lower()
    file_name = input("Enter the file name: ")

    if file_format == 'csv':
        with open(f"{file_name}.csv", mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {file_name}.csv")
    elif file_format == 'json':
        with open(f"{file_name}.json", mode='w') as file:
            json.dump(results, file, indent=4)
        print(f"Results saved to {file_name}.json")
    else:
        print("Invalid format. Please try again.")

# Function to calculate recommended daily intake based on user info
def calculate_recommended_intake():
    try:
        age = int(input("Enter your age: "))
        weight = float(input("Enter your weight (kg): "))
        activity_level = input("Enter your activity level (low, moderate, high): ").lower()

        # Basic recommended intake estimates (can be improved for more accuracy)
        if activity_level == "low":
            calories = 2000
            protein = weight * 0.8  # grams per kg
        elif activity_level == "moderate":
            calories = 2500
            protein = weight * 1.0
        else:
            calories = 3000
            protein = weight * 1.2

        print(f"\nRecommended daily intake based on your profile:")
        print(f"Calories: {calories} kcal")
        print(f"Protein: {protein:.2f} g\n")
    except ValueError:
        print("Invalid input. Please enter numeric values for age and weight.")

# Main loop with menu options
results = []
while True:
    display_menu()
    choice = input("Enter your choice: ")

    if choice == '1':
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
            results.append(macros)
        else:
            print("Food item not found in the USDA API. Please try again.")

    elif choice == '2':
        combined_macros = {
            "carbs": 0, "protein": 0, "fat": 0, "calories": 0, "fiber": 0, "quantity": 0
        }
        num_items = int(input("How many food items would you like to search? "))
        for _ in range(num_items):
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
                combined_macros["carbs"] += macros["carbs"]
                combined_macros["protein"] += macros["protein"]
                combined_macros["fat"] += macros["fat"]
                combined_macros["calories"] += macros["calories"]
                combined_macros["fiber"] += macros["fiber"]
                combined_macros["quantity"] += macros["quantity"]

        print(f"\nCombined Macros for {num_items} food items:")
        print(f"  Carbohydrates: {combined_macros['carbs']}g")
        print(f"  Protein: {combined_macros['protein']}g")
        print(f"  Fat: {combined_macros['fat']}g")
        print(f"  Calories: {combined_macros['calories']} kcal")
        print(f"  Dietary Fiber: {combined_macros['fiber']}g\n")

    elif choice == '3':
        if results:
            save_results(results)
        else:
            print("No results to save. Search for food items first.")

    elif choice == '4':
        calculate_recommended_intake()

    elif choice == '5':
        print("Exiting the program. Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")