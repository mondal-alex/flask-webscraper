from bs4 import BeautifulSoup
import flask
import re
import requests
import base64
from datetime import datetime, timedelta
import os
from google.cloud import datastore

datastore_client = datastore.Client()

def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)


def fetch_times(limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

class Query:

    def __init__(self, root_link):
        self.root_link = root_link
        self.root_soup = self.__create_soup(self.root_link)
        self.root_request = requests.get(self.root_link)
        self.hp_dict = {"Homework": {"Due Dates": {}, "Specs": {}},
                        "Projects": {"Due Dates": {}, "Specs": {}},
                       "Labs": {"Due Dates": {}, "Specs": {}},
                       "Unknown": {"Due Dates": {}, "Specs": {}}}
        return

    def __create_soup(self, link):
        html = requests.get(link)
        soup = BeautifulSoup(html.content, 'html.parser')
        return soup

    # search all tables for due dates
    def __tables(self):

        tables = pd.read_html(self.root_request.text)

        for table in tables:

            homework_column = None
            projects_column = None
            due_date_column = None

            column_names = table.columns
            num_columns = table.shape[1]

            num_rows = table.shape[0]

            for r in range(num_rows):

                dues = []

                dates = []

                due_dates = {}

                homeworks = {}

                projects = {}

                labs = {}

                print ("*** New Row ***")
                print("Row: " + str(r))
                print ("*** New Row ***")
                print(" ")
                print(" ")

                for c in range(num_columns):

                    cell = str(table.iloc[r, c])
                    print(cell)

                    print(" ")
                    print("Cell: " + str(c))
                    print ("Cell Content: " + cell)

                    # create an empty list of due dates by default
                    due_dates[c] = []

                    # if a due date is explicitly mentioned, grab it
                    due_datess = re.findall(r"[Dd][Uu][Ee]\s*[0-9]+[0-9]*\/[0-9]+[0-9]*", cell)
                    if not due_datess == []:
                        due_dates[c] = due_datess
                        print('Due Dates Found: ')
                        print(due_dates[c])

                    # else if a date is mentioned, grab it and infer it is a due date
                    else:
                        dates = re.findall(r"[0-9]+[0-9]*\/[0-9]+[0-9]*", cell)
                        if not dates == []:
                            due_dates[c] = ['Due ' + date for date in dates]
                            print('Dates Found: ')
                            print(due_dates[c])

                    assignments = re.findall(r"Homework\s*[0-9]+|HOMEWORK\s*[0-9]+|[Hh][Ww]\s*[0-9]+|Project\s*[0-9]+|PROJECT[0-9]\s*[0-9]+|Lab\s*[0-9]+|LAB\s*[0-9]+", cell)
                    print("Found Assignments: ")
                    print(assignments)

                    # for each assignment referenced in the cell:

                    if assignments != []:
                        for index , assignment in enumerate(assignments):

                                # if the assignment(s) have associated due date(s):
                                # ASSUMES THAT THERE IS A 1-1 MAPPING BETWEEN DUE DATES AND ASSIGNMENTS
                                # ^ POSSIBLE FIX LATER
                                if due_dates[c] != []:

                                    # get its due date
                                    due_date = due_dates[c][index]

                                    # get the type of the assignment
                                    assignment_type = ""

                                    if re.findall(r"Homework[0-9]*.*[0-9]*|HOMEWORK[0-9]*.*[0-9]*|[Hh][Ww]\s*[0-9]", assignment) != []:
                                        assignment_type = "Homework"
                                    elif re.findall(r"Project\s*[0-9]+|PROJECT[0-9]\s*[0-9]+", assignment) != []:
                                        assignment_type = "Projects"
                                    else:
                                        assignment_type = "Labs"


                                    self.hp_dict[assignment_type]['Due Dates'][assignment] = due_date


                    # EDGE CASE: Assignment Name in mentioned in the cell, due date is mentioned, but no
                    #descriptors (project, homework, lab). Assume that ONE assignment name and date are the only text in
                    # the cell, seperate and account for it.
#                     elif assignments == [] and due_dates[c] != []:

#                         assignment_link = None
#                         assignment_link_valid = False

#                         print(table.iloc[r, c])

#                         print(table.iloc[r, c].find_all('a'))

#                         try:
#                             assignment_link = table.iloc[r, c].find_all('a')['href']
#                             assignment_link_valid = (not re.findall(r"\.pdf$",href) == []) or (not re.findall(r"\.html$",href) == []) or (not len(re.findall(r"\.",href)) > 1)
#                         except:
#                             pass

#                         # remove date object
#                         cell = re.sub(r'[0-9]+[0-9]*\/[0-9]+[0-9]*', '', cell)

#                         # remove due
#                         cell = re.sub(r'[Dd][Uu][Ee]', '', cell)

#                         # remove day abbrevations
#                         cell = re.sub('[Mm][Oo][Nn]|[Tt][Uu][Ee]|[Ww][Ee][Dd]|[Tt][Hh][Uu]|[Ff][Rr][Ii]|[Ss][Aa][Tt]|[Ss][Uu][Nn]|\s*', '', cell)

#                         # quick fix for 61B...
#                         if (not cell == "") and (not assignment_link == None) and assignment_link_valid:

#                             self.hp_dict["Unknown"]['Due Dates'][cell] = due_dates[c][0]

    # search all textblocks (paragraphs,headers,bodies) for due dates
    def __textblocks(self):
        pass

    # search all links for project specs and due dates
    def __links(self, _class=None, text=False):

        if self.root_link[-1] == "/":
            self.root_link = self.root_link[:-1]
#             print(self.root_link)

        for link in self.root_soup.find_all('a',_class=_class):
            try:
                href = link['href']
            except:
                continue

            link_text = link.text

            due_date = re.findall(r"[Dd][Uu][Ee]\s+[0-9]+[0-9]*\/[0-9]+[0-9]*", link_text)
            abbrev_hw = re.findall(r"[Hh][Ww]\s*[0-9]+", link_text)
            full_hw = re.findall(r"Homework\s*[0-9]+|HOMEWORK\s*[0-9]+", link_text)
            proj = re.findall(r"Project\s*[0-9]+|PROJECT[0-9]\s*[0-9]+", link_text)
            lab = re.findall(r"Lab\s*[0-9]+|LAB\s*[0-9]+", link_text)


            is_due_date = not due_date == []
            is_pdf = not re.findall(r"\.pdf$",href) == []
            is_html = not re.findall(r"\.html$",href) == []
            is_general = not len(re.findall(r"\.",href)) > 1


            if abbrev_hw != []:
                if is_due_date:
                    self.hp_dict['Homework']['Due Dates'][abbrev_hw[0]] = due_date[0]

                if is_pdf or is_html or is_general:
                    try:
                        self.hp_dict['Homework']["Specs"][abbrev_hw[0]]
                    except:
                        self.hp_dict['Homework']["Specs"][abbrev_hw[0]] = self.root_link+"/"+href

            if full_hw != []:

                if is_due_date:
                    self.hp_dict['Homework']['Due Dates'][full_hw[0]] = due_date[0]

                if is_pdf or is_html or is_general:
                    try:
                        self.hp_dict['Homework']["Specs"][full_hw[0]]
                    except:
                        self.hp_dict['Homework']["Specs"][full_hw[0]] = self.root_link+"/"+href

            if proj != []:

                if is_due_date:
                    self.hp_dict['Projects']['Due Dates'][proj[0]] = due_date[0]

                if is_pdf or is_html or is_general:
                    try:
                        self.hp_dict['Projects']["Specs"][proj[0]]
                    except:
                        self.hp_dict['Projects']["Specs"][proj[0]] = self.root_link+"/"+href

            if lab != []:

                if is_due_date:
                    self.hp_dict['Labs']['Due Dates'][lab[0]] = due_date[0]

                if is_pdf or is_html or is_general:
                    try:
                        self.hp_dict['Projects']["Specs"][lab[0]]
                    except:
                        self.hp_dict['Labs']["Specs"][lab[0]] = self.root_link+"/"+href

    def generate_JSON(self):
        self.__tables()
        self.__links()
        return self.hp_dict
