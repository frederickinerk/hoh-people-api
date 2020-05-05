#
# people tests
# 

import logging
import json
import datetime
import csv

import peeps
import mycontext
import hohPeopleApi


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.info('peepTests: initialisation starting...')



# Test with a subject
def test1_0():
    print("Test1_0 - level 0 peeps")

    context = mycontext.newContext()

    #context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')

    items = peeps.getBirthdayList(context, "0", "365", "365", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)

    return

def test1_1():
    context = None

    print("Test1_1 - level 1 peeps")

    #print("context (before) = " + str(context))
    #context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "True", "345", "364", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_2():
    context = None

    print("Test1_2 - level 2 peeps")

    #print("context (before) = " + str(context))
    #context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "2", "200", "200", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_3():
    context = None

    print("Test1_3 - level 3 peeps")

    #print("context (before) = " + str(context))
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "3", "180", "181", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_4():
    context = None

    print("Test1_4 - level * (ALL) peeps")

    #print("context (before) = " + str(context))
 #   context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
   #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "*", "180", "181", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_5():
    context = None

    print("Test1_5 - level 1,2  peeps, but only the living")

    #print("context (before) = " + str(context))
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "1,2", "180", "181", "False")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_6():
    context = None

    print("Test1_6 - level 1,2,3  peeps, but only the living")

    #print("context (before) = " + str(context))
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "1,2,3", "180", "181", "False")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_7():
    context = None

    print("Test1_7 - level -2 and older peeps")

    #print("context (before) = " + str(context))
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    #print("context (after) = " + str(context))

    items = peeps.getBirthdayList(context, "-2", "183", "183", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return




def test2_1():

    print("TEST LAST YEAR ")
    currentDate = datetime.date(2020, 2, 1)
    dob = datetime.date(1961, 12, 22)
    cbd = peeps.getClosestBirthday(currentDate, dob, "-300")
    assert(cbd.year == 2019)

    print("TEST NEXT YEAR ")
    currentDate = datetime.date(2020, 10, 1)
    dob = datetime.date(1961, 2, 22)
    cbd = peeps.getClosestBirthday(currentDate, dob, "200")
    assert(cbd.year == 2021)

    print("TEST THIS YEAR ")
    currentDate = datetime.date(2020, 2, 20)
    dob = datetime.date(1961, 3, 22)
    cbd = peeps.getClosestBirthday(currentDate, dob, "100")
    assert(cbd.year == 2020)

    return 0

def test3_0():

    context = None
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    list = peeps.produceCSVList(context)
    print("List has " + str(len(list)) + " peeps in it")

    with open('peeps.csv', mode='w', newline="") as csv_file:
        fieldnames = ['index', 'id', 'level', 'firstName', 'familyName', 'preferredName', 'maidenName', 'dob', 'dod', 'fatherIndex', 'motherIndex' ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for row in list:
            writer.writerow(row)

    return

def test4_0():
    print("TEST4_0 - Dump the tree")
    context = None
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    lines = peeps.produceDecendentList(context, "09e34f8b-3f9c-43fa-8c03-3b529c01a1aa")

    for line in lines:
        print(line)
    return

def test5_0():
    print("TEST5_0 - PEOPLE LIST TESTS - single peep")
    context = None
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')
    testGuid = "09e34f8b-3f9c-43fa-8c03-3b529c01a1aa"
    p = peeps.getPeepsList(context, testGuid)

    print("peeps count = " + str(len(peeps)))
    assert(len(p) == 1)
    assert(p[0]['id'] == testGuid)
    assert(p[0]['firstName'] == 'Nita')

    return


def test5_1():
    print("TEST5_1 - PEOPLE LIST TESTS - list of peeps")
    context = None
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')

    p = peeps.getPeepsList(context, "")

    assert(len(p) >= 1)

    print("peeps count = " + str(len(p)))

    return

def test5_2():
    print("TEST5_0 - PEOPLE LIST TESTS - single peep not matched")
    context = None
#    context = peeps.loadPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepFile(context, '../hoh-people.json')

    p = peeps.getPeepsList(context, "11111111-2222-3333-8c03-3b529c01a1aa")

    print("peeps count = " + str(len(p)))
    assert(len(p) == 0)

    return

def test6_0():
    print("TEST6_0 - PEOPLE put a *NEW* peep")
    context = mycontext.newContext()

    p = {}
    p['familyName'] = "TESTFAMILYNAME"
    p['firstName'] = "TESTFIRSTNAME"
    p['birthCertificateSex'] = 'Male'

    r = peeps.putPeep(context, p)
    #r = peeps.putPeep(context, p)
    print("RESULT: " + str(r))

    return

def test9_0():
    print("TEST9_0 TEST THE Birthdays API Via a file input ...")
    fname = "test9.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_0>test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))
 
    return ""

def test9_1():
    print("TEST9_1 TEST THE Peoples API Via a file input ...")

    fname = "test9_1.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_1>test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))

    return ""

def test9_2():
    print("TEST9_2 TEST THE Peoples API Via a file input ...")

    fname = "test9_2.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_1>test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))
    
    assert(z['statusCode'] == "200")
    body = json.loads(z['body'])
    peep = body[0]
    print('peep=-->'+str(peep) + '<--')
    assert(peep['preferredName'] == "Pat")

    return ""


#test1_0()
#test1_1()
#test1_2()
#test1_3()
#test1_4()
#test1_5()
#test1_6()
#test1_7()

#test2_1()

#test3_0()

#test4_0()

#test5_0()
#test5_1()
#test5_2()

test6_0()

#test9_0()
#test9_1()
#test9_2()