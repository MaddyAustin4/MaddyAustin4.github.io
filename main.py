from pdf2image import convert_from_path


def pdf_to_image(path_to_pdf):
    image = convert_from_path(path_to_pdf, output_folder='.')
    print(image)

if __name__ == "__main__":
    pdf_to_image('EDpatientinfoleaflet.pdf')