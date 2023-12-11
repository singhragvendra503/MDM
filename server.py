from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import subprocess
import threading


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '8601',
    'database': 'system_info',
}

# Establish a connection to the MySQL database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

def update_ip_data(username, private_ip, public_ip, mac_address):
    try:
        # SQL query to insert or update data
        sql = "INSERT INTO ip_data (username, private_ip, public_ip, mac_address) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE private_ip=%s, public_ip=%s, mac_address=%s"
        values = (username, private_ip, public_ip, mac_address, private_ip, public_ip, mac_address)

        cursor.execute(sql, values)
        connection.commit()

        print(f"Data for {username} stored in the database.")
    except Exception as e:
        print(f"Error updating database: {str(e)}")

def get_ip_info(username):
    try:
        # SQL query to fetch data based on username
        sql = "SELECT username, private_ip, public_ip, mac_address FROM ip_data WHERE username = %s"
        values = (username,)

        cursor.execute(sql, values)
        result = cursor.fetchone()

        if result:
            # Convert result to a dictionary for JSON response
            ip_info = {
                'username': result[0],
                'private_ip': result[1],
                'public_ip': result[2],
                'mac_address': result[3]
            }
            return ip_info
        else:
            return None
    except Exception as e:
        print(f"Error fetching data from database: {str(e)}")
        return None
def get_username_from_database():
    try:
        # Modify this query based on your database schema and criteria to fetch the username
        sql = "SELECT username FROM users WHERE some_criteria = %s"
        values = (some_value,)  # Modify this based on your criteria value

        cursor.execute(sql, values)
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Error fetching username from database: {str(e)}")
        return None
def get_all_systems():
    try:
        # SQL query to fetch all system data
        sql = "SELECT username, private_ip, public_ip, mac_address FROM ip_data"
        cursor.execute(sql)
        results = cursor.fetchall()

        # Convert results to a list of dictionaries for JSON response
        systems_info = []
        for result in results:
            system_info = {
                'username': result[0],
                'private_ip': result[1],
                'public_ip': result[2],
                'mac_address': result[3]
            }
            systems_info.append(system_info)

        return systems_info
    except Exception as e:
        print(f"Error fetching all system data from database: {str(e)}")
        return None

process = None  # Global variable to store the subprocess

def execute_command_thread(ip_address):
    global process
    command = f"/home/ubuntu/noVNC/utils/novnc_proxy --vnc {ip_address}:5900"
    process = subprocess.Popen(command, shell=True)
    process.wait()

@app.route('/connect', methods=['POST'])
def connect():
    global process

    data = request.get_json()

    if 'ip_address' not in data:
        return jsonify({'error': 'Missing "ip_address" parameter'}), 400

    ip_address = data['ip_address']

    # Check if there's an existing process and terminate it
    if process is not None and process.poll() is None:
        process.terminate()
        process.wait()

    # Start a new thread to execute the command
    threading.Thread(target=execute_command_thread, args=(ip_address,), daemon=True).start()

    return jsonify({'status': 'success'})

@app.route('/update_ip', methods=['POST'])
def update_ip():
    try:
        # Get JSON data directly from the request
        data = request.get_json(force=True, silent=True)
        
        # Check if data is None or if the required keys are not present
        if data is None or 'username' not in data or 'mac_address' not in data:
            raise ValueError('Invalid JSON data')

        print(f"Received data: {data}")
        username = data['username']
        private_ip = data['private_ip']
        public_ip = data['public_ip']
        mac_address = data['mac_address']

        update_ip_data(username, private_ip, public_ip, mac_address)

        return jsonify({'message': 'IP information updated successfully'}), 200
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_ip_info/<username>', methods=['GET'])
def get_ip_info_route(username):
    try:
        ip_info = get_ip_info(username)
        if ip_info:
            return jsonify(ip_info), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/get_username', methods=['GET'])
def get_username():
    username = get_username_from_database()

    if username:
        return jsonify({'username': username}), 200
    else:
        return jsonify({'error': 'Username not found'}), 404

@app.route('/get_all_systems', methods=['GET'])
def get_all_systems_route():
    try:
        systems_info = get_all_systems()
        if systems_info:
            return jsonify(systems_info), 200
        else:
            return jsonify({'error': 'Failed to retrieve system information'}), 500
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Server ready to handle traffic'}), 200

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000)
