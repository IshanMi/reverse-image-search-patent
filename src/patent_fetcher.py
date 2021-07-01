from typing import List
from random import choice

import fitz
import os
from patent_client import USApplication
from PIL import Image
from io import BytesIO
from celery import Celery

from src.flask_celery import make_celery

celery = make_celery()


def conduct_search(title: str, author=False, status=False, expiry=False, lim=100):
    """ Search for a patent using the patent_client module. """
    search_results = USApplication.objects.filter(patent_title=title.upper()).limit(lim)

    if author:
        search_results = search_results.filter(first_named_applicant=author)
    if status:
        search_results = search_results.filter(app_status=status)
    if expiry:
        search_results = search_results.filter()

    return search_results


@celery.task(name="download_patents")
def download_patents(destination: str,
                     patent_list: List[USApplication] = None,
                     patent_title: str = None):
    """ Download all the patent drawings that arose from the search to the downloads/folder"""
    if patent_list is None and patent_title is not None:
        patent_list = conduct_search(patent_title, lim=10)

    if not destination.endswith("/"):
        destination += "/"

    for idx, patent in enumerate(patent_list, start=1):
        for document in patent.documents:
            if "DRAWING" in document.description.upper() and "NOTICE" not in document.description.upper():
                print(f'Downloading images from patent {idx}: {document.description}')
                try:
                    document.download(destination)
                except RuntimeError:
                    print(f'Unable to parse document: {document.description}')
                    continue
    # Return all saved PDF documents, with their relative path
    return [f'{destination}{i}' for i in os.listdir(destination) if i[-4:] == '.pdf']


@celery.task(name="get_sample_images")
def get_sample_images(drawing_files, destination):
    sample_images = []
    for drawing in drawing_files:
        # Remove all blank spaces in the Patent Title Name
        title_name = drawing.split("-")[0]
        # Extract all images from the Patent PDF
        patent_images = extract_images(drawing, destination=destination, title=title_name)
        if patent_images:
            sample_images.append(choice(patent_images))
        else:
            # If no images were extracted, use a stock icon of a patent
            sample_images.append(f"{destination}/patent_image_not_available.png")
    return sample_images


def extract_images(pdf_file, destination: str, title: str):
    """ Extract all the images from the patent (PDF)"""

    try:
        with fitz.open(pdf_file) as f:
            images = []

            # Check if first and last image from this patent are downloaded
            page_start = 0
            page_end = len(f) - 1

            first_img = f'{title.split("/")[-1][:-1]}_{page_start}.png'
            last_img = f'{title.split("/")[-1][:-1]}_{page_end}.png'

            if first_img in os.listdir(f'{destination}/images') and last_img in os.listdir(f'{destination}/images'):
                print("Patent already parsed, skipping.")

                # If they are, just save the image names to the array and move on to the next patent
                for page_index in range(page_end):
                    fname = f'{title.split("/")[-1][:-1]}_{page_index}.png'
                    images.append(f'{destination}/images/{fname}')
            else:
                # Iterate over PDF pages
                for page_index in range(page_end):

                    # get the page itself
                    page = f[page_index]
                    image_list = page.getImageList()

                    print(f'Looking at new page: Page #{page_index}/{len(f)}')
                    for img in image_list:

                        # Iterate over every image on that page
                        xref = img[0]

                        base_image = f.extractImage(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        """ This code isn't being used anymore but it's left here incase it needs to be brought back
                        tags = ["xref", "base_image", "image_bytes", "ext"]
                        new_image = dict(zip(tags, [xref, base_image, image_bytes, image_ext]))
                        """

                        # Prepare image name
                        fname = f'{title.split("/")[-1][:-1]}_{page_index}.{image_ext}'
                        abspath = os.path.join(os.path.abspath(destination), fname)

                        # Because Windows
                        if "\\" in abspath:
                            abspath = abspath.replace("\\", "/")

                        # Save images if not already in directory
                        if fname not in os.listdir(destination):
                            with Image.open(BytesIO(image_bytes)) as im:
                                im.save(abspath)
                        else:
                            print(f'Using cached image: {fname}')

                        images.append(fname)
        return images

    except RuntimeError:
        print(f'Unable to parse file: {pdf_file}')


def display(byte_data):
    """ Convert byte data to a PIL Image object that can be viewed."""
    return Image.open(BytesIO(byte_data))
