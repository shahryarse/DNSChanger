from PyQt5.QtWidgets import QInputDialog, QLineEdit
import subprocess
import logging

def get_sudo_password():
    """
    Prompt the user for their sudo password using a GUI dialog.
    
    Returns:
        str: The entered password, or None if the user cancels.
    """
    password, ok = QInputDialog.getText(None, 'Sudo Password', 'Enter your sudo password:', QLineEdit.Password)
    if ok:
        return password
    return None

def validate_sudo_password(password):
    """
    Validate the provided sudo password.
    
    Args:
        password (str): The sudo password to validate.
    
    Returns:
        bool: True if the password is valid, False otherwise.
    """
    try:
        process = subprocess.Popen(
            ['sudo', '-S', 'echo', 'Password is valid'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate(password + '\n')
        return process.returncode == 0
    except Exception as e:
        logging.error(f"Error validating sudo password: {str(e)}")
        return False

def check_network_connection():
    """
    Check if there's an active network connection.
    
    Returns:
        bool: True if there's an active connection, False otherwise.
    """
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'])
        return True
    except subprocess.CalledProcessError:
        return False

def get_current_dns():
    """
    Get the current DNS server(s) from the system configuration.
    
    Returns:
        list: A list of current DNS server IP addresses.
    """
    try:
        with open('/etc/resolv.conf', 'r') as f:
            lines = f.readlines()
        
        dns_servers = []
        for line in lines:
            if line.startswith('nameserver'):
                dns_servers.append(line.split()[1])
        
        return dns_servers
    except Exception as e:
        logging.error(f"Error getting current DNS: {str(e)}")
        return []

def is_valid_ip(ip):
    """
    Check if the given string is a valid IP address.
    
    Args:
        ip (str): The IP address to validate.
    
    Returns:
        bool: True if the IP is valid, False otherwise.
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True