#
# people tests
# 

import logging
import json
import datetime
import csv

import peeps
import birthdays

import hohPeopleApi

import mycontext
import jsonObjectDynamo
import jsonObjectFile

import MyAPIException

import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.info('peepTests: initialisation starting...')


# Test with a subject
def test1_0():
    print("Test1_0 - level 0 peeps")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "0", "365", "365", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)

    return

def test1_1():
    context = None

    print("Test1_1 - level 1 peeps")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "True", "345", "364", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_2():
    context = None

    print("Test1_2 - level 2 peeps")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)
    mycontext.setToday(context, "2020-04-07")

    items = birthdays.getBirthdayList(context, "2", "100", "100", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_3():
    context = None

    print("Test1_3 - level 3 peeps")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "3", "180", "181", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_4():
    print("Test1_4 - level * (ALL) peeps")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "*", "180", "181", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_5():
    print("Test1_5 - level 1,2  peeps, but only the living")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "1,2", "180", "181", "False")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_6():
    print("Test1_6 - level 1,2,3  peeps, but only the living")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "1,2,3", "180", "181", "False")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test1_7():
    print("Test1_7 - level -2 and older peeps")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    items = birthdays.getBirthdayList(context, "-2", "183", "183", "True")
    print("Peeps matched")
    for item in items:
        print("peep " + peeps.getPreferredName(item) + " birthday is in " + item['daysAway'] + " days")
    assert(len(items) >= 0)
    return

def test2_1():
    print("TEST LAST YEAR ")
    currentDate = datetime.date(2020, 2, 1)
    dob = datetime.date(1961, 12, 22)
    cbd = birthdays.getClosestBirthday(currentDate, dob, -300)
    assert(cbd.year == 2019)

    print("TEST NEXT YEAR ")
    currentDate = datetime.date(2020, 10, 1)
    dob = datetime.date(1961, 2, 22)
    cbd = birthdays.getClosestBirthday(currentDate, dob, 200)
    assert(cbd.year == 2021)

    print("TEST THIS YEAR ")
    currentDate = datetime.date(2020, 2, 20)
    dob = datetime.date(1961, 3, 22)
    cbd = birthdays.getClosestBirthday(currentDate, dob, 100)
    assert(cbd.year == 2020)

    return 0

def test3_0():
    print("TEST3_0 - produce CSV file")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    list = peeps.produceCSVList(context)
    print("Done --- List has " + str(len(list)) + " peeps in it")

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
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    lines = peeps.produceDecendentList(context, "09e34f8b-3f9c-43fa-8c03-3b529c01a1aa")
    print("Test produced " + str(len(lines)) + " lines")
    for line in lines:
        print(line)
    return

def test5_0():
    print("TEST5_0 - PEOPLE  TESTS - single peep")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)
    #mycontext.setObjectHandler(jsonObjectDynamo)

    testGuid = "09e34f8b-3f9c-43fa-8c03-3b529c01a1aa"
    p = peeps.getPeep(context, testGuid)

    print("peeps count = " + str(len(p)))
    assert(len(p) == 1)
    assert(p[0]['id'] == testGuid)
    assert(p[0]['firstName'] == 'Nita')

    return


def test5_1():
    print("TEST5_1 - PEOPLE LIST TESTS - list of peeps")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    p = peeps.getPeepsList(context)

    assert(len(p) >= 1)

    print("peeps count = " + str(len(p)))

    for peep in p:
        print(peep['familyName'] + ", " + peep['firstName'])

    return

def test5_2():
    print("TEST5_0 - PEOPLE LIST TESTS - single peep not matched")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    try:
        p = peeps.getPeep(context, "11111111-2222-3333-8c03-3b529c01a1aa")
        print("Testcase failed! Should not return - p=" + str(p))
        assert(False)
    except MyAPIException.MyAPIException as apiEx:
        code = apiEx.args[0]
        msg = apiEx.args[1]
        print("API Exception code = " + code + " msg = " + msg)
        print("Test Case success!!")
        assert(True)
    except Exception as ex:
        print("Unexpected exception: " + str(ex))
        assert(True)

    return

def test5_3():
    print("TEST5_3 - PEOPLE LIST TESTS - familyName and sex pecfied")
    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)

    p = peeps.getPeepsList(context, "Dean", "Female")

    print("peeps count = " + str(len(p)))
    for a in p:
        print(a['firstName'])
    assert(len(p) > 0)

    return

def test6_0():
    print("TEST6_0 - PEOPLE put a *NEW* peep")
    context = mycontext.newContext()
    mycontext.setObjectHandler(jsonObjectFile)

    xRand = random.randint(0,100)

    p = {}
    p['familyName'] = "TESTFAMILYNAME-" + str(xRand)
    r = peeps.putPeep(context, p)
    createdId = None 
    #r = peeps.putPeep(context, p)
    print("RESULT: " + str(r))

    if 'id' in r:
        createdId = r['id'] 
        print("Looks like it worked")
        p['id'] = createdId
        p['firstName'] = "TESTFIRSTNAME-" + str(xRand)
        # PUT IT IN AGAIN
        r = peeps.putPeep(context, p)
        #r = peeps.putPeep(context, p)
        #print("RESULT: " + str(r))

        p['birthCertificateSex'] = "Male"

        # PUT IT IN AGAIN
        r = peeps.putPeep(context, p)
        #r = peeps.putPeep(context, p)
        #print("RESULT: " + str(r))
    
    # Test it worked.
    assert(not createdId is None)
    testPeep = peeps.getPeep(context, createdId)[0]
    assert(testPeep['familyName'] == "TESTFAMILYNAME-" + str(xRand))
    assert(testPeep['firstName'] == "TESTFIRSTNAME-" + str(xRand))

    return

def test9_0():
    print("TEST9_0 TEST THE Birthdays API Via a file input ...")

    mycontext.setObjectHandler(jsonObjectFile)

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
    mycontext.setObjectHandler(jsonObjectFile)

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
    mycontext.setObjectHandler(jsonObjectFile)

    fname = "test9_2.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_2>test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))
    
    assert(z['statusCode'] == "200")
    body = json.loads(z['body'])
    peep = body[0]
    print('peep=-->'+str(peep) + '<--')
    assert(peep['preferredName'] == "Pat")

    return ""

def test9_3():
    print("TEST9_3 TEST THE Peoples API Via a file input ... (A PUT)")
    mycontext.setObjectHandler(jsonObjectFile)

    fname = "test9_3.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_3->test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))
    
    assert(z['statusCode'] == "200")
    res = json.loads(z['body'])
    assert(res['result'] == "Success")

    return ""

def test9_4():
    print("TEST9_4 TEST THE Birthdays API Via a file input ...")

    mycontext.setObjectHandler(jsonObjectFile)

    fname = "test9_4.json"
    with open(fname) as json_data:
        testJson = json.load(json_data)
        json_data.close()
    print("TEST9_4>test - Json loaded from file: " + fname + " ... length = " + str(len(str(testJson))))
    z = hohPeopleApi.api_handler(testJson, "Hello")
    print("Returned: " + str(z))
 
    return ""


def test10_0():
    print("Test10_0 - todays birthdays")

    context = mycontext.newContext()
    # set the handler to files for these tests
    mycontext.setObjectHandler(jsonObjectFile)
    mycontext.setToday(context, "2020-06-02")

    str = birthdays.getTodaysBirthdays(context)
    print(f'Todays birthdays = {str}')

    return

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
#test5_3()

#test6_0()

#test9_0()
#test9_1()
#test9_2()
#test9_3()
test9_4()

#test10_0()
