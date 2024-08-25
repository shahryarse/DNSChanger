import yaml
import os
import json
import logging

class Config:
    def __init__(self):
        self.config = self.load_config()
        self.dns_configs = self.load_dns_configs()
        self.sudo_password = None

    def load_config(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {
                'dns_config_file': os.path.join(os.path.dirname(__file__) + 'dns_config.json'),
                'resolv_conf_path': '/etc/resolv.conf',
                'log_file': os.path.join(os.path.dirname(__file__) + 'dns_changer.log'),
                'icon_path': os.path.join(os.path.dirname(__file__) + 'app_icon.png')
            }

    def load_dns_configs(self):
        try:
            with open(self.config['dns_config_file'], 'r') as f:
                data = json.load(f)
                return data.get('default_dns', []) + data.get('user_dns', [])
        except Exception as e:
            logging.error(f"Failed to load DNS configurations: {str(e)}")
            return []

    def save_dns_configs(self, dns_configs):
        try:
            with open(self.config['dns_config_file'], 'r') as f:
                data = json.load(f)
            data['user_dns'] = [config for config in dns_configs if config not in data.get('default_dns', [])]
            with open(self.config['dns_config_file'], 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save DNS configurations: {str(e)}")

    def save_config(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
                yaml.dump(self.config, f)
        except Exception as e:
            logging.error(f"Failed to save config: {str(e)}")

    def get_default_dns(self):
        try:
            with open(self.config['dns_config_file'], 'r') as f:
                data = json.load(f)
                return data.get('default_dns', [])
        except Exception as e:
            logging.error(f"Failed to load default DNS configurations: {str(e)}")
            return []

    def add_dns_config(self, new_dns):
        self.dns_configs.append(new_dns)
        self.save_dns_configs(self.dns_configs)

    def remove_dns_config(self, dns_name):
        self.dns_configs = [config for config in self.dns_configs if config['name'] != dns_name]
        self.save_dns_configs(self.dns_configs)

    def get_dns_by_name(self, name):
        return next((config for config in self.dns_configs if config['name'] == name), None)