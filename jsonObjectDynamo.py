#
# 
#  jsonObjectDynamo.py
#  Wrapper for DynamoDB
#

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

import json
import logging

import time
from datetime import tzinfo, timedelta, datetime, date

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())
logger.info('jsonObject: initialisation starting...')

dynamo = boto3.resource('dynamodb')

#################################################################
#
# T H I N G Y   F U N C T I O N S
#
#################################################################

##################################################################
# get Function (for thingies)
# return the dictionary item or None for error
# thingy is either a "People" or "relationship"
# Can add "family/clan" by using the autr hack. For the moment it is hoh hard coded.
def get(thingy, id):
    logger.info("jsonObjectDynamo->get - Entry /  thingy = " + thingy + " id = " + str(id))

    tableName = 'hoh' + thingy          # yes, its hacky
    keys = {'id': id}                   #, 'subject': subject}

    logger.info("jsonObjectDynamo->get - table " + tableName + " keys = " + str(keys))
 
    item = None
    try:
        table = dynamo.Table(tableName)
        #response = table.get_item(Key=keys)
        response = table.query(KeyConditionExpression=Key('id').eq(id))

    except Exception as e:
        logger.error("jsonObjectDynamo->get - Exception = " + str(e))
    else:
        logger.info("jsonObjectDynamo->get - data returned")
        logger.info("jsonObjectDynamo->get - data returned = [" + str(response) + "]")
        if 'Items' not in response.keys():
            # Create the default object
            logger.info("jsonObjectDynamo->get - No items available")
        else:
            if len(response['Items']) == 0:
                item = None
            else:
                item = response['Items'][0]         # TODO check if there is more than one.
            
    if item is not None:
        logger.debug("jsonObjectDynamo->get - returned item:" + str(json.dumps(item, indent=2)))
        logger.info("jsonObjectDynamo->get - returned item of " + str(len(str(item))) + " bytes")
    else:
        logger.info("jsonObjectDynamo->get - no item returned")

    logger.info("jsonObjectDynamo->get - Exit")
    
    return item


##################################################################
# 
# Put Function.
# Create/update a the specified object
# Data is a dict.
# Return 1 (true) for success or 0 for failure
#
def put(data, thingy, id):
    logger.info("jsonObjectDynamo->put - Entry - for thingy = " + thingy + ", id " + id)
    logger.debug("jsonObjectDynamo->put - data = " + str(data) ) 

    ret = 0 # failure
    
    # Put a timestamp
    # All objects have the updateEpoch timestamp (or they do now!) 
    epoch = str(int(time.time()))
    logger.info("jsonObjectDynamo->put epoch = " + epoch)
    data['updatedEpoch'] = epoch
    data['id'] = id
#    data['clientId'] = clientId

    logger.debug("jsonObjectDynamo->put - data (now) = " + str(data)) 

    tableName = 'hoh' + thingy          # yes, its hacky
    
    logger.info("jsonObjectDynamo->put - table = " + tableName + " for thingy = " + thingy + " epoch = " + epoch)
    logger.debug("jsonObjectDynamo->put" + str(data))

    try:
        table = dynamo.Table(tableName)
        response = table.put_item(Item=data)
        logger.debug("jsonObjectDynamo->put response was - " + str(response))
    except ClientError as e:
        logger.error("jsonObjectDynamo->put error Storing data - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObjectDynamo->put Storing data - success thingy = " + thingy + ", id = " + id)
        ret = 1 
   
    logger.info("jsonObjectDynamo->put - Exit - ret = " + str(ret))
    return ret

#################################################################
#
# O B J E C T S    F U N C T I O N S
#
#################################################################

##################################################################
#
# Get Objects Function.
# Obj type is "People" etc.
# AltKey is if I want to use the "sort" key. Not implemented yet.
# return item list or none
#

