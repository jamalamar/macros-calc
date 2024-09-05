# Nutrition App

This Python-based command-line app allows users to search for food items, retrieve nutritional information from the USDA FoodData Central API, and calculate detailed macro- and micronutrient data. Users can also compare their intake to recommended daily values based on their age, weight, and activity level.

## Features
- Search for a single or multiple food items.
- Calculate and display combined nutritional information.
- Save search results as CSV or JSON.
- Compare nutritional intake with recommended daily values.

## Requirements
- Python 3.x
- `requests` library
- `python-dotenv` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nutrition-app.git
   ```

2. Navigate to the project directory:
   ```bash
   cd nutrition-app
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file to store your USDA API key:
   ```
   API_KEY="your_api_key_here"
   ```

## Usage

Run the program:
```bash
python app.py
```

Follow the on-screen prompts to search for food items, calculate macros, or save the results to a file.

## Future Improvements
- Add more detailed recommended daily intake calculations.
- Extend support for more nutrients.

---

Feel free to update any sections as needed!
