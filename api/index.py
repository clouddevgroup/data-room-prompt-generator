from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import time
import random
import requests
import csv
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up template folder path for local and Vercel environments
template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
if not os.path.exists(template_path):
    # If not found, try relative to current directory (for Vercel)
    template_path = os.path.join(os.getcwd(), 'templates')

app = Flask(__name__, template_folder=template_path)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Get Anthropic API key from environment variable (if available)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

@app.route('/')
def index():
    return render_template('data_room_prompt_generator.html')

@app.route('/import-csv', methods=['POST'])
def import_csv():
    app.logger.info("Import CSV request received")
    
    if 'file' not in request.files:
        app.logger.error("No file part in request")
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    app.logger.info(f"File received: {file.filename}")
    
    if file.filename == '':
        app.logger.error("Empty filename")
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.endswith('.csv'):
        app.logger.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "File must be a CSV"}), 400
    
    try:
        # Read the CSV file
        file_content = file.stream.read().decode("utf-8")
        app.logger.debug(f"CSV content (first 100 chars): {file_content[:100]}")
        
        stream = StringIO(file_content, newline=None)
        csv_reader = csv.reader(stream)
        
        # Skip header row if it exists
        try:
            header = next(csv_reader)
            app.logger.debug(f"CSV header: {header}")
        except StopIteration:
            app.logger.error("CSV file is empty")
            return jsonify({"error": "CSV file is empty"}), 400
        
        # Process the rest of the rows
        imported_data = []
        for row_num, row in enumerate(csv_reader):
            app.logger.debug(f"Processing row {row_num}: {row}")
            
            if len(row) < 2:
                app.logger.warning(f"Skipping row {row_num} with insufficient columns: {row}")
                continue  # Skip rows with insufficient columns
                
            item = {
                "category": row[0].strip(),
                "question": row[1].strip(),
                "prompt": row[2].strip() if len(row) > 2 else ""
            }
            
            if item["category"] and item["question"]:  # Only add if both fields have values
                imported_data.append(item)
                app.logger.debug(f"Added item: {item}")
            else:
                app.logger.warning(f"Skipping row {row_num} with empty category or question")
        
        if not imported_data:
            app.logger.error("No valid data found in CSV")
            return jsonify({"error": "No valid data found in CSV"}), 400
            
        # Ensure proper content type and response format
        app.logger.info(f"Successfully imported {len(imported_data)} items")
        response = jsonify(imported_data)
        response.headers.add('Content-Type', 'application/json')
        return response
        
    except Exception as e:
        app.logger.error(f"CSV import error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing CSV: {str(e)}"}), 400

@app.route('/generate-prompts', methods=['POST'])
def generate_prompts():
    data = request.json
    use_anthropic = request.args.get('use_anthropic', 'false').lower() == 'true'
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    for item in data:
        category = item['category']
        question = item['question']
        
        # Generate prompt using either Anthropic API or local function
        if use_anthropic and ANTHROPIC_API_KEY:
            prompt = generate_prompt_with_anthropic(category, question)
        else:
            prompt = generate_prompt_locally(category, question)
            # Add a small delay to simulate API call
            time.sleep(0.5)
        
        item['prompt'] = prompt
    
    return jsonify(data)

def generate_prompt_with_anthropic(category, question):
    """
    Generate a prompt using Anthropic's Claude API
    """
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Create the system prompt that explains the context and task
        system_prompt = """
        You are an expert at creating clear, specific prompts for data room analysis.
        Your task is to create a prompt that would help an AI analyze information from a data room.
        The prompt should be specific to the category and question provided.
        """
        
        # Create the user message with the category and question
        user_message = f"""
        I need to create a prompt for analyzing information in a data room.
        
        Category: {category}
        Question: {question}
        
        Please generate a clear, specific prompt that would help an AI extract or analyze this information from a data room.
        The prompt should be direct and include instructions on what to do if the information is not available.
        For example, if the question is about a shareholder list, a good prompt might be:
        "Provide a full list of shareholders. If there are no shareholders say return 'Shareholder information not available'."
        
        Return only the prompt text without any additional explanation.
        """
        
        # Call Anthropic API
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 300,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
        )
        
        if response.status_code != 200:
            print(f"Error from Anthropic API: {response.text}")
            return f"Error generating prompt: API returned status code {response.status_code}"
        
        # Extract the generated prompt
        response_data = response.json()
        generated_prompt = response_data.get("content", [{"text": "Error: No content returned"}])[0]["text"].strip()
        
        return generated_prompt
    
    except Exception as e:
        print(f"Error generating prompt with Anthropic: {str(e)}")
        return f"Error generating prompt: {str(e)}"

