"""Registro simple de predicciones en CSV.
Cada predicción guarda: timestamp, cliente_id, probabilidad, nivel, factores
"""
from pathlib import Path
import csv
from datetime import datetime

LOG_PATH = Path('predictions_log.csv')


def log_prediction(cliente_id: str, prob: float, nivel: str, factores: list):
    fieldnames = ['timestamp', 'cliente_id', 'probabilidad', 'nivel', 'factores']
    write_header = not LOG_PATH.exists()
    with open(LOG_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.utcnow().isoformat(),
            'cliente_id': cliente_id,
            'probabilidad': float(prob),
            'nivel': nivel,
            'factores': ';'.join(factores or [])
        })
