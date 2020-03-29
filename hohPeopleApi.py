# Lambda function to return the various Objects. Triggered GET/PUT functions.
# 
import json
import logging
#import os

#import time
#from datetime import tzinfo, timedelta, datetime, date

# Related modules
import peep
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

    if dictName in query:
        return query[dictName]
    else:
        return default


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
    daysAfter = getQueryString(query, "daysBefore", "7")
    allFlag = getQueryString(query, "allFlag", "allFlag")
    generations = getQueryString(query, "generations", "3")

    logger.info("hoh-people-api->getBirthdays - daysBefore = " + daysBefore + ", daysAfter = " + daysAfter + " list =" + allFlag + " generations = " + generations )

    # TODO THIS NEEDS TO BE WAY SMARTER
    context = None
    context = mycontext.setPeepFile(context, '../hoh-people.json')

    list = peep.getBirthdayList(context, generations, daysBefore, daysAfter, allFlag)

    # curate the list returned to just what we want
    retList = []
    for val in list:
        entry = {}
        entry['daysAway'] = val['daysAway']
        entry['name'] = peep.getPreferredName(val, True)
        if int(val['age']) > 99:    #16:
            entry['ageAtBirthday'] = "-1"
        else:
            entry['ageAtBirthday'] = val['age']
        if 'birthCertificateSex' in val:
            entry['birthSex'] = val['birthCertificateSex']
        else:
            entry['birthSex'] = "unknown"
        retList.append(entry) 

    retJson = json.dumps(retList)

    logger.info("hoh-people-api->getBirthdays - returned item: " + str(retJson) + " bytes")
    
    logger.debug("hoh-people-api->getBirthdays - returning:" + retJson)
    logger.info("hoh-people-api->getBirthdays - Exit")
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
# Generic response function returning standard headers.
#
def respond(err, operation, res=None):

    # TODO this needs some work...

    logger.info("hoh-people-api->respond - err = " + str(err) + " res is " + str(len(res)) + " bytes")
    return {
        'statusCode': '400' if err == 1 else '200',
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
# lambda_handler Function.
# Default AWS lambda entry point
#
def api_handler(event, context):

    logger.debug("hoh-people-api->api_handler: Received event: event = " + json.dumps(event, indent=2))
    
    operation = event['httpMethod']
    path = event['path']
    query = event['queryStringParameters'] 
    body = event['body']
    logger.info("hoh-people-api->api_handler - Operation = [" + operation + "] path = [" + path + "] query = " + str(query))

    action = getActionEntry(path, operation)

    if action is None:
        errorText = '{"message": "Operation [' + operation + '] is not supported for resource [' + path + ']"}'
        logger.info("hoh-people-api->api_handler - Failed: " + errorText)
        return respond(1, operation, errorText)
    
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
    
    logger.info("hoh-people-api->api_handler - retJson = " + retJson)
    
    return respond(0, operation, retJson) 


# Define the Action table     
# Service List

logger.info('hoh-people-api->load: action table loading... = ')
actionTable = []
actionTable.append({"resource": "/hoh-people-api/birthdays", "operation": "GET", "fn": getBirthdays})

logger.info('hoh-people-api->load: loaded action table - entries = ' + str(len(actionTable)))
