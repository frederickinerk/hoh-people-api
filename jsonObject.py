#
# 
#  jsonObject.py
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
# thingy is either a "people" or "relationship"
# Can add "family/clan" by using the autr hack. For the moment it is hoh hard coded.
def get(thingy, id):
    logger.info("jsonObject->get - Entry /  thingy = " + thingy + " id = " + str(id))

    tableName = 'hoh' + thingy          # yes, its hacky
    keys = {'id': id}                   #, 'subject': subject}

    logger.info("jsonObject->get - table " + tableName + " keys = " + str(keys))
 
    item = None
    try:
        table = dynamo.Table(tableName)
        response = table.get_item(Key=keys)
    except Exception as e:
        logger.error("jsonObject->get - Exception = " + str(e))
    else:
        logger.info("jsonObject->get - data returned")
        if 'Item' not in response.keys():
            # Create the default object
            logger.info("jsonObject->get - No item available")
        else:
            item = response['Item']
            
    if item is not None:
        logger.debug("jsonObject->get - returned item:" + str(json.dumps(item, indent=2)))
        logger.info("jsonObject->get - returned item of " + str(len(str(item))) + " bytes")
    else:
        logger.info("jsonObject->get - no item returned")

    logger.info("jsonObject->get - Exit")
    
    return item


##################################################################
# 
# Put Function.
# Create/update a the specified object
# Data is a dict.
# Return 1 (true) for success or 0 for failure
#
def put(data, thingy, id):
    logger.info("jsonObject->put - Entry - for thingy = " + thingy + ", id " + id)
    logger.debug("jsonObject->put - data = " + str(data) ) 

    ret = 0 # failure
    
    # Put a timestamp
    # All objects have the updateEpoch timestamp (or they do now!) 
    epoch = str(int(time.time()))
    logger.info("jsonObject->put epoch = " + epoch)
    data['updatedEpoch'] = epoch
    data['id'] = id
#    data['clientId'] = clientId

    logger.debug("jsonObject->put - data (now) = " + str(data)) 

    tableName = 'hoh' + thingy          # yes, its hacky
    
    logger.info("jsonObject->put - table = " + tableName + " for thingy = " + thingy + " epoch = " + epoch)
    logger.debug("jsonObject->put" + str(data))

    try:
        table = dynamo.Table(tableName)
        response = table.put_item(Item=data)
        logger.debug("jsonObject->put response was - " + str(response))
    except ClientError as e:
        logger.error("jsonObject->put error Storing data - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObject->put Storing data - success thingy = " + thingy + ", id = " + id)
        ret = 1 
   
    logger.info("jsonObject->put - Exit - ret = " + str(ret))
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
    logger.info("jsonObject->getList - Entry - objType = " + objType  + " altKey = " + str(altkey))

    tableName = 'hoh' + objType       

    items = None # Error
    table = dynamo.Table(tableName)
    try:
        logger.debug("jsonObject->getList - about to scan the table = " + tableName)
        response = table.scan()
        logger.debug("jsonObject->getList - done scan. Have a response = " + str(response))
        if not 'Items' in response.keys():
            # Todo Create the default object
            logger.info("jsonObject->getList - no items")
        else:
            items = response['Items']
            logger.info("jsonObject->getList - returned items:" + str(len(items)) + " items")
            logger.debug("jsonObject->getList - returned item:" + str(items))
    except ClientError as e:
        logger.error("jsonObject->getList error Storing data - " + e.response['Error']['Message'])

    logger.info("jsonObject->getList - Exit")
    return items

##################################################################
#
# Get Batch Function.
# return the item or None for error
#
def getJSONObjectByQuery(clientId, objType, keyName, keyValue):
    logger.info("jsonObject->getJSONObjectByQuery - Entry - clientId=" + clientId + " objType=" + objType + " key=" + keyName + " value=" + keyValue)

 # BLAH NEED TO ADD A SORT KEY TO THE BATCH TABLE... WHATEVER THAT MIGHT BE... Maybe status?? 

    tableName = 'autr' + objType + '-' + clientId          # yes, its hacky

    logger.info("jsonObject->getJSONObjectByQuery - query table " + tableName)
    table = dynamo.Table(tableName)

    ret = None  # Error by default
    try:
        response = table.query(
            KeyConditionExpression=Key(keyName).eq(keyValue)    # 'id'
        )
    except ClientError as e:
        logger.error("jsonObject->getJSONObjectByQuery error get by query - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObject->getJSONObjectByQuery  - success")
        if 'Items' in response.keys():
            # should be just one. Todo probably should check.
            if len(response['Items']) > 0:
                logger.info("jsonObject->getJSONObjectByQuery  - item count = " + str(len(response['Items'])))
                ret = response['Items'][0]
                logger.debug("jsonObject->getJSONObjectByQuery - returning:" + str(ret))
            else:
                logger.warn("jsonObject->jsonObject - No Batch found")

    logger.info("jsonObject->getJSONObjectByQuery - Exit")

    return ret


