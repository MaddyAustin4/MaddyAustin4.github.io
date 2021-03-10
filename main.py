from pdf2image import convert_from_path
from PIL import Image
import pyqrcode
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
    os.system('rm -f index.html')
    with open("index.html", "a") as myfile:
        for i in pdf_to_jpg():
            str = f'<img src="{i}" width="145" height="126" alt="Planets"usemap="#planetmap">\n'
            myfile.write(str)


def create_qr_code():
    url = pyqrcode.create('https://maddyaustin4.github.io/')
    url.png('./new.png')


if __name__ == "__main__":
    for image in os.listdir('.'):
        if image.startswith('output'):
            os.remove(image)
    to_index()
    os.system('git add .')
    os.system('git commit -m automated')
    os.system('git push')
    create_qr_code()
