#
# people class
# 

import logging
import json
import datetime
from dateutil.relativedelta import relativedelta
import uuid

import mycontext

import jsonObjectDynamo   # TODO REwork like MBS

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('peep: initialisation starting...')


###
# getPreferredName
# Returns the preferred name or the firstName otherwise
# 
###

def getPreferredName(peep, includeFN = False):
    logger.debug("peep->getPreferredName Entry for " + peep['firstName'])

    if ('preferredName' in peep):
        if includeFN:
            sName = peep['firstName'] + " (" + peep['preferredName'] + ")"
        else:
            sName = peep['preferredName']

    else:
        sName = peep['firstName']

    logger.debug("peep->getPreferredName Exit - returning " + sName)

    return sName

###
# getParentIndex
# id to use: either the father or mother
# returns either the index or None if not found or not a id
###

def getParentIndex(context, peep, parentid):
    if not parentid in peep:
        logger.debug('peep->getParentIndex no id for ' + parentid)
        return ""

    if len(peep[parentid]) != 36:
        logger.debug('peep->getParentIndex id not valid for ' + parentid)
        return ""

    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")
    #peepList = mycontext.getPeeps(context)
    for lookupPeep in peepList:
        if lookupPeep['id'] == peep[parentid]:
            logger.debug('peep->getParentIndex FOUND parent ' + parentid + " its " + lookupPeep['firstName'] + " with id = " + lookupPeep['id'] + ' for ' + peep['firstName'])
            return lookupPeep['id']

    logger.debug('peep->getParentIndex did not find Parent ' + parentid + " for peep " + lookupPeep['firstName'])
    return ""

def fieldOrDefault(peep, fieldName, default=""):
    if fieldName in peep:
        return peep[fieldName]
    return default

###
# produceCSVList
# Dump the JSON list as csv (for excel)
###

def produceCSVList(context):
    logger.info("peep->produceCSVList Entry" )

    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")
    #peepList = mycontext.getPeeps(context)

    logger.info("peep->produceCSVList - peepList has " +  str(len(peepList)) + " peeps in it")

    list = []
    for peep in peepList:
        row = {}

        row['index'] = fieldOrDefault(peep, 'index', "0")
        row['id'] = fieldOrDefault(peep, 'id')
        row['level'] = fieldOrDefault(peep, 'level')
        row['firstName'] = fieldOrDefault(peep, 'firstName')
        row['familyName'] = fieldOrDefault(peep, 'familyName')
        row['preferredName'] = fieldOrDefault(peep, 'preferredName')
        row['dob'] = fieldOrDefault(peep, 'dob')
        row['dod'] = fieldOrDefault(peep, 'dod')
        row['maidenName'] = fieldOrDefault(peep, 'maidenName')
        row['fatherIndex'] = getParentIndex(context, peep, 'fatherid')
        row['motherIndex'] = getParentIndex(context, peep, 'motherid')
             
        list.append(row)

    logger.info("peep->produceCSVList Exit - returning list with " + str(len(list)) + " peeps in it")

    return list

###
# produceDecendentList
# Return a "tree" view from a single ancestor
# returns an array of strings
###

def produceDecendentList(context, id):

    decendentLines = []

    logger.info("peep->produceDecendentList Entry" )
    #peepList = mycontext.getPeeps(context)
    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")

    logger.info("peep->produceDecendentList - peepList has " +  str(len(peepList)) + " peeps in it")

    # first dump the top level parent (find them first)
    line = ""
    for peep in peepList:
        if peep['id'] == id:
            line = peep['firstName']
            break
    decendentLines.append(line)

    lines = processDecendentNode(peepList, id, 1)
    decendentLines += lines

    logger.info("peep->produceDecendentList Exit" )

    return decendentLines

###
# GetRelString
# idTag of peep to lookup
# returns a string
###

def GetRelString(peepList, peep, relName, idTag):

    relString = ""
    if idTag in peep:
        for relPeep in peepList:
            if peep[idTag] == relPeep['id']:
                relString = relName + " " + getPreferredName(relPeep, True) + ";"
                break
            #relPeep = findPeep(p)
    
    return relString

###
# processOtherRels
# Look for other links for this this peep
# returns a string
###

def processOtherRels(peepList, peep):

    retString = GetRelString(peepList, peep, 'father', 'fatherid')
    retString += " " + GetRelString(peepList, peep, 'mother', 'motherid')
    retString += " " + GetRelString(peepList, peep, 'stepfather', 'stepFatherid')

    return retString

###
# processDateDetails
# Process dob/dod
# returns a string (empty if no details)
###

def processDateDetails(peep):
    if 'dob' in peep:
        line = 'DOB - ' + peep['dob'] 
    if 'dod' in peep:
        line += 'DOD - ' + peep['dod'] 
    
    if len(line) > 0:
        return "++ " + line
    return ""

###
# processPartnerDetails
# Process any partner relationships
# returns a string (empty if no details)
###

def processPartnerDetails(peep):
    line = " TBD"

    if len(line) > 0:
        return "++ " + line
    return ""


###
# processParentNode
# Process mother/father
# returns an array of strings
###

def processParentNode(peepList, peep, id, parentidTag, indentLevel):
    indentString = "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
    nodeLines = []

    if not parentidTag in peep:
        return None

    if peep[parentidTag] == id:
        # Decendent
        line = indentString[0:indentLevel] + getPreferredName(peep, True) + " (" + processOtherRels(peepList, peep)  + ")" 
        nodeLines.append(line)
        detailLine = processDateDetails(peep)
        if detailLine != "":
            line = indentString[0:indentLevel] + detailLine         
            nodeLines.append(line)
        detailLine = processPartnerDetails(peep)
        if detailLine != "":
            line = indentString[0:indentLevel] + detailLine         
            nodeLines.append(line)
        moreLines = processDecendentNode(peepList, peep['id'], indentLevel + 1)
        nodeLines += moreLines
        return nodeLines

    return None

