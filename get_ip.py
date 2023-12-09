import socket
import requests
import getpass
from getmac import get_mac_address

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return str(e)

def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        ip_address = response.json()['origin']
        return ip_address
    except Exception as e:
        return str(e)

def send_ip_to_server(username, private_ip, public_ip, mac_address):
    server_url = 'http://54.175.50.140:5000/update_ip'
    payload = {
        'username': username,
        'private_ip': private_ip,
        'public_ip': public_ip,
        'mac_address': mac_address  # Include MAC address in the payload
    }

    try:
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print(f"IP information sent successfully for {username}")
        else:
            print(f"Failed to send IP information for {username}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending IP information: {str(e)}")

if __name__ == "__main__":
    username = getpass.getuser()
    private_ip = get_private_ip()
    public_ip = get_public_ip()
    mac_address = get_mac_address()  # Use get_mac_address from getmac library

    print(f"Username: {username}")
    print(f"Private IP: {private_ip}")
    print(f"Public IP: {public_ip}")
    print(f"MAC Address: {mac_address}")

    send_ip_to_server(username, private_ip, public_ip, mac_address)

