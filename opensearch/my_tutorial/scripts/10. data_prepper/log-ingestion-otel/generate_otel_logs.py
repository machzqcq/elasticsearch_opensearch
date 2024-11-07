# call http://localhost:5002/rolldice?user=anonymous
import logging
from random import randint
from flask import Flask, request
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource
from datetime import datetime
from pathlib import Path

# Set up Flask app
app = Flask(__name__)

# Set up logging to a file with a timestamped filename
current_time = datetime.now().strftime("%Y%m%d")
# make directory sample_logs if not exists using pathlib
Path("sample_logs").mkdir(parents=True, exist_ok=True)
log_filename = f"sample_logs/log_{current_time}.log"

# Configure logging to write to a file
logging.basicConfig(level=logging.DEBUG, 
                    filename=log_filename, 
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up OpenTelemetry logging
resource = Resource.create({"service.name": "demo-dice"})
logger_provider = LoggerProvider(resource=resource)
otlp_exporter = OTLPLogExporter()
handler = LoggingHandler(logger_provider=logger_provider)  # Correctly pass logger_provider

# Acquire a tracer
tracer = trace.get_tracer("dice-roller")

@app.route("/rolldice")
def roll_dice():
    user = request.args.get('user', "anonymous")
    rolls = [do_roll(user) for _ in range(100)]
    
    # Log each roll with OpenTelemetry and to the file
    for roll in rolls:
        message = f"User: {user} rolled: {roll}"
        logging.getLogger("dice_logger").info(message)
        logging.info(message)  # Log to the file as well
    
    return {"rolls": rolls}

def do_roll(user):
    # Simulate rolling a dice (1-6)
    with tracer.start_as_current_span("roll"):
        result = randint(1, 6)
        return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)