##################################################################
#
# Put Function for a specific Object
# Return 1 (true) for success or 0 for failure
#

def putObjectType(clientId, objType, id, objItem):
    logger.info("jsonObject->putObjectType - Entry - clientId=" + clientId + " objType=" + objType + " id=" + id)
    logger.debug("jsonObject->putObjectType - object=" + str(objItem))

    ret = 0  # failure

    # Put a timestamp
    epoch = str(int(time.time()))
    logger.info("jsonObject->putObjectType epoch = " + epoch)
    objItem['updatedEpoch'] = epoch

    tableName = 'autr' + objType + '-' + clientId          # yes, its hacky
    logger.info("jsonObject->putObjectType - table = " + tableName)

    try:
        table = dynamo.Table(tableName)
        response = table.put_item(Item=objItem)
        logger.debug("jsonObject->putObjectType response was - " + str(response))
    except ClientError as e:
        logger.error("jsonObject->putObjectType error Storing data - " + e.response['Error']['Message'])
    else:
        logger.info("jsonObject->jsonObject Storing data - success")
        ret = 1

    logger.info("jsonObject->jsonObject - Exit")
    return ret


##################################################################
#
# delete Objects Function.
# Obj type is "Batches" etc.
# AltKey is if I want to use the "sort" key. Not implemented yet.
# returns 1 if success
#

def deleteJSONObjects(clientId, objType, id):
    logger.info("jsonObject->deleteJSONObjects - Entry - objType = " + objType + " clientId = " + clientId + " id = " + str(id))

    tableName = 'autr' + objType +  "-" + clientId       

    logger.info("jsonObject->deleteJSONObjects - Tablename = [" + tableName + "]")

    worked = 0  # Error

    table = dynamo.Table(tableName)
    try:
        response = table.delete_item(
            Key={
            'id': id
            }
        )
    except ClientError as e:
        logger.error("jsonObject->deleteJSONObjects - error on delete " + e.response['Error']['Message'])
    else:
        worked = 1
        logger.info("jsonObject->deleteJSONObjects DeleteItem succeeded - response = " + str(response))
    
    logger.info("jsonObject->deleteJSONObjects - Exit")
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

    logger.info("jsonObject->checkObjectStoreExists - Entry")

    dynamodb_client = boto3.client('dynamodb')

    searchTableName = 'autr' + objType +  "-" + clientId       
    logger.info("jsonObject->checkObjectStoreExists - Searching for table - [" + searchTableName + "]")
    exclusiveStartTableName = ""
    while 1:
        # ExclusiveStartTableName=exclusiveStartTableName,
        if exclusiveStartTableName == "": # first call
            response = dynamodb_client.list_tables(Limit=pageSize)
        else:
            response = dynamodb_client.list_tables(ExclusiveStartTableName=exclusiveStartTableName, Limit=pageSize)
        logger.debug("jsonObject->checkObjectStoreExists - response = " + str(response))
        if searchTableName in response['TableNames']:
            result = 1
            break
        if "LastEvaluatedTableName" in response:
            # Loop again
            exclusiveStartTableName = response["LastEvaluatedTableName"]
        else:
            # NOT FOUND, Exit
            break 

    logger.info("jsonObject->checkObjectStoreExists - Exit - result = " + str(result))

    return result

##################################################################
#
# Create new table.
#
# returns 1 if table created, 0 if not something bad happened
#

def createObjectStore(clientId, objType, primaryKey, sortKey):
    logger.info("jsonObject->createObjectStore - Entry - " + clientId + "/" + objType + "/" + primaryKey + "/" + sortKey)

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

        #logger.info("jsonObject->createObjectStore - it takes a while for the jelly to set - wait for AWS to create the tables")
        #waiter = dynamo.meta.client.get_waiter('table_exists')
        #waiter.wait(TableName=tableName)
        #logger.info("jsonObject->createObjectStore - hopefully all is well and our table (" + tableName + ") is now there!")
        # Took out the wait stuff. Works ok locally but not so good in Lambda.
        # Probably OK if there is a delay between a new client and adding other data (tell dave)
        logger.info("jsonObject->createObjectStore - hopefully all is well and our table (" + tableName + ") will be there shortly!")

        logger.info("jsonObject->createObjectStore - Table = " + str(table) )
    except ClientError as ce:
        logger.error("jsonObject->createObjectStore - Failed to create table - errorcode = " + ce.response['Error']['code'] )

    logger.info("jsonObject->createObjectStore - Exit - result = " + str(result))

    return result
