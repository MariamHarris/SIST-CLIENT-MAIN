from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import os

def generar_reporte_semanal(context, output_path=None):
    html = render_to_string('dashboard/report_template.html', context)
    output_path = output_path or os.path.join(settings.BASE_DIR, 'reports', 'reporte_semanal.pdf')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    HTML(string=html).write_pdf(target=output_path)
    return output_path
