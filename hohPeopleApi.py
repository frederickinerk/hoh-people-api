# Lambda function to return the various Objects. Triggered GET/PUT functions.
# 
import json
import logging
import datetime
#import os

#import time
#from datetime import tzinfo, timedelta, datetime, date

# Related modules
import peeps
import mycontext


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO logger.addHandler(logging.StreamHandler())
logger.info('hoh-people-api: initialisation starting. (Mar 2020)..')

#dynamo = boto3.resource('dynamodb')

##################################################################
# 
# getQueryString Function.
# return the query string if it exists or an empty string
#
def getQueryString(query, dictName, default=""):
    logger.info("hoh-people-api->getQueryString - Processing query string - " + dictName)
    if query is None: 
        return default
    if not dictName in query:
        return default
    if query[dictName] == "":
        return ""

    if query[dictName][0] == '\"': 
        logger.info("hoh-people-api->getQueryString - Quoted string was [" + query[dictName] + "]")
        query[dictName] = query[dictName][1:len(query[dictName]) - 1]
        logger.info("hoh-people-api->getQueryString - Quoted string is now [" + query[dictName] + "]")
        return query[dictName]
    else:
        return query[dictName]

##################################################################
# 
# valIfExists.
# Helper function to return a dictionary item if it exist or default
# return value for dict
#  
def valIfExists(entry, dictName, defValue=""):
    logger.debug("hoh-people-api->valIfExists - dictName = " + dictName)

    if dictName in entry:
        if entry[dictName] == "<<NOT DEFINED>>":  # Undo the placeholder
            return ""
        return entry[dictName]
    return defValue

##################################################################
# 
# PrivateValIfExists.
# Helper function to return a obscured dictionary item for the living
# if it exists or a "not reccorded" value 
# return value for dict
#  
def PrivateValIfExists(entry, dictName, private):
    retVal = "Not Recorded"
    if dictName in entry:
        if entry[dictName] != "<<NOT DEFINED>>":  # Undo the placeholder
            if private:
                retVal = "Recorded"
            else:
                retVal = entry[dictName]
    return retVal

##################################################################
# 
# FormatMyDate.
# Helper function to format dates like I like them
# return formatted function
#  
def FormatMyDate(entry, dictName):
    fmtDate = ""
    if dictName in entry:
        if entry[dictName] != "":
            dt = datetime.datetime.strptime(entry[dictName], "%Y-%m-%d")
            fmtDate = dt.strftime("%d-%b-%Y")
            if (fmtDate[0] == '0'):
                fmtDate = fmtDate[1:len(fmtDate)]
    return fmtDate

#################################################################
# 
# FormatFamName.
# Helper function to format family names like I like them
# return formatted value (includes leading space)
#  
def FormatMyFamName(entry):
    ret = ""
    if 'familyName' in entry:
        if entry['familyName'] != "":
            ret += " " + entry['familyName']
            if 'maidenName' in entry:
                if entry['maidenName'] != "":
                    ret += " (née " + entry['maidenName'] + ")"
    return ret

#################################################################
# 
# CalcDQScore.
# Helper function to give a number reflecting the amount of data 
# defined for the persion
# return string value of the score (currently out of 5)
# 
def CalcDQScore(entry):
    score = 0
    if entry['dob'] != "Not Recorded":
        score += 1
    if entry['firstName'] != "Not Recorded" and entry['firstName'] != "":
        score += 1
    if entry['familyName'] != "Not Recorded" and entry['familyName'] != "":
        score += 1
    if entry['motherid'] != "Not Recorded":
        score += 1
    if entry['fatherid'] != "Not Recorded":
        score += 1
    return str(score)
    

##################################################################
# 
# Get Birthdays Function.
# Passed query values for before/after dates, all/living flag and generations list
# return 0 for OK, 1 for error BLAH TODO
# return the JSON text 
#
def getBirthdays(action, operation, query):
    logger.info("hoh-people-api->getBirthdays - Entry")

    daysBefore = getQueryString(query, "daysBefore", "28")
    daysAfter = getQueryString(query, "daysAfter", "7")
    allFlag = getQueryString(query, "allFlag", "false")
    generations = getQueryString(query, "generations", "3")
    today = getQueryString(query, "date", "")

    logger.info("hoh-people-api->getBirthdays - daysBefore = " + daysBefore + ", daysAfter = " + daysAfter + " allFlag =" + allFlag + " generations = " + generations )

    # TODO THIS NEEDS TO BE WAY SMARTER
    context = None
    #context = mycontext.setPeepFile(context, '../hoh-people.json')
    context = mycontext.setPeepObjects(context)
    mycontext.setToday(context, today)

    list = peeps.getBirthdayList(context, generations, daysBefore, daysAfter, allFlag)

    # curate the list returned to just what we want
    retList = []
    for val in list:
        entry = {}
        entry['id'] = val['id']
        entry['daysAway'] = val['daysAway']
        entry['name'] = peeps.getPreferredName(val, True)
    
        if 'birthCertificateSex' in val:
            entry['birthSex'] = val['birthCertificateSex']
        else:
            entry['birthSex'] = "unknown"
        if 'dod' in val:
            entry['dobFmt'] = FormatMyDate(val, 'dob')
            entry['dodFmt'] = FormatMyDate(val, 'dod')
            entry['living'] = "False"
            entry['name'] += FormatMyFamName(val)   # Return full name for the departed
        else:
            entry['living'] = "True"
        if int(val['age']) > 16 and entry['living'] == "True":
            entry['ageAtBirthday'] = "-1"
        else:
            entry['ageAtBirthday'] = val['age']
        
        retList.append(entry) 

    retJson = json.dumps(retList)

    logger.info("hoh-people-api->getBirthdays - returned item: " + str(retJson) + " bytes")
    
    logger.debug("hoh-people-api->getBirthdays - returning:" + retJson)
    logger.info("hoh-people-api->getBirthdays - Exit")
    return retJson

