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

import jsonObject

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('mycontext: initialisation starting...')

def newContext():
    logger.info('mycontext.newContext: creating default context object')
    context =  {}
    context['signature'] = 'mycontext'
    return context


def setPeepFile(context, peepFileName):
    if (context is None):
        context =  newContext()
    context['peepFileName'] = peepFileName

    with open(peepFileName) as json_file:
        data = json.load(json_file)    
        index = 0
        for peep in data['peeps']:
            peep['index'] = str(index)
            index += 1
    
    context = setPeeps(context, data['peeps'])
    logger.info("mycontext->loadPeepFIle returned a list " + str(len(data['peeps'])))

    return context

def setPeeps(context, peepList):
    if (context is None):
        logger.info('mycontext.setPeeps: creating default context object')
        context =  newContext()
        context['signature'] = 'mycontext'
    context['peeps'] = peepList
    return context

def getPeeps(context):
    logger.debug('mycontext.getPeeps. Return array with  ' + str(len(context['peeps'])) + ' people')
    return context['peeps'] 

def setPeepObjects(context):
    if (context is None):
        context =  newContext()

    data = jsonObject.getList("People")
    index = 0
    for peep in data:
        peep['index'] = str(index)
        index += 1
    
    context = setPeeps(context, data) 
    logger.info("mycontext->setPeepObjects returned a list " + str(len(data)))

    return context


def setToday(context, dt):
    context['today'] = dt
    return

def getToday(context):
    ret = None
    if 'today' in context:
        if context['today'] != "":
            ret = datetime.date.fromisoformat(context['today'])
    if ret is None:  # any port in a storm
        ret = datetime.date.today() 
    return ret