def processDecendentNode(peepList, id, indentLevel):

    logger.info("peep->processDecendentNode Entry - level " + str(indentLevel) )
    nodeLines = []

    for peep in peepList:
        # Test for Mother
        moreLines = processParentNode(peepList, peep, id, 'motherid', indentLevel)
        if moreLines != None:
            nodeLines += moreLines

        # Test for Father
        moreLines = processParentNode(peepList, peep, id, 'fatherid', indentLevel)
        if moreLines != None:
            nodeLines += moreLines

    logger.info("peep->processDecendentNode Exit (" + str(len(nodeLines)) + ")" )

    return nodeLines

#########################################################################################################
#########################################################################################################

###
# compareIfExists
# Check the dict item has a value of name and then test if it is the same as value.
# Only return true if present and matches
###

def compareIfExists(item, name, value):
    ret = False
    if name in item:
        if item[name] == value:
            ret = True
    return ret

###
# getPeep
# Return a list of one peep that matches ID  specfied
###

def getPeep(context, id):

    objHandler = mycontext.getObjectHandler()
    aPeep = objHandler.get("People", id)
    #peepList = mycontext.getPeeps(context)

    logger.info("peep->getPeeps - aPeep is " + str(aPeep))

    if not aPeep is None: 
        theList = []
        theList.append(aPeep)

    logger.info("peep->getPeep - returned list has " +  str(len(theList)) + " peeps in it (one expected)")

    return theList


###
# peepSort
# Sort by familyName and firstName
###

def peepSort(dict):
    return dict['familyName'] + "." + dict['firstName']

###
# getPeepsList
# Return one or a list of peeps (as a list)
# Matches ID if specfied
# returns a List of peeps
###

def getPeepsList(context, familyName="", birthSex=""):

    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")
    #peepList = mycontext.getPeeps(context)

    logger.info("peep->getPeepsList - peepList has " +  str(len(peepList)) + " peeps in it")
    logger.info("peep->getPeepsList - familyName = " + familyName + " sex = " + birthSex)
    theList = []
    for peep in peepList:
        # Check for the id first 

        if familyName != "":
            #logger.info("peep->getPeepsList - trying to match familyName = " + familyName + " with peep familyname = " + peep['familyName'])
            if compareIfExists(peep, 'familyName', familyName) or compareIfExists(peep, 'maidenName', familyName):
                if birthSex != "":
                    if peep['birthCertificateSex'] == birthSex:
                        theList.append(peep)
                        continue
                else:   # I.e. FamilyName specfied but not sex. only match of family name in this case.
                    theList.append(peep)
                continue
        else:
            #TODO match on sex only if needed
            #logger.info("Appending the fallthrough")
            theList.append(peep)

    # Sort the key by family name
    if len(theList) > 1:
        theList.sort(key=peepSort)

    logger.info("peep->getPeepsList - returned list has " +  str(len(theList)) + " peeps in it")

    return theList

###
# putPeep
# create or update a peep
# returns the updated peep (e.g. with id if new )
###

def putPeep(context, peep):
    logger.info("peep->putPeep entry")

    # List of fields that can be in a peep
    stdPeep =  ["id", "firstName", "familyName", "otherNames", "maidenName", "level", "motherid", "fatherid", "stepFatherid", "stepMotherid", "dob", "dod", "birthCertificateSex", "version", "notes"]
    result = None

    id = None
    if 'id' in peep:
        id = peep['id']
        if id == "":
            id = None
        else:
            # TODO Check for stale copy
            logger.info("peep->putPeep check for updated blah blah")
  
    if id is None:
        id = str(uuid.uuid4())              # Set the ID
        logger.info("peep->putPeep - NEW PEEP - Id assigned = " + id)
        ver = 0
        targetPeep = {} 
    else:
        # Get the current record
        logger.info("peep->putPeep - EXITING PEEP - Id = " + id)
        targetPeep = getPeep(context, id)[0]
        ver = 0
        if 'version' in targetPeep:
            ver =  int(targetPeep['version'])
        ver += 1

    targetPeep['id'] = id
    targetPeep['version'] = str(ver)               # Assume it's the first

    for fld in stdPeep:
        if fld in peep:
            if (peep[fld] != "Recorded") and (peep[fld] != "Not Recorded") and (peep[fld] != ""): 
                targetPeep[fld] = peep[fld]
    if 'familyName' not in targetPeep:
            targetPeep['familyName'] = "<<NOT DEFINED>>"
    if 'level' not in targetPeep:
            targetPeep['level'] = "3"       # Most likely a baby? ToDo. Maybe can look up parents...
    if 'birthCertificateSex' not in targetPeep:
            targetPeep['birthCertificateSex'] = "<<NOT DEFINED>>"
    if 'birthSex' in peep:
        targetPeep['birthCertificateSex'] = peep['birthSex']

    objHandler = mycontext.getObjectHandler()
    x = objHandler.put(targetPeep, "People", id)
    
    if x == 1:
        #print("fn returned " + str(x))
        result = {'result': 'Success', 'id': id}
    else:
        result = {'result': 'Failed'}

    logger.info("peep->putPeep exit")

    return result
