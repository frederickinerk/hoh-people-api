#
# convert file to objects and vice-versa
# 

import logging
import json
import datetime
from dateutil.relativedelta import relativedelta
import argparse

import mycontext
import peeps
import jsonObject

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())
logger.info('utility: initialisation starting...')

def fileToObjects():
    logger.debug('fileToObjects: Entry')
    print("File to Objects...")
    print("Load the file...")
    context = peeps.loadPeepFile(None, "hoh-people.json")

    ps = mycontext.getPeeps(context)
    print("File had " + str(len(peeps)) + " peeps in it")

    count = 0
    successes = 0
    for p in ps:
        count += 1
        print("Processing peep[" + str(count) + "] " + p['firstName'] + " " + p['familyName'])

        for k in p.keys():
            if p[k] == "":
                p[k] = "<<NOT DEFINED>>"

        x = jsonObject.put(p, "People", p['id'])
        if x == 1:
            successes += 1
            #print("fn returned " + str(x))

    print("Loaded " + str(successes) + " of " + str(count) + " objects")
    return

def validateEntry(p, dictName):
    missing = ""
    if dictName in p:
        if p[dictName] == "" or p[dictName] == "<<NOT DEFINED>>":
            missing += dictName + " "
    return missing

def asMuchAsWeKnow(peep):
    ret = ""
    if 'firstName' in peep:
        ret += peep['firstName'] + " "
    if 'familyName' in peep:
        ret += peep['familyName'] + " "
    if ret == "":
        ret += peep['id']
    return ret

def validateObjects():
    context = None
    context = mycontext.setPeepObjects(context)
    peepList = mycontext.getPeeps(context)

    for peep in peepList:
        #missing = validateEntry(peep, "id")
        missing = validateEntry(peep, "firstName")
        missing += validateEntry(peep, "familyName")
        missing += validateEntry(peep, "level")
        missing += validateEntry(peep, "motherid")
        missing += validateEntry(peep, "fatherid")
        missing += validateEntry(peep, "dob")
        missing += validateEntry(peep, "birthCertificateSex")

        if missing != "":
            print("Validation: " + asMuchAsWeKnow(peep) + " - missing - " + missing)        
    return

def main():
    logger.info('fileToObjects: main')

    parser = argparse.ArgumentParser(description='Peeps Utilities.')
    parser.add_argument('-v', '--validate', action='store_true', default='False', help='Validate the data held')
    parser.add_argument('-u', '--upload',  action='store_true', default='False', help='Upload the magic file')    #ToDo allow file to be added as parm
    parser.add_argument('-d', '--download',  action='store_true', default='False', help='Download to the magic file')    #ToDo allow file to be added as parm

    args = parser.parse_args()
    print(args)
    
    if args.upload == True:
        print("Uploading...")
        fileToObjects()

    if args.validate == True:
        print("Validating...")
        validateObjects()

    if args.download == True:
        print("Download...")
    return

main()
