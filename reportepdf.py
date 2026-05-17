from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

def crear_reporte_pdf(datos, nombre_archivo="reporte.pdf"):
    """
    Crea un reporte PDF a partir de una lista de datos.

    Args:
        datos: Una lista de tuplas, donde cada tupla representa una fila de datos.
        nombre_archivo: El nombre del archivo PDF a guardar.
    """
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, 10.5 * inch, "Reporte de Datos")

    y = 10 * inch
    for fila in datos:
        texto_fila = ", ".join(map(str, fila))
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, y, texto_fila)
        y -= 0.5 * inch

    c.save()
    print(f"Reporte PDF creado: {nombre_archivo}")

if __name__ == "__main__":
    # Datos de ejemplo
    datos_ejemplo = [
        ("Producto A", 10, 25.50),
        ("Producto B", 5, 12.75),
        ("Producto C", 20, 5.20)
    ]
    crear_reporte_pdf(datos_ejemplo)