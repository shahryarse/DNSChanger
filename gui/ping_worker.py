from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class PingWorker(QThread):
    result = pyqtSignal(str, float)
    finished = pyqtSignal()

    def __init__(self, dns_configs):
        super().__init__()
        self.dns_configs = dns_configs

    def run(self):
        for config in self.dns_configs:
            ping_time = self.ping(config['dns1'])
            self.result.emit(config['name'], ping_time)
        self.finished.emit()

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