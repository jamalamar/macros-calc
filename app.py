import os
import requests
import csv
import json
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()  # Load API key from .env file
API_KEY = os.getenv('API_KEY')  # Get the API key from the environment variables

# Function to fetch nutrition data from USDA API
def fetch_from_usda(food, quantity):
    # Construct the search URL with the food query and API key
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food}&api_key={API_KEY}"
    try:
        # Make a GET request to the USDA API
        response = requests.get(search_url)
        # Raise an error if the request was unsuccessful
        response.raise_for_status()
        # Convert the response to JSON format
        data = response.json()

        # Check if any food items were found
        if data.get('foods'):
            food_data = data['foods'][0]  # Get the first food item found
            # Extract nutrient information into a dictionary
            nutrients = {nutrient['nutrientId']: nutrient['value'] for nutrient in food_data.get('foodNutrients', [])}

            # Return calculated nutrition values based on the requested quantity
            return {
                "carbs": nutrients.get(1005, 0) / 100 * quantity,
                "protein": nutrients.get(1003, 0) / 100 * quantity,
                "fat": nutrients.get(1004, 0) / 100 * quantity,
                "calories": nutrients.get(1008, 0) / 100 * quantity,
                "fiber": nutrients.get(1079, 0) / 100 * quantity,
                "quantity": quantity,
                "food_description": food_data.get('description', 'N/A')  # Get food description or default to 'N/A'
            }
        print("No foods found in the USDA database.")  # Inform user if no food was found
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")  # Print error message if there's an issue with the request

    return None  # Return None if there was an error or no food was found

# Function to display the main menu options
def display_menu():
    menu_options = [
        "1. Search for a single food item",
        "2. Search for multiple food items and calculate combined macros",
        "3. Save results to a file (CSV or JSON)",
        "4. Enter personal details for recommended daily intake comparison",
        "5. Exit"
    ]
    print("\n--- Nutrition App Menu ---")
    print("\n".join(menu_options))  # Print menu options

# Function to save results in either CSV or JSON format
def save_results(results):
    file_format = input("How would you like to save the file? (csv/json): ").lower()  # Get desired file format
    file_name = input("Enter the file name (without extension): ")  # Get file name from user

    try:
        # Save as CSV
        if file_format == 'csv':
            with open(f"{file_name}.csv", mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=results[0].keys())  # Create a CSV writer
                writer.writeheader()  # Write header row
                writer.writerows(results)  # Write result rows
            print(f"Results saved to {file_name}.csv")  # Inform user of successful save
        # Save as JSON
        elif file_format == 'json':
            with open(f"{file_name}.json", mode='w') as file:
                json.dump(results, file, indent=4)  # Write results to JSON file with indentation
            print(f"Results saved to {file_name}.json")  # Inform user of successful save
        else:
            print("Invalid format. Please try again.")  # Handle invalid format case
    except Exception as e:
        print(f"Error saving file: {e}")  # Print error message if there's an issue saving the file

# Function to calculate Basal Metabolic Rate (BMR)
def calculate_bmr(weight, height, age, gender):
    return (
        10 * weight + 6.25 * height - 5 * age + (5 if gender == 'male' else -161)  # BMR calculation formula
    )

# Function to calculate Total Daily Energy Expenditure (TDEE) based on activity level
def calculate_tdee(bmr, activity_level):
    # Define activity multipliers
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very active': 1.9
    }
    return bmr * activity_factors.get(activity_level, 1.2)  # Return TDEE based on activity level

# Function to calculate recommended macronutrient distribution based on TDEE
def recommended_macros(tdee):
    # Define macronutrient ratios
    ratios = {
        "carbs": (45, 65),
        "protein": (10, 35),
        "fat": (20, 35)
    }
    # Calculate recommended ranges for each nutrient
    return {nutrient: [(tdee * percent / 4 if nutrient != 'fat' else tdee * percent / 9) for percent in ratio] for nutrient, ratio in ratios.items()}

# Function to calculate recommended intake based on personal details
def calculate_recommended_intake():
    try:
        # Get personal details from user
        age = int(input("Enter your age: "))
        weight = float(input("Enter your weight (kg): "))
        height = float(input("Enter your height (cm): "))
        gender = input("Enter your gender (male/female): ").lower()
        activity_level = input("Enter your activity level (sedentary, light, moderate, active, very active): ").lower()

        # Calculate BMR and TDEE using inputted data
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        macros = recommended_macros(tdee)  # Calculate recommended macros

        # Display recommended intake
        print(f"\nRecommended daily intake based on your profile:")
        print(f"Calories: {tdee:.2f} kcal")
        print(f"Carbohydrates: {macros['carbs'][0]:.2f}g - {macros['carbs'][1]:.2f}g")
        print(f"Protein: {macros['protein'][0]:.2f}g - {macros['protein'][1]:.2f}g")
        print(f"Fat: {macros['fat'][0]:.2f}g - {macros['fat'][1]:.2f}g\n")
    except ValueError:
        print("Invalid input. Please enter valid numeric values.")  # Handle invalid input case

# Main function to run the app
def main():
    results = []  # Initialize an empty list to store results
    
    while True:  # Loop indefinitely until the user decides to exit
        display_menu()  # Display the menu options
        choice = input("Enter your choice: ")  # Get user choice

        # Option 1: Search for a single food item
        if choice == '1':
            food = input("Enter the food item: ")  # Get food item from user
            quantity_str = input("Enter the quantity (in grams): ")  # Get quantity from user

            try:
                quantity = float(quantity_str)  # Convert quantity to float
                if quantity <= 0:
                    raise ValueError("Quantity must be a positive number.")  # Ensure quantity is positive
            except ValueError as e:
                print(f"Invalid quantity input: {e}")  # Handle invalid quantity input
                continue  # Go back to the start of the loop

            # Fetch nutrition data for the specified food item
            macros = fetch_from_usda(food, quantity)
            if macros:
                # Display nutrition information
                print(f"\nNutrition for {macros['food_description']} ({macros['quantity']}g):")
                for key in ['carbs', 'protein', 'fat', 'calories', 'fiber']:
                    print(f"  {key.capitalize()}: {macros[key]}g")
                results.append(macros)  # Append the result to the list
            else:
                print("Food item not found in the USDA API. Please try again.")  # Inform if not found

        # Option 2: Search for multiple food items
        elif choice == '2':
            combined_macros = {key: 0 for key in ["carbs", "protein", "fat", "calories", "fiber", "quantity"]}
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
                    for key in combined_macros:
                        combined_macros[key] += macros[key]

            print(f"\nCombined Macros for {num_items} food items:")
            for key in combined_macros:
                print(f"  {key.capitalize()}: {combined_macros[key]}g")

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

if __name__ == "__main__":
    main()
