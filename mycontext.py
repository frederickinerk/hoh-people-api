####### 
## CONTEXT OBJECT FOR THE PROCESSING
## Stores data to be passed around in a dictionary
## Current Contents are:
## + signature      - eyecatcher
## + peeps          - list of peeps
#######

import logging
import json

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
    logger.info("peep->loadPeepFIle returned a list " + str(len(data['peeps'])))

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