##################################################################
# 
# Get Peoples Function.
# Passed query values for BLAH
# return 0 for OK, 1 for error BLAH TODO
# return the JSON text 
#
def getPeoples(action, operation, query):
    logger.info("hoh-people-api->getPeoples - Entry")

    id = getQueryString(query, "id", "")
    logger.info("hoh-people-api->getPeoples - got the queryStrings - id = [" + id + "]")

    context = None
    context = mycontext.setPeepObjects(context)

    logger.info("hoh-people-api->getPeoples - get the list of peeps")
    list = peeps.getPeepsList(context, id)
    logger.info("hoh-people-api->getPeoples - the list of peeps has " + str(len(list)) + " peeps in it")

    # curate the list returned to just what we want
    retList = []
    i = 0
    for val in list:
        i += 1
        logger.debug("hoh-people-api->getPeoples - processing peep " + str(i))

        entry = {}
        entry['id'] = valIfExists(val, 'id')
        entry['firstName'] =  valIfExists(val, 'firstName')
        entry['familyName'] =  valIfExists(val, 'familyName')
        entry['preferredName'] =  valIfExists(val, 'preferredName')
    
        entry['birthSex'] = valIfExists(val, 'birthCertificateSex', "Unknown")
        entry['living'] = 'True'
        if 'dod' in val:
            if len(val['dod']) == 10:
                entry['living'] = 'False'
        entry['dob'] = PrivateValIfExists(val, 'dob', entry['living'] == 'True')
        entry['dod'] = PrivateValIfExists(val, 'dod', entry['living'] == 'True')
        entry['motherid'] = PrivateValIfExists(val, 'motherid', entry['living'] == 'True')
        entry['fatherid'] = PrivateValIfExists(val, 'fatherid', entry['living'] == 'True')
        entry['dqScore'] = CalcDQScore(entry)
        retList.append(entry) 

    retJson = json.dumps(retList)
    
    logger.debug("hoh-people-api->getPeoples - returning:" + retJson)
    logger.info("hoh-people-api->getPeoples - Exit")
    return retJson

##################################################################
# 
# getActionEntry
# Return the dict corresponding to the supplied resource and operation.
#
def getActionEntry(resource, operation):
    logger.info("hoh-people-api->getActionEntry: Looking for " + resource + " for operation " + operation)
    theDict = None
    i = 0
    for action in actionTable:
        #logger.info("Action table entry: " + str(i))
        if (action["resource"] == resource and action["operation"] == operation):
            theDict = action
            logger.info("hoh-people-api->getActionEntry: Found a match")
            break
        i = i + 1

    if theDict is None:
        logger.error("hoh-people-api->getActionEntry: Failed to find a match")
    return theDict

##################################################################
# 
# respond
# Generic responsefor success function returning standard headers.
#
def respondOK(operation, res=""):

    logger.info("hoh-people-api->respondOK - res is " + str(len(res)) + " bytes")
    return {
        'statusCode': '200',
        'body': res,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": "*" ,
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": operation
        },
    }

##################################################################
# 
# respondErr
# Generic responsefor failure function returning standard headers.
#
def respondErr(operation, code, msg):

    logger.info("hoh-people-api->respondErr - code is " + code + " msg = " + msg)
    return {
        'statusCode': code,
        'message': msg,
        'body': "",
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": "*" ,
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": operation
        },
    }


##################################################################
# 
# lambda_handler Function.
# Default AWS lambda entry point
#
def api_handler(event, context):

    logger.debug("hoh-people-api->api_handler: Received event: event = " + json.dumps(event, indent=2))
    
    try:
        operation = event['httpMethod']
        path = event['path']
        query = event['queryStringParameters'] 
        body = event['body']
        logger.info("hoh-people-api->api_handler - Operation = [" + operation + "] path = [" + path + "] query = " + str(query))

        action = getActionEntry(path, operation)

        if action is None:
            errorText = '{"message": "Operation [' + operation + '] is not supported for resource [' + path + ']"}'
            logger.error("hoh-people-api->api_handler - Failed: " + errorText)
            return respondErr(operation, "400", "Requested resource unknown")
        
        logger.info("hoh-people-api->api_handler - OPERATION: " + operation + " Resource: " + path + " with query:" + str(query))
        
        if operation == 'GET':
            logger.info("hoh-people-api->api_handler - GET OPERATION")
            get_fn = action["fn"]
            retJson = (get_fn)(action, operation, query)
        elif operation == 'PUT':
            logger.info("hoh-people-api->api_handler - PUT OPERATION")
            put_fn = action["fn"]
            retJson = put_fn(action, operation, path, query, body)
        else:
            # TODO something dodgy requested
            logger.error("hoh-people-api->api_handler - XXX OPERATION: " + operation)
            return respondErr(operation, "400", "Requested operation not supported (" + operation + ")")

        logger.debug("hoh-people-api->api_handler - retJson = " + retJson)

    except Exception as ex:
        # Something bad happend. TODO make smarter
        logger.error("hoh-people-api->api_handler - Internal excpetion: " + operation + " TRACE - " + str(ex))
        return respondErr(operation, "500", "Something bad happened")

    return respondOK(operation, retJson) 


# Define the Action table     
# Service List

logger.info('hoh-people-api->load: action table loading... = ')
actionTable = []
actionTable.append({"resource": "/birthdays", "operation": "GET", "fn": getBirthdays})
actionTable.append({"resource": "/peoples", "operation": "GET", "fn": getPeoples})

logger.info('hoh-people-api->load: loaded action table - entries = ' + str(len(actionTable)))
