from bs4 import BeautifulSoup
import flask
import re
import requests
import base64
from datetime import datetime, timedelta
import os

class Query:

    def __init__(self, root_link):
        self.root_link = root_link
        self.root_soup = self.__create_soup(self.root_link)
        return

    def __create_soup(self, link):
        html = requests.get(link)
        soup = BeautifulSoup(html.content, 'html.parser')
        return soup

    def __findall_type(self, link_regex, link_tag):

        if not (re.findall(link_regex, link_tag["href"]) == []):
            return link_tag

    def __findall_html(self, link_tag):
        return self.__findall_type(r".pdf$", link_tag)

    def __findall_pdf(self, link_tag):
        return self.__findall_type(r".html$", link_tag)


    # to be implemented by Angela
    def __due_dates(self):
        return

    def __specs(self, _class=None, text=False):

        specs = {"Homework": {}, "Projects": {}}

        for link1 in self.root_soup.find_all('a',_class=_class):

            # for hwx, Hwx, hWx, HWx, where x in an integer 0-9
            abbrev_hw = False in [re.findall(r"^[Hh][Ww][0-9]*.*$", chars) == [] for chars in link1.text.split()]

            # for Homeworkx, HOMEWORKx, where x is an integer 0-9
            full_hw = False in [re.findall(r"Homework[0-9]*.* | HOMEWORK[0-9]*.*", chars) == [] for chars in link1.text.split()]

            # for Project[x], where x in an integer 0-9
            proj = False in [re.findall(r"Project[0-9]*.*", chars) == [] for chars in link1.text.split()]

            is_pdf = not self.__findall_pdf(link1) == []
            is_html = not self.__findall_html(link1) == []

            if abbrev_hw or full_hw:
                if is_pdf or is_html:
                    specs['Homework'][link1.text] = self.root_link+"/"+link1['href']

            if proj:
                if is_pdf or is_html:
                    specs['Projects'][link1.text] = self.root_link+"/"+link1['href']

        return specs

    def generate_dict(self):

        due_dates = self.__due_dates()
        specs = self.__specs()

        return {self.root_link: specs}
