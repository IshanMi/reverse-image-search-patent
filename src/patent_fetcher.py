import requests


def get_patent(keyword: str):
    """ Search for a patent by keyword"""
    title_search = f'{{"patent_title":"{keyword}"}}'
    query = f'https://api.patentsview.org/patents/query?q={{"_text_any":{title_search}}}'
    response = requests.get(query)
    print(response.json()['total_patent_count'])
    return


