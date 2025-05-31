from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import re
import random
import logging
from datetime import datetime
from config import get_config

# Initialize Flask app with configuration
app = Flask(__name__)
config = get_config()
app.config.from_object(config)
CORS(app)

# Setup logging
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedChatBot:
    def __init__(self):
        self.knowledge_base = {
            "greeting": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon"],
                "responses": [
                    "Hello! I'm your Data Engineering Assistant. How can I help you today?",
                    "Hi there! Ready to explore some data engineering concepts?",
                    "Hey! What data engineering topic would you like to discuss?"
                ]
            },
            "data_pipeline": {
                "patterns": ["pipeline", "etl", "data flow", "ingestion", "data pipeline"],
                "responses": [
                    "Data pipelines are automated workflows that extract, transform, and load data. Key components include data sources, transformation logic, and destinations. Popular tools are Apache Airflow, Prefect, and cloud-native services like AWS Glue.",
                    "A data pipeline orchestrates the movement and transformation of data from various sources to destinations. Think of it as an assembly line for data processing."
                ]
            },
            "databases": {
                "patterns": ["database", "sql", "nosql", "postgres", "mongodb", "db"],
                "responses": [
                    "In data engineering, you'll work with various databases: SQL databases (PostgreSQL, MySQL) for structured data, NoSQL (MongoDB, Cassandra) for flexible schemas, and analytical databases (Snowflake, BigQuery) for data warehousing.",
                    "Database choice depends on your use case: OLTP databases for transactions, OLAP for analytics, and NoSQL for unstructured data."
                ]
            },
            "streaming": {
                "patterns": ["streaming", "kafka", "real-time", "event", "stream processing"],
                "responses": [
                    "Stream processing handles real-time data flows. Apache Kafka is the most popular message broker, while Apache Flink and Spark Streaming handle stream processing. Key concepts include producers, consumers, topics, and partitions.",
                    "Real-time streaming is essential for applications requiring immediate data processing, like fraud detection or live analytics."
                ]
            },
            "cloud": {
                "patterns": ["aws", "azure", "gcp", "cloud", "s3", "bigquery"],
                "responses": [
                    "Cloud platforms offer managed data services: AWS (S3, Redshift, Glue), Google Cloud (BigQuery, Dataflow), Azure (Data Factory, Synapse). They handle infrastructure so you can focus on data logic.",
                    "Cloud services provide scalability and managed infrastructure, reducing operational overhead for data engineering teams."
                ]
            },
            "python": {
                "patterns": ["python", "pandas", "spark", "airflow", "programming"],
                "responses": [
                    "Python is essential for data engineering. Key libraries: Pandas for data manipulation, PySpark for big data processing, SQLAlchemy for database connections, and Airflow for workflow orchestration.",
                    "Python's ecosystem makes it perfect for data engineering: rich libraries, great community, and excellent integration with big data tools."
                ]
            }
        }
        self.fallback_responses = [
            "I'm not sure about that specific topic, but I can help you with data engineering concepts like pipelines, databases, streaming, cloud platforms, and Python tools. What would you like to explore?",
            "That's an interesting question! Can you provide more context so I can give you a better answer?",
            "I'd be happy to help! Could you rephrase that or ask about data pipelines, databases, or cloud platforms?"
        ]
    
    def get_response(self, user_input, conversation_history=None):
        user_input = user_input.lower().strip()
        
        # Log the interaction
        logger.info(f"User input: {user_input}")
        
        # Check for matches in knowledge base
        for intent, data in self.knowledge_base.items():
            for pattern in data["patterns"]:
                if pattern in user_input:
                    response = random.choice(data["responses"])
                    logger.info(f"Intent matched: {intent}")
                    return response
        
        # Fallback response
        response = random.choice(self.fallback_responses)
        logger.info("Using fallback response")
        return response

# Initialize bot
bot = EnhancedChatBot()

@app.route('/')
def index():
    return render_template('index.html', chatbot_name=app.config['CHATBOT_NAME'])

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        # Validate input
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'status': 'error'
            }), 400
        
        if len(user_message) > app.config['MAX_MESSAGE_LENGTH']:
            return jsonify({
                'error': f'Message too long. Maximum {app.config["MAX_MESSAGE_LENGTH"]} characters.',
                'status': 'error'
            }), 400
        
        # Generate response
        bot_response = bot.get_response(user_message, conversation_history)
        
        return jsonify({
            'response': bot_response,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )