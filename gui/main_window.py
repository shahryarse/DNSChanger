import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QProgressBar, QTextEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .add_dns_dialog import AddDnsDialog
from config import Config
from dns_manager import DnsManager
from utils.system_utils import get_current_dns, check_network_connection
import logging

class PingWorker(QThread):
    result = pyqtSignal(str, float)
    finished = pyqtSignal()

    def __init__(self, dns_manager, dns_configs):
        super().__init__()
        self.dns_manager = dns_manager
        self.dns_configs = dns_configs

    def run(self):
        for config in self.dns_configs:
            ping_time = self.dns_manager.ping(config['dns1'])
            self.result.emit(config['name'], ping_time)
        self.finished.emit()

class DnsChangerApp(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.dns_manager = DnsManager(self.config)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Buttons
        button_layout = QHBoxLayout()
        self.clearButton = QPushButton('Clear DNS', self)
        self.clearButton.clicked.connect(self.clear_dns)
        button_layout.addWidget(self.clearButton)

        self.changeButton = QPushButton('Change DNS', self)
        self.changeButton.clicked.connect(self.change_dns)
        button_layout.addWidget(self.changeButton)

        self.pingButton = QPushButton('Check Ping', self)
        self.pingButton.clicked.connect(self.check_ping)
        button_layout.addWidget(self.pingButton)

        self.addDnsButton = QPushButton('Add DNS', self)
        self.addDnsButton.clicked.connect(self.add_dns)
        button_layout.addWidget(self.addDnsButton)

        self.removeDnsButton = QPushButton('Remove DNS', self)
        self.removeDnsButton.clicked.connect(self.remove_dns)
        button_layout.addWidget(self.removeDnsButton)

        layout.addLayout(button_layout)

        # DNS selection combo box
        self.comboBox = QComboBox(self)
        self.update_dns_combo_box()
        layout.addWidget(self.comboBox)

        # Status label
        self.statusLabel = QLabel('Ready', self)
        layout.addWidget(self.statusLabel)

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        # Ping results text area
        self.pingResultsText = QTextEdit(self)
        self.pingResultsText.setReadOnly(True)
        layout.addWidget(self.pingResultsText)

        self.setLayout(layout)
        self.setWindowTitle('DNS Changer Utility')
        self.setGeometry(300, 300, 500, 400)
        
        icon_path = self.config.config.get('icon_path')
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        self.show()

    def update_dns_combo_box(self):
        current_text = self.comboBox.currentText()
        self.comboBox.clear()
        self.comboBox.addItems([config['name'] for config in self.config.dns_configs])
        if current_text in [config['name'] for config in self.config.dns_configs]:
            self.comboBox.setCurrentText(current_text)
        self.update_remove_button_state()

    def update_remove_button_state(self):
        current_dns = self.comboBox.currentText()
        is_default = any(config['name'] == current_dns for config in self.config.get_default_dns())
        self.removeDnsButton.setEnabled(not is_default)

    def change_dns(self):
        if not check_network_connection():
            QMessageBox.warning(self, 'No Network', 'No active network connection detected.')
            return

        dns_choice = self.comboBox.currentText()
        selected_config = self.config.get_dns_by_name(dns_choice)

        if not selected_config:
            QMessageBox.critical(self, 'Error', f'DNS configuration for {dns_choice} not found!')
            return

        self.statusLabel.setText('Changing DNS...')
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)  # Indeterminate progress

        success = self.dns_manager.change_dns(selected_config)

        if success:
            self.config.config['last_used_dns'] = dns_choice
            self.config.save_config()
            QMessageBox.information(self, 'Success', f'DNS changed to {dns_choice} successfully!')
        else:
            QMessageBox.critical(self, 'Error', f'Failed to change DNS to {dns_choice}.')

        self.statusLabel.setText('Ready')
        self.progressBar.setVisible(False)

    def clear_dns(self):
        if not check_network_connection():
            QMessageBox.warning(self, 'No Network', 'No active network connection detected.')
            return

        self.statusLabel.setText('Clearing DNS...')
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)  # Indeterminate progress

        success = self.dns_manager.clear_dns()

        if success:
            QMessageBox.information(self, 'Success', 'DNS cleared successfully!')
        else:
            QMessageBox.critical(self, 'Error', 'Failed to clear DNS.')

        self.statusLabel.setText('Ready')
        self.progressBar.setVisible(False)

    def check_ping(self):
        if not check_network_connection():
            QMessageBox.warning(self, 'No Network', 'No active network connection detected.')
            return

        self.statusLabel.setText('Checking ping...')
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, len(self.config.dns_configs))
        self.progressBar.setValue(0)

        self.pingResultsText.clear()
        self.ping_results = []

        self.ping_worker = PingWorker(self.dns_manager, self.config.dns_configs)
        self.ping_worker.result.connect(self.on_ping_result)
        self.ping_worker.finished.connect(self.on_ping_finished)
        self.ping_worker.start()

    def on_ping_result(self, name, ping_time):
        self.ping_results.append((name, ping_time))
        self.ping_results.sort(key=lambda x: x[1])
        self.update_ping_results_display()
        self.progressBar.setValue(self.progressBar.value() + 1)

    def on_ping_finished(self):
        self.statusLabel.setText('Ready')
        self.progressBar.setVisible(False)

    def update_ping_results_display(self):
        self.pingResultsText.clear()
        for name, ping_time in self.ping_results:
            if ping_time == float('inf'):
                status = "Timeout"
                color = "red"
            else:
                status = f"{ping_time:.2f} ms"
                color = "green"
            self.pingResultsText.append(f'<font color="{color}">{name}: {status}</font>')

    def add_dns(self):
        dialog = AddDnsDialog(self)
        if dialog.exec_():
            new_dns = dialog.get_dns_info()
            self.config.add_dns_config(new_dns)
            self.update_dns_combo_box()

    def remove_dns(self):
        dns_choice = self.comboBox.currentText()
        if dns_choice not in [config['name'] for config in self.config.get_default_dns()]:
            reply = QMessageBox.question(self, 'Remove DNS', f"Are you sure you want to remove {dns_choice}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config.remove_dns_config(dns_choice)
                self.update_dns_combo_box()

    def closeEvent(self, event):
        current_dns = get_current_dns()
        if current_dns != self.config.get_default_dns()[0]['dns1']:
            reply = QMessageBox.question(self, 'Exit', 
                                         "The current DNS is not set to the default. Do you want to reset it before exiting?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.dns_manager.change_dns(self.config.get_default_dns()[0])
        event.accept()