import sys
import csv

class CSVLogger:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.console = sys.stdout  
        self.file = open(self.csv_path, 'w', encoding='utf-8', newline='')
        self.writer = csv.writer(self.file)

    def write(self, text):
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                self.writer.writerow([line])
        self.console.write(text)
        self.console.flush()
        self.file.flush()

    def flush(self):
        self.console.flush()
        self.file.flush()

    def close(self):
        self.file.close()
