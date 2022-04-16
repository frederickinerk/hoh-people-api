####### 
## CONTEXT OBJECT FOR THE PROCESSING
## Stores data to be passed around in a dictionary
## Current Contents are:
## + signature      - eyecatcher
## + peeps          - list of peeps
#######

import logging
import json
import datetime

import jsonObjectDynamo

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('mycontext: initialisation starting...')


#######
# CONTEXT OBJECT FOR THE PROCESSING
# Allow either files or dynamo objects to be used.
#######

def newContext():
    logger.info('mycontext.newContext: creating default context object')
    theContext = {}
    theContext['signature'] = 'mycontext'
    return theContext

def setObjectHandler(objectHandler):
    logger.info('mycontext.setObjectHandler')
    context = getContext()
    context['objHandler'] = objectHandler
    return 

def getObjectHandler():
    logger.info('mycontext.getObjectHandler')
    context = getContext()
    if not 'objHandler' in context:
        context['objHandler'] = jsonObjectDynamo
    return context['objHandler']

def getContext():
    logger.debug("mycontext.getContext:  context object = " + str(theContext))
    return theContext

##
# Allow the date to be overridden for testing and dealing with timezones
def setToday(context, dt):
    context['today'] = dt
    return

def getToday(context):
    ret = None
    try:
        if 'today' in context:
            if context['today'] != "":
                dt = context['today']
                i = dt.find("T")
                if i != -1:
                    dt = dt[0: i]
                logger.info("mycontext->getToday make date from  - " + str(dt) )
                ret = datetime.date.fromisoformat(dt)
    except:
        logger.error("mycontext->getToday Exception in formatting date" )
    if ret is None:  # any port in a storm
        ret = datetime.date.today() 
    logger.info("mycontext->getToday returning date - " + str(ret) )
    return ret

###
# Global Instance variable
##

theContext = {'signature': 'mycontext'}
