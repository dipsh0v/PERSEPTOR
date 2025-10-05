from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import uuid
from modules.qa_module import create_qa_system
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize QA system
qa_system = None

def get_qa_system(openai_api_key):
    global qa_system
    if not qa_system:
        qa_system = create_qa_system(openai_api_key=openai_api_key)
    return qa_system

# Test route
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

@app.route('/api/generate_rule', methods=['POST', 'OPTIONS'])
def generate_rule():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        openai_api_key = data.get('openai_api_key')
        
        if not prompt or not openai_api_key:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get QA system instance
        qa = get_qa_system(openai_api_key)
        
        # Generate rule using QA system
        result = qa._generate_response(prompt, "sigma")
        
        if not result or "rule" not in result:
            return jsonify({'error': 'Failed to generate rule'}), 500

        # Calculate confidence score
        confidence_result = qa.confidence_calculator.calculate_confidence(result["rule"], result.get("test_cases", []))

        # Ensure author is set to PERSEPTOR
        if "rule" in result and isinstance(result["rule"], dict):
            result["rule"]["author"] = "PERSEPTOR"
            result["rule"]["date"] = datetime.now().strftime('%Y/%m/%d')

        return jsonify({
            'rule': result["rule"],
            'explanation': result.get("explanation", ""),
            'test_cases': result.get("test_cases", []),
            'mitre_techniques': result.get("mitre_techniques", []),
            'recommendations': result.get("recommendations", []),
            'references': result.get("references", []),
            'confidence_score': confidence_result["overall_score"],
            'component_scores': confidence_result["component_scores"],
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in generate_rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port, host='0.0.0.0') 