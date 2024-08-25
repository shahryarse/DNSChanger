import tempfile
import subprocess
import logging
import os

class DnsManager:
    def __init__(self, config):
        self.config = config

    def change_dns(self, selected_config):
        try:
            # Backup the current resolv.conf
            self.run_sudo_command(['cp', self.config.config['resolv_conf_path'], f"{self.config.config['resolv_conf_path']}.bak"])

            # Create new content for resolv.conf
            new_content = f"nameserver {selected_config['dns1']}\n"
            if selected_config['dns2']:
                new_content += f"nameserver {selected_config['dns2']}\n"

            # Write new content to resolv.conf
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(new_content)
                temp_file_path = temp_file.name

            self.run_sudo_command(['mv', temp_file_path, self.config.config['resolv_conf_path']])

            logging.info(f"DNS changed to {selected_config['name']}")
            return True
        except Exception as e:
            logging.error(f"Failed to change DNS: {str(e)}")
            return False

    def clear_dns(self):
        try:
            # Backup the current resolv.conf
            self.run_sudo_command(['cp', self.config.config['resolv_conf_path'], f"{self.config.config['resolv_conf_path']}.bak"])

            # Create new content for resolv.conf (empty or with default nameservers)
            new_content = "# DNS entries cleared\n"

            # Write new content to resolv.conf
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(new_content)
                temp_file_path = temp_file.name

            self.run_sudo_command(['mv', temp_file_path, self.config.config['resolv_conf_path']])

            logging.info("DNS cleared")
            return True
        except Exception as e:
            logging.error(f"Failed to clear DNS: {str(e)}")
            return False

    def run_sudo_command(self, command):
        try:
            process = subprocess.Popen(['sudo', '-S'] + command, stdin=subprocess.PIPE, 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       universal_newlines=True)
            stdout, stderr = process.communicate(self.config.sudo_password + '\n')
            if process.returncode != 0:
                raise Exception(f"Command failed: {stderr}")
            return stdout
        except Exception as e:
            logging.error(f"Failed to run sudo command: {str(e)}")
            raise

    def ping(self, host):
        try:
            output = subprocess.check_output(["ping", "-c", "4", "-W", "2", host], universal_newlines=True)
            lines = output.split('\n')
            for line in lines:
                if "avg" in line:
                    return float(line.split('/')[4])
        except:
            return float('inf')
        return float('inf')