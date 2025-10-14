import random
from faker import Faker
import time

# Initialize Faker
fake = Faker()

# Function to generate a single Apache log entry
def generate_apache_log():
    ip = fake.ipv4()
    timestamp = fake.date_time_this_year().strftime('%d/%b/%Y:%H:%M:%S +0000')
    method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
    path = fake.uri_path()
    status = random.choice([200, 404, 500])
    size = random.randint(200, 5000)
    referrer = fake.url()
    user_agent = fake.user_agent()
    
    return f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {size} "{referrer}" "{user_agent}"\n'

# Function to append logs to a file
def append_logs_to_file(file_path, num_logs):
    with open(file_path, 'a') as log_file:
        for _ in range(num_logs):
            log_entry = generate_apache_log()
            log_file.write(log_entry)
            time.sleep(0.1)  # Sleep for a short duration if needed

# Example usage
log_file_path = './test.log'  # Path to your existing log file
number_of_logs_to_generate = 10  # Number of logs you want to append
append_logs_to_file(log_file_path, number_of_logs_to_generate)