import datetime


class Patent:

    def __init__(self, title: str, authors: list, date: datetime.date, patent_id: str):
        self.title = title
        self.authors = authors
        self.priority_date = date
        self.patent_id = patent_id
        self.images = []

    def get_pdf(self):
        """ Use the second API to grab a PDF of that patent"""
        pass

