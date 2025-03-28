# Data Room Prompt Generator

A web application that helps users create prompts for analyzing data rooms. This tool allows users to input categories and questions, then generates appropriate prompts that can be used with AI systems to extract information from data rooms.

## Features

- Input categories and questions in a user-friendly interface
- Generate prompts automatically using either:
  - Simulated responses (no API key required)
  - Anthropic's Claude API (if API key is available)
- Export results to CSV format
- Pre-defined category examples for common data room sections

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install flask python-dotenv requests
```

3. (Optional) If you want to use the Anthropic API:
   - Create a `.env` file in the project directory
   - Add your Anthropic API key: `ANTHROPIC_API_KEY=your_api_key_here`

## Usage

1. Run the application:

```bash
# To use the version without Anthropic API integration:
python app.py

# OR to use the version with Anthropic API integration:
python app_with_anthropic.py
```

2. Open your web browser and navigate to: `http://localhost:5000`

3. Use the application:
   - Click on example categories or enter your own category and question
   - Click "Add" to add rows to the table
   - Click "Generate Prompts" to create prompts for each row
   - Click "Export to CSV" to download the results

## How It Works

1. **Input**: Users enter categories (e.g., "Financial Information") and questions (e.g., "Balance Sheet")
2. **Processing**: The application generates appropriate prompts for each category/question pair
3. **Output**: Users can view the generated prompts and export them to CSV

## Example Use Cases

- Due diligence for mergers and acquisitions
- Investment analysis
- Legal document review
- Compliance audits
- Financial analysis

## Sample Categories

The application includes example buttons for common data room categories:

- Owners & Managers
- Summary & Background
- Financial Information
- Legal & Compliance
- Operations
- Market & Customers

## CSV Export Format

The exported CSV file contains three columns (without headers):
1. Category
2. Question
3. Prompt

Example:
```
"Financial Information","Balance Sheet","Analyze the balance sheet and provide a summary of assets, liabilities, and equity. If no balance sheet is available, return 'Balance sheet not available'."
```

## Notes

- The application works without an Anthropic API key by using simulated responses
- If an Anthropic API key is provided, you can toggle between using the API or simulated responses
- The simulated responses include templates for common categories and questions, with generic fallbacks for other inputs