import requests
from patent_client import USApplication


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


def download_patents(patent_list: list[USApplication]):
    """ Download all the patent drawings that arose from the search to the downloads/folder"""
    for patent in patent_list:
        for document in patent.documents:
            if "DRAWING" in document:


    pass

