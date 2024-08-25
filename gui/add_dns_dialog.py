from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
import ipaddress

class AddDnsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom DNS")
        layout = QFormLayout()
        self.name_input = QLineEdit()
        self.dns1_input = QLineEdit()
        self.dns2_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        layout.addRow("Primary DNS:", self.dns1_input)
        layout.addRow("Secondary DNS:", self.dns2_input)
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        name = self.name_input.text()
        dns1 = self.dns1_input.text()
        dns2 = self.dns2_input.text()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Name cannot be empty.")
            return

        if not self.is_valid_ip(dns1):
            QMessageBox.warning(self, "Validation Error", "Invalid Primary DNS IP address.")
            return

        if dns2 and not self.is_valid_ip(dns2):
            QMessageBox.warning(self, "Validation Error", "Invalid Secondary DNS IP address.")
            return

        self.accept()

    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def get_dns_info(self):
        return {
            "name": self.name_input.text(),
            "dns1": self.dns1_input.text(),
            "dns2": self.dns2_input.text()
        }