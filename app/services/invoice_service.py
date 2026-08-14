"""Genera la factura en PDF con los datos de la tabla `facturas`."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# mismos colores de variables.css, para que el PDF se vea de la tienda
COLOR_FONDO = colors.HexColor("#0f172a")
COLOR_ACENTO = colors.HexColor("#2563eb")
COLOR_SUAVE = colors.HexColor("#f1f5f9")
COLOR_BORDE = colors.HexColor("#cbd5e1")
COLOR_GRIS = colors.HexColor("#64748b")


def _pesos(valor):
    return "$ {:,.0f}".format(valor)


def _estilos():
    base = getSampleStyleSheet()

    return {
        "titulo": ParagraphStyle(
            "titulo",
            parent=base["Title"],
            fontSize=24,
            leading=28,
            textColor=COLOR_FONDO,
            alignment=0,
        ),
        "seccion": ParagraphStyle(
            "seccion",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=COLOR_ACENTO,
            spaceAfter=4,
        ),
        "texto": ParagraphStyle(
            "texto",
            parent=base["Normal"],
            fontSize=9.5,
            leading=14,
            textColor=COLOR_FONDO,
        ),
        "pie": ParagraphStyle(
            "pie",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=COLOR_GRIS,
            alignment=1,
        ),
    }


def _encabezado(factura, estilos):
    """Logo/titulo a la izquierda y numero de factura a la derecha."""
    izquierda = [
        Paragraph("UrbanStyle", estilos["titulo"]),
        Paragraph("Tienda de ropa urbana<br/>NIT 900.123.456-7", estilos["texto"]),
    ]

    derecha = [
        Paragraph("FACTURA DE VENTA", estilos["seccion"]),
        Paragraph(
            "<b>N° {}</b><br/>Fecha: {}<br/>Estado: {}".format(
                factura["numero_factura"] or "-",
                factura["fecha"].strftime("%d/%m/%Y %I:%M %p"),
                factura["estado"].capitalize(),
            ),
            estilos["texto"],
        ),
    ]

    tabla = Table([[izquierda, derecha]], colWidths=[95 * mm, 75 * mm])
    tabla.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return tabla


def _autorizacion(factura, estilos):
    """Recuadro con el numero de autorizacion del pago."""
    contenido = Paragraph(
        "<font size=9 color='#94a3b8'>PAGO APROBADO &nbsp;·&nbsp; "
        "{}</font><br/><font size=17 color='#ffffff'><b>N° de autorización: "
        "{}</b></font>".format(
            factura["metodo_pago"], factura["numero_autorizacion"] or "sin registrar"
        ),
        ParagraphStyle("auth", fontSize=10, leading=22, textColor=colors.white),
    )

    tabla = Table([[contenido]], colWidths=[170 * mm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_FONDO),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    return tabla


def _datos_cliente(factura, estilos):
    """Dos columnas: cliente facturado y direccion de envio."""
    nombre = "{} {}".format(factura["name"], factura["apellidos"]).strip()

    cliente = "{}<br/>{}".format(nombre, factura["email"])
    if factura["documento_identidad"]:
        cliente += "<br/>C.C. {}".format(factura["documento_identidad"])
    if factura["celular"]:
        cliente += "<br/>Tel. {}".format(factura["celular"])

    envio = "{}<br/>{}".format(factura["direccion"], factura["ciudad"] or "")
    if factura["departamento"]:
        envio += ", {}".format(factura["departamento"])
    if factura["codigo_postal"]:
        envio += "<br/>C.P. {}".format(factura["codigo_postal"])

    tabla = Table(
        [
            [
                Paragraph("FACTURAR A", estilos["seccion"]),
                Paragraph("ENVIAR A", estilos["seccion"]),
            ],
            [
                Paragraph(cliente, estilos["texto"]),
                Paragraph(envio, estilos["texto"]),
            ],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    tabla.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )
    return tabla


def _detalle(factura, estilos):
    """Tabla de productos comprados."""
    filas = [["Producto", "Talla / Color", "Cant.", "Precio unit.", "Subtotal"]]

    for item in factura["items"]:
        filas.append(
            [
                Paragraph(
                    "{}<br/><font size=7.5 color='#64748b'>{}</font>".format(
                        item["producto_nombre"], item["sku"] or item["referencia"] or ""
                    ),
                    estilos["texto"],
                ),
                "{} / {}".format(item["talla"], item["color"]),
                str(item["cantidad"]),
                _pesos(item["precio_unitario"]),
                _pesos(item["subtotal"]),
            ]
        )

    tabla = Table(
        filas,
        colWidths=[68 * mm, 34 * mm, 15 * mm, 26 * mm, 27 * mm],
        repeatRows=1,
    )
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_FONDO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (1, 1), (-1, -1), "Helvetica"),
                ("TEXTCOLOR", (1, 1), (-1, -1), COLOR_FONDO),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_SUAVE]),
                ("LINEBELOW", (0, 1), (-1, -1), 0.4, COLOR_BORDE),
            ]
        )
    )
    return tabla


def _totales(factura, estilos):
    """Subtotal / IVA / envio / total, alineados a la derecha."""
    filas = [
        ["Subtotal", _pesos(factura["subtotal"])],
        ["IVA (19%)", _pesos(factura["iva"])],
        ["Envío", _pesos(factura["envio"])],
        ["TOTAL PAGADO", _pesos(factura["total"])],
    ]

    interna = Table(filas, colWidths=[45 * mm, 35 * mm])
    interna.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -2), 9.5),
                ("TEXTCOLOR", (0, 0), (-1, -2), COLOR_GRIS),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEABOVE", (0, -1), (-1, -1), 0.8, COLOR_FONDO),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("TEXTCOLOR", (0, -1), (-1, -1), COLOR_FONDO),
                ("TOPPADDING", (0, -1), (-1, -1), 8),
            ]
        )
    )

    contenedor = Table([["", interna]], colWidths=[90 * mm, 80 * mm])
    contenedor.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return contenedor


def generar_pdf(factura):
    """Arma la factura en PDF y devuelve los bytes listos para descargar."""
    buffer = BytesIO()
    estilos = _estilos()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Factura {}".format(factura["numero_factura"] or factura["id"]),
        author="UrbanStyle",
    )

    doc.build(
        [
            _encabezado(factura, estilos),
            Spacer(1, 10 * mm),
            _autorizacion(factura, estilos),
            Spacer(1, 8 * mm),
            _datos_cliente(factura, estilos),
            Spacer(1, 8 * mm),
            _detalle(factura, estilos),
            Spacer(1, 6 * mm),
            _totales(factura, estilos),
            Spacer(1, 12 * mm),
            Paragraph(
                "Gracias por comprar en UrbanStyle. Conserva esta factura como "
                "soporte de tu compra.<br/>Este documento fue generado "
                "electrónicamente y no requiere firma.",
                estilos["pie"],
            ),
        ]
    )

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
