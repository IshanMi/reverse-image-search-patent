import requests
from werkzeug.utils import secure_filename


def get_patent(keyword: str):
    """ Search for a patent by keyword"""
    title_search = f'{{"patent_title":"{keyword}"}}'
    query = f'https://api.patentsview.org/patents/query?q={{"_text_any":{title_search}}}'
    response = requests.get(query)
    return response.json()


