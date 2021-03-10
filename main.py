from pdf2image import convert_from_path
from PIL import Image
import os

def pdf_to_jpg():
    convert_from_path('EDpatientinfoleaflet.pdf', output_folder='.', output_file='output')
    names = []
    for image in os.listdir('.'):
        if image.startswith('output'):
            im = Image.open(image)
            image_name = f"{image}.jpg"
            names.append(image_name)
            im.save(image_name)
    return names

def to_index():
    with open("index.html", "a") as myfile:
        for i in pdf_to_jpg():
            str = f"<a href=EDpatientinfoleaflet.pdf class=image fit><img src={i} alt=></a>\n"
            myfile.write(str)


if __name__ == "__main__":
    to_index()
