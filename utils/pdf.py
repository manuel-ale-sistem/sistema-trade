import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para calcular con precisión el total de páginas 
    e imprimir un pie de página corporativo en todas las hojas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor('#718096'))
        
        # Línea separadora sutil del pie de página
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.75)
        self.line(36, 40, letter[0] - 36, 40)
        
        # Texto izquierdo: Sistema y Fecha de Emisión
        fecha_actual = datetime.now().strftime("%d/%m/%Y a las %H:%M hrs")
        self.drawString(36, 26, f"SISTEMA TRADE — Documento Oficial Generado el {fecha_actual}")
        
        # Texto derecho: Paginación dinámica (Página X de Y)
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(letter[0] - 36, 26, page_text)
        
        self.restoreState()


def generar_pdf_solicitud(data):
    """
    Genera el comprobante oficial en PDF con un diseño ejecutivo moderno,
    limpio y perfectamente estructurado.
    """
    buffer = io.BytesIO()
    
    # Márgenes profesionales de 36 puntos (0.5 pulgadas)
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=36, 
        leftMargin=36,
        topMargin=36, 
        bottomMargin=55
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Paleta de Colores de Alta Gama (Estilo Corporativo Moderno)
    COLOR_PRIMARY = colors.HexColor('#1A365D')    # Azul Marino Profundo
    COLOR_SECONDARY = colors.HexColor('#2B6CB0')  # Azul Acero / Acento
    COLOR_DARK_TEXT = colors.HexColor('#2D3748')  # Gris Carbón (Texto principal)
    COLOR_MUTED_TEXT = colors.HexColor('#4A5568') # Gris Medio
    COLOR_BG_LIGHT = colors.HexColor('#F7FAFC')   # Fondo Ultra Claro (Celdas)
    COLOR_BORDER = colors.HexColor('#CBD5E0')     # Gris Borde Suave
    
    # Estilos Tipográficos Avanzados
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=12,
        leading=16,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#E2E8F0'),
        fontName='Helvetica'
    )
    
    box_header_style = ParagraphStyle(
        'BoxHeader',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    sub_title_style = ParagraphStyle(
        'SubSecTitle',
        parent=styles['Heading3'],
        fontSize=8.5,
        leading=12,
        textColor=COLOR_SECONDARY,
        fontName='Helvetica-Bold',
        spaceAfter=2,
        spaceBefore=4,
        keepWithNext=True
    )
    
    label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=COLOR_PRIMARY,
        fontName='Helvetica-Bold'
    )
    
    value_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=COLOR_DARK_TEXT,
        fontName='Helvetica'
    )
    
    section_title_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=9.5,
        leading=13,
        textColor=COLOR_PRIMARY,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        spaceBefore=8,
        keepWithNext=True
    )

    # 1. ENCABEZADO / BANNER PRINCIPAL
    folio_val = str(data.get('folio', data.get('id', 'N/A')))
    banner_data = [
        [
            Paragraph("SISTEMA TRADE — COMPROBANTE DE GESTIÓN", title_style),
            Paragraph(f"<b>FOLIO REF:</b> #{folio_val}", ParagraphStyle('FolioTop', parent=subtitle_style, alignment=2))
        ]
    ]
    banner_table = Table(banner_data, colWidths=[370, 170])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 6))

    # 2. DATOS DEL CLIENTE Y OPERATIVOS (Diseño Moderno en Dos Columnas)
    elements.append(Paragraph("INFORMACIÓN GENERAL", section_title_style))
    
    col_cliente = [
        [Paragraph("DATOS DEL CLIENTE", box_header_style), Paragraph("", box_header_style)],
        [Paragraph("SAP", label_style), Paragraph(str(data.get('sap', '')), value_style)],
        [Paragraph("Negocio", label_style), Paragraph(str(data.get('negocio', '')), value_style)],
        [Paragraph("Teléfono", label_style), Paragraph(str(data.get('telefono', '')), value_style)],
        [Paragraph("Segmento", label_style), Paragraph(str(data.get('segmento', '')), value_style)],
        [Paragraph("GEC", label_style), Paragraph(str(data.get('gec', '')), value_style)],
    ]
    
    col_operativo = [
        [Paragraph("DATOS OPERATIVOS", box_header_style), Paragraph("", box_header_style)],
        [Paragraph("Canal", label_style), Paragraph(str(data.get('canal', '')), value_style)],
        [Paragraph("Jefatura", label_style), Paragraph(str(data.get('jefatura', '')), value_style)],
        [Paragraph("Ruta", label_style), Paragraph(str(data.get('ruta', '')), value_style)],
        [Paragraph("Asesor", label_style), Paragraph(str(data.get('asesor', '')), value_style)],
        [Paragraph("PPA", label_style), Paragraph(str(data.get('ppa', '')), value_style)],
    ]

    tabla_col_cliente = Table(col_cliente, colWidths=[70, 190])
    tabla_col_operativo = Table(col_operativo, colWidths=[70, 190])
    
    estilo_cajas = TableStyle([
        ('SPAN', (0, 0), (1, 0)), # Une la cabecera de la caja
        ('BACKGROUND', (0, 0), (1, 0), COLOR_SECONDARY),
        ('BACKGROUND', (0, 1), (0, -1), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    tabla_col_cliente.setStyle(estilo_cajas)
    tabla_col_operativo.setStyle(estilo_cajas)

    doble_columna = Table([[tabla_col_cliente, tabla_col_operativo]], colWidths=[270, 270])
    doble_columna.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(doble_columna)
    elements.append(Spacer(1, 6))

    # 3. UBICACIÓN
    elements.append(Paragraph("UBICACIÓN Y GEOREFERENCIACIÓN", section_title_style))
    maps_url = str(data.get("url_maps", ""))
    ubicacion = [
        [Paragraph("Coordenadas", label_style), Paragraph(f"Lat: {data.get('latitud', 'N/A')} | Long: {data.get('longitud', 'N/A')}", value_style)],
        [Paragraph("Google Maps", label_style), Paragraph(f'<a href="{maps_url}" color="#2B6CB0"><u>{maps_url}</u></a>' if maps_url else "N/A", value_style)]
    ]
    tabla_ubicacion = Table(ubicacion, colWidths=[90, 450])
    tabla_ubicacion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tabla_ubicacion)
    elements.append(Spacer(1, 6))

    # 4. RESUMEN EJECUTIVO Y TABLA DE REQUERIMIENTOS
    detalle = data.get("detalle_requerimientos", [])
    elements.append(Paragraph("RESUMEN DE REQUERIMIENTOS", section_title_style))
    elements.append(Paragraph(f"<b>Total de requerimientos registrados:</b> {len(detalle)}", value_style))
    elements.append(Spacer(1, 4))

    if detalle:
        th_style = ParagraphStyle(
            'THStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        tabla_req = [[
            Paragraph("#", th_style),
            Paragraph("Categoría", th_style),
            Paragraph("Solicitud", th_style),
            Paragraph("Modelo", th_style),
            Paragraph("Cantidad", th_style)
        ]]

        for i, item in enumerate(detalle, start=1):
            tabla_req.append([
                Paragraph(str(i), value_style),
                Paragraph(str(item.get("categoria", "")), value_style),
                Paragraph(str(item.get("tipo_solicitud", "")), value_style),
                Paragraph(str(item.get("modelo", "")), value_style),
                Paragraph(str(item.get("cantidad", "")), value_style)
            ])

        t_reqs = Table(tabla_req, colWidths=[25, 95, 260, 100, 60])
        t_reqs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_SECONDARY),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_SECONDARY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_reqs)
        elements.append(Spacer(1, 6))

        # 5. DETALLE EXTENDIDO DE REQUERIMIENTOS
        elements.append(Paragraph("DETALLE ESPECÍFICO DE REQUERIMIENTOS", section_title_style))
        for i, item in enumerate(detalle, 1):
            req_elementos = [Paragraph(f"REQUERIMIENTO #{i}", sub_title_style)]

            campos = [
                ("Categoría", item.get("categoria", "")),
                ("Solicitud", item.get("tipo_solicitud", "")),
                ("Modelo", item.get("modelo", "")),
                ("Cantidad", item.get("cantidad", "")),
                ("Serie", item.get("serie", "")),
                ("Reporte", item.get("reporte", "")),
                ("Material", item.get("material", "")),
                ("Capacidad Actual", item.get("capacidad_actual", "")),
                ("Capacidad Solicitada", item.get("capacidad_solicitada", "")),
                ("Comentarios", item.get("comentarios", ""))
            ]

            for etiqueta, valor in campos:
                if valor not in ["", None, "None"]:
                    req_elementos.append(Paragraph(f"<b>{etiqueta}:</b> {valor}", value_style))

            req_elementos.append(Spacer(1, 3))
            elements.append(KeepTogether(req_elementos))

    # 6. OBSERVACIONES GENERALES
    elements.append(Paragraph("OBSERVACIONES GENERALES", section_title_style))
    obs_data = [[Paragraph(str(data.get("observaciones", "Sin observaciones.")), value_style)]]
    tabla_obs = Table(obs_data, colWidths=[540])
    tabla_obs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(tabla_obs)
    elements.append(Spacer(1, 6))

    # 7. GESTIÓN
    elements.append(Paragraph("ESTATUS Y GESTIÓN", section_title_style))
    gestion = [
        [Paragraph("Estatus", label_style), Paragraph(str(data.get("estatus", "")), value_style)],
        [Paragraph("Resultado", label_style), Paragraph(str(data.get("resultado", "")), value_style)],
        [Paragraph("Responsable", label_style), Paragraph(str(data.get("usuario_gestiona", "")), value_style)],
        [Paragraph("Fecha Cierre", label_style), Paragraph(str(data.get("fecha_cierre", "")), value_style)],
        [Paragraph("Comentarios", label_style), Paragraph(str(data.get("comentarios_admin", "")), value_style)]
    ]
    tabla_gestion = Table(gestion, colWidths=[90, 450])
    tabla_gestion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tabla_gestion)

    # 8. FIRMAS PROFESIONALES
    estilo_firma_linea = ParagraphStyle(
        'FirmaLinea',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=COLOR_MUTED_TEXT,
        fontName='Helvetica-Bold'
    )

    firmas_table = Table(
        [
            [
                Paragraph("_______________________", estilo_firma_linea),
                Paragraph("_______________________", estilo_firma_linea),
                Paragraph("_______________________", estilo_firma_linea)
            ],
            [
                Paragraph("Asesor", estilo_firma_linea),
                Paragraph("Responsable Trade", estilo_firma_linea),
                Paragraph("Supervisor", estilo_firma_linea)
            ]
        ],
        colWidths=[180, 180, 180]
    )
    firmas_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    bloque_firmas = [
        Spacer(1, 20),
        firmas_table
    ]
    elements.append(KeepTogether(bloque_firmas))

    # Construcción final del documento
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    buffer.seek(0)
    return buffer.getvalue()