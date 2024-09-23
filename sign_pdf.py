import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image, ImageTk
import fitz  # PyMuPDF para convertir PDF a imagen

# Función para abrir el PDF y convertir la primera página en imagen
def abrir_pdf():
    global img
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        doc = fitz.open(pdf_path)
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((600, 800), Image.ANTIALIAS)  # Ajustar tamaño de la imagen
        img_tk = ImageTk.PhotoImage(img)
        canvas_pdf.create_image(0, 0, anchor="nw", image=img_tk)
        canvas_pdf.image = img_tk
        boton_firma.config(state=tk.NORMAL)
        doc.close()

# Función que se ejecuta al hacer clic para obtener las coordenadas de la firma
def obtener_posicion(event):
    global pos_x, pos_y
    pos_x = event.x
    pos_y = event.y
    colocar_firma()

# Función para colocar la firma en la posición seleccionada
def colocar_firma():
    global pos_x, pos_y
    firma_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
    if firma_path:
        # Ajustar posición y tamaño de la firma
        agregar_firma(ruta_pdf, firma_path, "documento_firmado.pdf", pos_x, pos_y)

# Función para agregar la firma al PDF
def agregar_firma(pdf_path, firma_path, output_path, pos_x, pos_y):
    lector_pdf = PdfReader(pdf_path)
    escritor_pdf = PdfWriter()

    # Cargar la imagen de la firma
    firma_img = Image.open(firma_path)
    ancho_firma, alto_firma = firma_img.size

    # Crear un PDF con la firma en la posición seleccionada
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawImage(firma_path, pos_x, pos_y, width=ancho_firma/4, height=alto_firma/4)
    can.save()

    # Añadir la página firmada al PDF original
    packet.seek(0)
    firma_pdf = PdfReader(packet)
    
    for pagina in range(len(lector_pdf.pages)):
        pagina_pdf = lector_pdf.pages[pagina]
        firma_pdf_page = firma_pdf.pages[0]
        pagina_pdf.merge_page(firma_pdf_page)
        escritor_pdf.add_page(pagina_pdf)

    with open(output_path, "wb") as archivo_salida:
        escritor_pdf.write(archivo_salida)

    print("Firma añadida con éxito en", output_path)

# Interfaz gráfica con tkinter
ventana = tk.Tk()
ventana.title("Insertar firma en PDF")
ventana.geometry("600x800")

canvas_pdf = tk.Canvas(ventana, width=600, height=800)
canvas_pdf.pack()

boton_cargar = tk.Button(ventana, text="Abrir PDF", command=abrir_pdf)
boton_cargar.pack()

boton_firma = tk.Button(ventana, text="Seleccionar posición de firma", state=tk.DISABLED)
boton_firma.pack()

canvas_pdf.bind("<Button-1>", obtener_posicion)

ventana.mainloop()