def generate_prompt_locally(category, question):
    """
    Generate a prompt based on the category and question.
    This function simulates what an LLM like Claude would do.
    """
    # Dictionary of example prompts for common categories
    prompt_templates = {
        "Owners & Managers": {
            "Shareholder List": "Provide a full list of shareholders. If there are no shareholders, return 'Shareholder information not available'.",
            "Management Team": "List all members of the management team with their roles and responsibilities. If this information is not available, return 'Management team information not available'.",
            "Organizational Chart": "Describe the organizational structure based on the organizational chart. If no chart is available, return 'Organizational chart not available'."
        },
        "Summary & Background": {
            "Summary of Company": "Provide a comprehensive summary of the business, including products and services, customers, operations, locations, and scope of activities. If this information is not available, return 'Company summary not available'.",
            "Company History": "Outline the company's history including founding date, major milestones, and significant events. If this information is not available, return 'Company history not available'.",
            "Mission Statement": "State the company's mission statement. If not available, return 'Mission statement not available'."
        },
        "Financial Information": {
            "Balance Sheet": "Analyze the balance sheet and provide a summary of assets, liabilities, and equity. If no balance sheet is available, return 'Balance sheet not available'.",
            "Income Statement": "Summarize the income statement, highlighting revenue, expenses, and profit/loss. If no income statement is available, return 'Income statement not available'.",
            "Cash Flow Statement": "Review the cash flow statement and summarize operating, investing, and financing activities. If no cash flow statement is available, return 'Cash flow statement not available'."
        },
        "Legal & Compliance": {
            "Contracts": "List all major contracts and summarize key terms and obligations. If no contract information is available, return 'Contract information not available'.",
            "Litigation": "Summarize any ongoing or past litigation involving the company. If no litigation information is available, return 'No litigation information available'.",
            "Regulatory Compliance": "Describe the company's compliance with relevant regulations. If this information is not available, return 'Regulatory compliance information not available'."
        },
        "Operations": {
            "Supply Chain": "Describe the company's supply chain, including key suppliers and logistics. If this information is not available, return 'Supply chain information not available'.",
            "Manufacturing Process": "Explain the manufacturing process and production capabilities. If this information is not available, return 'Manufacturing process information not available'.",
            "Quality Control": "Detail the quality control measures and standards in place. If this information is not available, return 'Quality control information not available'."
        },
        "Market & Customers": {
            "Market Analysis": "Provide an analysis of the market size, trends, and growth potential. If this information is not available, return 'Market analysis not available'.",
            "Customer Base": "Describe the customer base, including major clients and customer demographics. If this information is not available, return 'Customer information not available'.",
            "Competitive Landscape": "Analyze the competitive landscape, identifying key competitors and the company's competitive advantages. If this information is not available, return 'Competitive landscape information not available'."
        }
    }
    
    # Check if we have a template for this category and question
    if category in prompt_templates and question in prompt_templates[category]:
        return prompt_templates[category][question]
    
    # If not in our templates, generate a generic prompt based on the category and question
    generic_prompts = [
        f"Analyze the {question.lower()} information in the {category.lower()} section. If this information is not available, return '{question} information not available'.",
        f"Extract and summarize all details related to {question.lower()} from the {category.lower()} documents. If no information is found, return '{question} details not available'.",
        f"Provide a comprehensive overview of {question.lower()} based on the {category.lower()} data. If this information cannot be found, return 'No {question.lower()} information available'.",
        f"Review the {category.lower()} section and extract all {question.lower()} information. If no relevant information exists, return '{question} information not found'.",
        f"Summarize the key points about {question.lower()} from the {category.lower()} documents. If this information is missing, return '{question} information missing'."
    ]
    
    return random.choice(generic_prompts)

@app.route('/api-status', methods=['GET'])
def api_status():
    """Check if the Anthropic API key is configured"""
    if ANTHROPIC_API_KEY:
        return jsonify({"status": "available"})
    else:
        return jsonify({"status": "unavailable"})

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f'Server error: {error}')
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    app.logger.error(f'Bad request: {error}')
    return jsonify({"error": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    app.logger.error(f'Not found: {error}')
    return jsonify({"error": "Not found"}), 404

# This is for local development
if __name__ == '__main__':
    # Make sure the templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Enable more detailed logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    app.run(debug=True, port=5001)

# Vercel serverless handler
def handler(request):
    return app