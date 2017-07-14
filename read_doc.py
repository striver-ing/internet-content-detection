# -*- coding: utf-8 -*-
'''
Created on 2017-07-11 14:39
---------
@summary:
---------
@author: Boris
'''

from docx import Document
from db.oracledb import OracleDB

oracle = OracleDB()


# dir_docx = 'test.docx'
# document = Document(dir_docx)
# for p in document.paragraphs:
#     print(p.text)


def parser_docx_paragraphs(docx):
    document = Document(dir_docx)
    for p in document.paragraphs:
        print(p.text)

def parse_docx_table(f):
    person = {}

    document = Document(f)
    table = document.tables[0]

    for i in range(109):
        name = table.cell(i, 1).text.strip()
        origation = table.cell(i, 5).text.strip()

        if origation not in person.keys():
            person[origation] = set()

        person[origation].add(name)

        # print (name, origation)

    from pprint import pprint
    pprint(person)

    filename = "persons.txt"
    # with open(filename, mode = 'w', encoding = 'utf-8') as file:
    #     for origation, names in person.items():
    #         print(origation)
    #         print(name)
    #         content = origation + ':\n' + ','.join(names)
    #         file.write(content)
    #         file.write('\n------------------------------------\n')

    sequence = 1
    for origation, names in person.items():
        print(origation)

        sql = 'insert into TAB_IOPM_FIRST_CLUES_CLASSIFY t (t.first_classify_id, t.first_classify, t.zero_id) values (%s, \'%s\', 1)'%(sequence, origation)
        oracle.add(sql)

        for name in names:
            print(name)
            sql = 'insert into TAB_IOPM_CLUES (id, name, Keyword2, First_Classify_Id) values (%s, \'%s\', \'%s\', %s)'%("sequence.nextval", name, name, sequence)
            oracle.add(sql)
        sequence+=1

parse_docx_table('test.docx')