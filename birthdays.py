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
# isMatchedLevel
# Passed a list of integers or the word "all"
# If the level of the peep (currentLevel) of the peep is in the list to return, return True
# Return True if the string is "All"
# return False otherwise
###

def isMatchedLevel(targetLevel, currentLevel):

    if targetLevel == "*":      # ALL
        return True

    if currentLevel == "<<NOT DEFINED>>":       #TODO Revisit??
        return False        
    
    levelList = targetLevel.split(",")
    for level in levelList:
        if level == currentLevel:
            return True
        # IF the target is "-2", then that means any older will match
        if level == "-2":
            if int(currentLevel) <= -2:
                return True  
    return False

def isIncludePeep(peep, level, allPeeps):
    if 'level' in peep:
        if isMatchedLevel(level, peep['level']) == False:
            # Only include if level in scope
            logger.debug("peep->getBirthdayList - peep not matched level")
            return False
    # If level not known, let them through (TODO - think about)

    logger.debug("peep->getBirthdayList - peep '" + peep['firstName'] + "' is at the correct level")
    # Only include living
    if ('dod' in peep):
        logger.debug("peep->getBirthdayList - peep " +  peep['firstName'] + " has dod" )
        logger.debug("peep->getBirthdayList - all peeps is " + allPeeps.upper() )

        if not((allPeeps.upper() == "TRUE") and validDate(peep, "dod")):
            logger.debug("peep->getBirthdayList - peep skipped as not all peeps and valid date")
            return False
    return True

###
# getBirthdayList
# Returns list of peeps who match the criteria
# level - string containing level to match 
# allPeeps - Include quick and the dead
###

def getBirthdayList(context, level, daysUntil, daysSince, allPeeps):
    logger.info("peep->getBirthdayList Entry - level - " + level + " daysUntil = " + daysUntil + " daysSince = " + daysSince + " allPeeps = " + allPeeps)

    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")
 
    logger.info("peep->getBirthdayList - peepList has " +  str(len(peepList)) + " peeps in it")

    list = []
    today = mycontext.getToday(context)

    logger.debug("peep->getBirthdayList - today is  " +  str(today))

    for peep in peepList:
        logger.debug("peep->getBirthdayList - processing peep " +  peep['firstName'])

        if not validDate(peep, "dob"):
            logger.debug("peep->getBirthdayList - peep skipped as no valid dob")
            continue

        # In theory a peep can be added twice (TODO NEED TO CHECK FOR 365 days)
        dob = datetime.datetime.strptime(peep['dob'], "%Y-%m-%d")
        logger.debug("peep->getBirthdayList - peep (" + peep['firstName'] + ") DOB is  " + str(dob))

        # Check for past birthdays...
        cbd = getClosestBirthday(today, dob, -1 * int(daysSince))
        logger.debug("peep->getBirthdayList - peep " + peep['firstName'] + " closest birthday is  " + str(cbd))
        if cbd is None:
            logger.debug("peep->getBirthdayList - peep " + peep['firstName'] + " does not have a birthday in the past close enough")
        else:
            daysAway = (cbd - today).days
            pastPeep = peep.copy() # Clone the peep
            logger.debug("peep->getBirthdayList (in the past) - days away is  " + str(daysAway) )
            pastPeep['daysAway'] = str(daysAway)
            age = relativedelta(today, dob).years
            pastPeep['age'] = str(age) 
            if isIncludePeep(peep, level, allPeeps):
                logger.debug("peep->getBirthdayList adding peep (past) " + peep['firstName'] )
                addPeepToBirthdayList(list, pastPeep)

        # Check for future birthdays...
        cbd = getClosestBirthday(today, dob, int(daysUntil))
        logger.debug("peep->getBirthdayList - peep " + peep['firstName'] + " closest birthday is  " + str(cbd))
        if cbd is None:
            logger.debug("peep->getBirthdayList - peep " + peep['firstName'] + " does not have a birthday in the future close enough")
        else:
            daysAway = (cbd - today).days
            futurePeep = peep.copy() # Clone the peep
            logger.debug("peep->getBirthdayList (in the future) - days away is  " + str(daysAway) )
            futurePeep['daysAway'] = str(daysAway)
            age = relativedelta(today, dob).years
            if daysAway == 0:   
                futurePeep['age'] = str(age) 
            else:
                futurePeep['age'] = str(age + 1) 
            if isIncludePeep(peep, level, allPeeps) or daysAway == 0:   # Always include birthday peeps
                logger.debug("peep->getBirthdayList adding peep (future) " + peep['firstName'] )
                addPeepToBirthdayList(list, futurePeep)

    logger.info("peep-> getBirthdayList Exit - returning " + str(len(list)) + " birthday events")

    return list

