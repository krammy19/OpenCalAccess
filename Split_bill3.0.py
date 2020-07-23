#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      m_noa_000
#
# Created:     13/08/2019
# Copyright:   (c) m_noa_000 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re
import sqlite3
# bunch of dummy bill lists to test split_bill
bills1 = 'AB 2120 AB 300 AB 506 SB 1 SB 200 SB 650 Department of Motor Vehicles'
bills2 = 'SB 2500 600 AB 350 AB 620 SB 300'
bills3 = "Gov. Jerry Brown meetings with legislators AB 750 43 SB 650"

def split_bill(billpackage):
    AB = False
    SB = False
    print("0:", billpackage)
    legislature_bills = []
    other_words = []
    list = re.findall('[AaSsBb]{0,2}[Ss]?\W?\s?\d{1,4}', billpackage)

# ------ this is for later when ready to add other text
#    other_words = (re.sub('[AaSsBb]{0,2}[Ss]?\W?\s?\d{1,4}',"", billpackage))
#    words = re.sub('^\W*',"", ("".join(other_words)))
#--------
    for item in list:
        item = (re.sub('\W',"", item)).strip()
        if item.startswith(('AB', 'Ab', 'ab')):
            AB = True
            SB = False
            item = (re.sub('\D',"",item)).strip()
            item = "AB " + item
            legislature_bills.append(item)
        elif item.startswith(('SB', 'Sb', 'sb')):
            SB = True
            AB = False
            item = (re.sub('\D',"",item)).strip()
            item = "SB " + item
            legislature_bills.append(item)
        elif item.isdigit():
            if AB: legislature_bills.append("AB " + item)
            if SB: legislature_bills.append("SB " + item)
    return legislature_bills #,words
# ------------------------------

def leg_year(date):

    if int(date) % 2 == 0:
        date = str(int(date)-1) + "-" + date
    else:
        date = date + "-" + str(int(date)+1)
    return(date)



# need to change name later
conn = sqlite3.connect('lobbying2.db')
cur1 = conn.cursor()
cur2 = conn.cursor()

cur2.execute('''DROP TABLE IF EXISTS Bills''')
#cur2.execute('''DROP TABLE IF EXISTS Other_Text''')

cur2.execute('''CREATE TABLE IF NOT EXISTS Bills (
id INTEGER PRIMARY KEY AUTOINCREMENT,
Bill TEXT,
Year TEXT,
UNIQUE (Bill, Year))
''')

#----- THIS IS FOR LATER WHEN OTHER_TEXT IS READY
#cur2.execute('''CREATE TABLE IF NOT EXISTS Other_Text (
#id INTEGER PRIMARY KEY AUTOINCREMENT,
#Other_Text TEXT,
#Year TEXT,
#Filing_id INTEGER) ''' )

conn.commit()
#amended SELECT TO INCLUDE Text_memo, Legislation.Form_ID
i = 0
for row in cur1.execute('''SELECT LPAY.legislation, CVR_LOBBY_DISCLOSURE.Report_Date, TEXT_MEMO_LOBBYING.Text4000
FROM LPAY
JOIN CVR_LOBBY_DISCLOSURE on LPAY.Filing_ID = CVR_LOBBY_DISCLOSURE.Filing_id
LEFT OUTER JOIN TEXT_MEMO_LOBBYING on CVR_LOBBY_DISCLOSURE.Filing_id = TEXT_MEMO_LOBBYING.Filing_id;'''):
#    print(row)
#----- EDITED TO TAKE OUT WORDS / OTHER_WORDS FOR OTHER_TEXT TABLE -----
#    list, words = split_bill(row[0])
    try:
        list = split_bill(row[0])
        year = leg_year(row[1])
        if row[2] is not None:
#        other_text, other_words = split_bill(row[2])
            other_text = split_bill(row[2])
            list.extend(other_text)
    except:
        continue
#        words = (words + other_words)
    print("Trying to add:", list)
    for bill in list:
        try:
            cur2.execute('''INSERT INTO Bills
        (Bill, Year) VALUES (?, ?)''', (bill, year ))
            print('IM ADDING ' + bill, year)
        except:
            continue
    if i > 50:
        conn.commit()
conn.commit()
#----- THIS IS FOR LATER WHEN OTHER_TEXT IS READY
#    cur2.execute('''INSERT INTO Other_text
#    (other_text, year) VALUES (?, ? )''',
#    (words, year,) )
conn.close()