def getList(objType, altkey=None):
    logger.info("jsonObjectDynamo->getList - Entry - objType = " + objType  + " altKey = " + str(altkey))

    tableName = 'hoh' + objType       

    items = None # Error
    table = dynamo.Table(tableName)
    try:
        logger.debug("jsonObjectDynamo->getList - about to scan the table = " + tableName)
        response = table.scan()
        logger.debug("jsonObjectDynamo->getList - done scan. Have a response = " + str(response))
        if not 'Items' in response.keys():
            # Todo Create the default object
            logger.info("jsonObjectDynamo->getList - no items")
        else:
            items = response['Items']
            logger.info("jsonObjectDynamo->getList - returned items:" + str(len(items)) + " items")
            logger.debug("jsonObjectDynamo->getList - returned item:" + str(items))
    except ClientError as e:
        logger.error("jsonObjectDynamo->getList error Storing data - " + e.response['Error']['Message'])

    logger.info("jsonObjectDynamo->getList - Exit")
    return items

##################################################################
#
# Get list by query Function.
# return the item or None for error
#
def getjsonObjectQuery(clientId, objType, keyName, keyValue):
    logger.info("jsonObjectDynamo->getJSONObjectByQuery - Entry - clientId=" + clientId + " objType=" + objType + " key=" + keyName + " value=" + keyValue)

 # BLAH NEED TO ADD A SORT KEY TO THE BATCH TABLE... WHATEVER THAT MIGHT BE... Maybe status?? 

    tableName = 'autr' + objType + '-' + clientId          # yes, its hacky

    logger.info("jsonObjectDynamo->getJSONObjectByQuery - query table " + tableName)
    table = dynamo.Table(tableName)

    ret = None  # Error by default
    try:
        response = table.query(
            KeyConditionExpression=Key(keyName).eq(keyValue)    # 'id'
        )
    except ClientError as e:
        logger.error("jsonObjectDynamo->getJSONObjectByQuery error get by query - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObjectDynamo->getJSONObjectByQuery  - success")
        if 'Items' in response.keys():
            # should be just one. Todo probably should check.
            if len(response['Items']) > 0:
                logger.info("jsonObjectDynamo->getJSONObjectByQuery  - item count = " + str(len(response['Items'])))
                ret = response['Items'][0]
                logger.debug("jsonObjectDynamo->getJSONObjectByQuery - returning:" + str(ret))
            else:
                logger.warn("jsonObjectDynamo->jsonObject - No Batch found")

    logger.info("jsonObjectDynamo->getJSONObjectByQuery - Exit")

    return ret


##################################################################
#
# Put Function for a specific Object
# Return 1 (true) for success or 0 for failure
#

def putObjectType(clientId, objType, id, objItem):
    logger.info("jsonObjectDynamo->putObjectType - Entry - clientId=" + clientId + " objType=" + objType + " id=" + id)
    logger.debug("jsonObjectDynamo->putObjectType - object=" + str(objItem))

    ret = 0  # failure

    # Put a timestamp
    epoch = str(int(time.time()))
    logger.info("jsonObjectDynamo->putObjectType epoch = " + epoch)
    objItem['updatedEpoch'] = epoch

    tableName = 'autr' + objType + '-' + clientId          # yes, its hacky
    logger.info("jsonObjectDynamo->putObjectType - table = " + tableName)

    try:
        table = dynamo.Table(tableName)
        response = table.put_item(Item=objItem)
        logger.debug("jsonObjectDynamo->putObjectType response was - " + str(response))
    except ClientError as e:
        logger.error("jsonObjectDynamo->putObjectType error Storing data - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObjectDynamo->jsonObject Storing data - success")
        ret = 1

    logger.info("jsonObjectDynamo->jsonObject - Exit")
    return ret


##################################################################
#
# delete Objects Function.
# Obj type is "Batches" etc.
# AltKey is if I want to use the "sort" key. Not implemented yet.
# returns 1 if success
#

