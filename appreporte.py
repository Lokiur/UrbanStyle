from flask import Flask, render_template, Response
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io

app = Flask(__name__)

# Configura Jinja2 para encontrar las plantillas
env = Environment(loader=FileSystemLoader('.')) # Asume que las plantillas están en el mismo directorio

@app.route('/')
def generar_reporte_pdf():
    # 1. Datos dinámicos para tu reporte
    datos_reporte = {
        'fecha': '2025-08-22',
        'datos': [
            {'id': 1, 'nombre': 'Artículo A', 'valor': 100},
            {'id': 2, 'nombre': 'Artículo B', 'valor': 150},
            {'id': 3, 'nombre': 'Artículo C', 'valor': 200}
        ]
    }

    # 2. Carga y renderiza la plantilla HTML
    template = env.get_template('reporte.html')
    html_renderizado = template.render(datos_reporte)

    # 3. Convierte el HTML a PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        io.StringIO(html_renderizado), # Fuente de HTML
        dest=pdf_buffer # Donde escribir el PDF
    )

    # 4. Prepara el PDF para la descarga
    if not pisa_status.err:
        pdf = pdf_buffer.getvalue()
        response = Response(pdf, mimetype='application/pdf')
        response.headers['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        return response
    else:
        return "Error al generar el PDF", 500

if __name__ == '__main__':
    app.run(debug=True)
