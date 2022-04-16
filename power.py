#
# power class - Different objects with stuff
# 

import logging
import json
import datetime
import uuid

import mycontext

#import jsonObjectDynamo   # TODO REwork like MBS

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('power: initialisation starting...')



###
# putEnvoy5S
# create or update a "envoy5S" record
# returns result (worked/faild)
###

def putEnvoy5s(rec):
    logger.info("power->putEnvoy5s entry")

    objHandler = mycontext.getObjectHandler()
    x = objHandler.put(rec, "Power", "envoy5s")
    
    if x == 1:
        #print("fn returned " + str(x))
        result = {'result': 'Success', 'id': "envoy5s"}
    else:
        result = {'result': 'Failed'}

    logger.info("peep->putEnvoy5s exit")

    return result

###
# gettEnvoy5S
# get a "envoy5S" record
# returns record
###

def getEnvoy5s():
    logger.info("power->getEnvoy5s entry")

    objHandler = mycontext.getObjectHandler()
    
    rec = objHandler.get("Power", "envoy5s")
    
    logger.info("peep->getEnvoy5s exit")

    return rec