def deletejsonObjectDynamo(clientId, objType, id):
    logger.info("jsonObjectDynamo->deleteJSONObjects - Entry - objType = " + objType + " clientId = " + clientId + " id = " + str(id))

    tableName = 'autr' + objType +  "-" + clientId       

    logger.info("jsonObjectDynamo->deleteJSONObjects - Tablename = [" + tableName + "]")

    worked = 0  # Error

    table = dynamo.Table(tableName)
    try:
        response = table.delete_item(
            Key={
            'id': id
            }
        )
    except ClientError as e:
        logger.error("jsonObjectDynamo->deleteJSONObjects - error on delete " + e.response['Error']['Message'])
    else:
        worked = 1
        logger.info("jsonObjectDynamo->deleteJSONObjects DeleteItem succeeded - response = " + str(response))
    
    logger.info("jsonObjectDynamo->deleteJSONObjects - Exit")
    return worked

##################################################################
#
# Check table  exists.
# 
# returns 1 if table exists, 0 if not exists
#
def checkObjectStoreExists(clientId, objType):
    result = 0 
    pageSize = 100

    logger.info("jsonObjectDynamo->checkObjectStoreExists - Entry")

    dynamodb_client = boto3.client('dynamodb')

    searchTableName = 'autr' + objType +  "-" + clientId       
    logger.info("jsonObjectDynamo->checkObjectStoreExists - Searching for table - [" + searchTableName + "]")
    exclusiveStartTableName = ""
    while 1:
        # ExclusiveStartTableName=exclusiveStartTableName,
        if exclusiveStartTableName == "": # first call
            response = dynamodb_client.list_tables(Limit=pageSize)
        else:
            response = dynamodb_client.list_tables(ExclusiveStartTableName=exclusiveStartTableName, Limit=pageSize)
        logger.debug("jsonObjectDynamo->checkObjectStoreExists - response = " + str(response))
        if searchTableName in response['TableNames']:
            result = 1
            break
        if "LastEvaluatedTableName" in response:
            # Loop again
            exclusiveStartTableName = response["LastEvaluatedTableName"]
        else:
            # NOT FOUND, Exit
            break 

    logger.info("jsonObjectDynamo->checkObjectStoreExists - Exit - result = " + str(result))

    return result

##################################################################
#
# Create new table.
#
# returns 1 if table created, 0 if not something bad happened
#

def createObjectStore(clientId, objType, primaryKey, sortKey):
    logger.info("jsonObjectDynamo->createObjectStore - Entry - " + clientId + "/" + objType + "/" + primaryKey + "/" + sortKey)

    result = 0

    try:
        tableName = 'autr' + objType + "-" + clientId
        table = dynamo.create_table(
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': primaryKey,
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': sortKey,
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': primaryKey,
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': sortKey,
                    'AttributeType': 'S'
                },

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2
            }
        )
        result = 1 # It worked

        #logger.info("jsonObjectDynamo->createObjectStore - it takes a while for the jelly to set - wait for AWS to create the tables")
        #waiter = dynamo.meta.client.get_waiter('table_exists')
        #waiter.wait(TableName=tableName)
        #logger.info("jsonObjectDynamo->createObjectStore - hopefully all is well and our table (" + tableName + ") is now there!")
        # Took out the wait stuff. Works ok locally but not so good in Lambda.
        # Probably OK if there is a delay between a new client and adding other data (tell dave)
        logger.info("jsonObjectDynamo->createObjectStore - hopefully all is well and our table (" + tableName + ") will be there shortly!")

        logger.info("jsonObjectDynamo->createObjectStore - Table = " + str(table) )
    except ClientError as ce:
        logger.error("jsonObjectDynamo->createObjectStore - Failed to create table - errorcode = " + ce.response['Error']['code'] )

    logger.info("jsonObjectDynamo->createObjectStore - Exit - result = " + str(result))

    return result
