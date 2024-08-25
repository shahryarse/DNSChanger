import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui import DnsChangerApp
from config import Config
from utils import get_sudo_password

def setup_logging():
    config = Config()
    logging.basicConfig(
        filename=config.config['log_file'],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def run_app():
    app = QApplication(sys.argv)
    
    setup_logging()
    
    sudo_password = get_sudo_password()
    if not sudo_password:
        logging.error("No sudo password provided. Exiting.")
        sys.exit(1)
    
    config = Config()
    config.sudo_password = sudo_password
    
    ex = DnsChangerApp(config)
    ex.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()