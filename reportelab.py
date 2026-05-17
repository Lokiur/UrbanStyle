class ReporteLibroPDF(View):
    def tabla(self,pdf,y):
       Story = []
       styles=getSampleStyleSheet()
       styleBH= styles["Normal"]
       styleBH.align= 'CENTER'
       styleBH.fontSize= 10
       Story.append(Paragraph('hoja de ruta', styles["Normal"]))
       Story.append(Paragraph('fecha de recepcion', styles["Normal"]))
       Story.append(Paragraph('Procedencia', styles["Normal"]))
       Story.append(Paragraph('Referencia', styles["Normal"]))
       Story.append(Paragraph('Destino', styles["Normal"]))     

       lista=[]
       for var in corresp.objects.all().order_by('-id')  :
           p=Paragraph(var.procedencia, styles["Normal"])
           r=Paragraph(var.referencia, styles["Normal"])
           f=Paragraph(str(var.fecha_recepcion), styles["Normal"])             
           lista.append(f, p,r)
       lista.reverse()
       detalle_orden= Table([Story] + lista, colWidths=[4 * cm, 5 * cm, 10 * cm])
       Story.append(detalle_orden)
       detalle_orden.setStyle(TableStyle(
       [
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),          
            ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
       ]
      ))
      detalle_orden.wrapOn(pdf, 800, 600)
      detalle_orden.drawOn(pdf, 60,y)
      Story.append(detalle_orden)

def get(self, request, *args, **kwargs): 
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment;filename="ReporteLibro.pdf"'
   buffer = BytesIO()
   pdf = canvas.Canvas(buffer)
   pdf.setPageSize(landscape(letter)) 
   y=400
   self.tabla(pdf,y)
   pdf.showPage()
   pdf.save()
   pdf = buffer.getvalue()
   buffer.close()
   response.write(pdf)
   return response  