import fitz #Pymupdf


TARGET_DPI = 200 #200 dots per inch 
MAX_PAGES = 15

#Convert given pdf pages into png (a png has pixels/dots per inch) (bytes)
def _render_pdf_pages_to_images(pdf_bytes: bytes) -> list[bytes]:  
    doc = fitz.open(stream=pdf_bytes, filetype="pdf") #Pdf_bytes directly went into the fitz.open from Upload Pdf Button
    zoom = TARGET_DPI / 72 #Caculate the scaling factor
    matrix = fitz.Matrix(zoom, zoom) # scales the image from height and width

    images = []
    for page in doc:
        if len(images) >= MAX_PAGES:
            break
        pix = page.get_pixmap(matrix=matrix) #Coverts into png
        images.append(pix.tobytes("png"))
    doc.close()
    return images #List Of Bytes

