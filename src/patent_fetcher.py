from typing import List

import requests
import fitz
import os
from patent_client import USApplication
from PIL import Image
from io import BytesIO


def get_patent(keyword: str):
    """ Previous/old API"""
    title_search = f'{{"patent_title":"{keyword}"}}'
    query = f'https://api.patentsview.org/patents/query?q={{"_text_any":{title_search}}}'
    response = requests.get(query)
    print(response.json()['total_patent_count'])
    return


def conduct_search(title: str, limit=100):
    """ Search for a patent using the patent_client module. """
    print(title)
    search_results = USApplication.objects.filter(patent_title=title.upper())
    print(len(search_results))
    if len(search_results) > limit:
        search_results = search_results[:limit]

    return search_results


def download_patents(patent_list: List[USApplication]):
    """ Download all the patent drawings that arose from the search to the downloads/folder"""

    for patent in patent_list:
        for document in patent.documents:
            if "DRAWING" in document.description.upper() and "NOTICE" not in document.description.upper():
                print(f'Downloading - {document.description}')
                print(os.getcwd())
                print(os.listdir())
                try:
                    document.download("./src/downloads/")
                except RuntimeError:
                    print(f'Unable to parse document: {document.description}')
                    continue

    return os.listdir('./src/downloads')


def extract_images(pdf_file):
    """ Extract all the images from the patent (PDF)"""
    try:
        f = fitz.open(pdf_file)
    except RuntimeError:
        print(f'Unable to parse file: {pdf_file}')
        return
    images = []

    # Iterate over PDF pages
    for page_index in range(len(f)):

        # get the page itself
        page = f[page_index]
        image_list = page.getImageList()

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]

            base_image = f.extractImage(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            tags = ["xref", "base_image", "image_bytes", "ext"]
            new_image = dict(zip(tags, [xref, base_image, image_bytes, image_ext]))
            images.append(new_image)
    return images


def display(byte_data):
    """ Convert byte data to a PIL Image object that can be viewed."""
    return Image.open(BytesIO(byte_data))
