from pdf2image import convert_from_path
from PIL import Image
# images_from_path = convert_from_path('EDpatientinfoleaflet.pdf', output_folder='output.txt')

im = Image.open("31e06b2b-2fa4-47f3-988d-ae21201b289b-1.ppm")
im.save("sweet_pic.jpg")