###
# addPeepToBirthdayList
# Insert the peep at the appropriate place in the list
# 
###

def addPeepToBirthdayList(list, peep):
    logger.debug("peep->addPeepToBirthdayList Entry for " + peep['firstName'] + " List has " + str(len(list)) + " items") 

    if len(list) == 0:
        list.append(peep)
    else:
        index = 0
        inserted = False
        for item in list:
            if int(peep['daysAway']) < int(item['daysAway']):
                list.insert(index, peep)
                inserted = True
                break
            index += 1
        if inserted == False:
            list.append(peep)

    logger.debug("peep->addPeepToBirthdayList Exit - list has  " + str(len(list)) + " items")

    return

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
# getClosestBirthday
# Returns a date for the closest birtday, either last year, this year or next year that is within the
# range specified.
# currentDate - Date type
# dob - Date Type
# rangeDays - integer - number of days into the future to filter (+ve) or in the past (-ve)
###

def getClosestBirthday(currentDate, dob, rangeDays):

    thisYearsBD = datetime.date(currentDate.year, dob.month, dob.day)
    lastYearsBD = datetime.date(currentDate.year - 1, dob.month, dob.day)
    nextYearsBD = datetime.date(currentDate.year + 1, dob.month, dob.day)

    diffLY = (lastYearsBD - currentDate).days
    diffTY = (thisYearsBD - currentDate).days
    diffNY = (nextYearsBD - currentDate).days

    logger.debug("peep->getClosestBirthday Last Years = " + str(diffLY))
    logger.debug("peep->getClosestBirthday This Years = " + str(diffTY))
    logger.debug("peep->getClosestBirthday Next Years = " + str(diffNY))

    if rangeDays < 0:
        logger.debug("peep->getClosestBirthday Checking for birthdays past")
        # looking for the previous birthday
        if (diffTY < 0) and (abs(diffTY) < abs(rangeDays)):
            # This years birthday is within range
            logger.debug("peep->getClosestBirthday This Years birthday was within range")
            return(thisYearsBD)

        if (abs(diffLY) < abs(rangeDays)):
            # Last years birthday is within range
            return(lastYearsBD)
    else:
        logger.debug("peep->getClosestBirthday Checking for birthdays future (or today)")
        # looking for the next birthday
        if (diffTY >= 0) and (diffTY <= rangeDays):
            logger.debug("peep->getClosestBirthday This Years birthday was within range (future)")
            return(thisYearsBD)

        if (diffNY <= rangeDays):
            # Next years birthday is within range
            return(nextYearsBD)
    
    logger.debug("peep->getClosestBirthday No birthdays within range")    
    return None

###
# validDate
# Check that the name dict item is a valid date
# Use for DOB or DOD
# Missing is considered invalid
# Date must be of form yyyy-mm-dd
###

def validDate(peep, field):
    if not field in peep:
        return False
    
    if len(peep[field]) != 10:
        return False
    
    # This will do for now...

    return True

###
# getParentIndex
# guid to use: either the father or mother
# returns either the index or None if not found or not a guid
###

def getParentIndex(context, peep, parentGuid):
    if not parentGuid in peep:
        logger.debug('peep->getParentIndex no guid for ' + parentGuid)
        return ""

    if len(peep[parentGuid]) != 36:
        logger.debug('peep->getParentIndex guid not valid for ' + parentGuid)
        return ""

    objHandler = mycontext.getObjectHandler()
    peepList = objHandler.getList("People")
    #peepList = mycontext.getPeeps(context)
    for lookupPeep in peepList:
        if lookupPeep['id'] == peep[parentGuid]:
            logger.debug('peep->getParentIndex FOUND parent ' + parentGuid + " its " + lookupPeep['firstName'] + " with id = " + lookupPeep['index'] + ' for ' + peep['firstName'])
            return lookupPeep['index']

    logger.debug('peep->getParentIndex did not find Parent ' + parentGuid + " for peep " + lookupPeep['firstName'])
    return ""

def fieldOrDefault(peep, fieldName):
    if fieldName in peep:
        return peep[fieldName]
    return ""

###
# getTodaysBirthdays
# returns a pre-canned empty string or a comman based string list
###

def getTodaysBirthdays(context):
    logger.info("peep->getTodaysBirthdays Entry")

    list = []

    # Get the birthday list, don't match the level, want all
    list = getBirthdayList(context, "", "0", "0", "False")

    if len(list) == 0:
        retString = "None"
    else:
        retString = ""
        index = 0
        for val in list:
            retString += getPreferredName(val, False)
            index += 1
            if index != len(list):               
                if index == len(list) - 1:
                    retString += " and "
                else:
                    retString += ", "

    logger.info(f'peep->getTodaysBirthdays Exit - {retString}')

    return retString
