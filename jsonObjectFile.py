import logging
import json
import datetime
import time

import MyAPIException       

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('jsonObjectFile: initialisation starting...')

def getList(thingy, altkey=None):
    logger.info("jsonObjectFile->getList for thingy = " + thingy + " where altkey = " + str(altkey))
    data = None
    try:
        objFileName = "hoh-" + thingy + ".json"
        logger.info("jsonObjectFile->getList objFileName = " + objFileName)
        with open(objFileName) as json_file:
            data = json.load(json_file)
            json_file.close()
    except Exception as ex:
        errMsg = str(ex)
        logger.error("jsonObjectFile->getList exception = [" + errMsg + "]") 
        raise MyAPIException.MyAPIException("404", "Resource not found (" + errMsg + ")")

    logger.info("jsonObjectFile->getList returned a list of " + str(len(data)) + " " + thingy)
    logger.debug("jsonObjectFile->getList returned a list = " + str(data))
    return data


def get(thingy, id):
    logger.info("jsonObjectFile->get for thingy = " + thingy + " where id = " + str(id))
    list = getList(thingy)
    val = None
    for x in list:
        logger.info("jsonObjectFile->get item = " + str(x))
        if x["id"] == id:
            val = x
            break
    
    if val is None:
        logger.info("jsonObjectFile->get match failed for id = " + str(id))
        raise MyAPIException.MyAPIException("404", "Item with Id '" + str(id) + "' of resource '" + thingy + "' not found")

    logger.info("jsonObjectFile->get returned a val = " + str(val))


    return val

def put(obj, thingy, id=None):
    logger.info("jsonObjectFile->put for thingy = " + thingy + " where id = " + str(id))

    list = getList(thingy)
    i = 0
    for x in list:
        if x["id"] == id:
            # Simulate an update by deleting the old one.
            logger.info("jsonObjectFile->put - deleting index " + str(i))
            del list[i]
            break
        i += 1

    # Put a timestamp
    epoch = str(int(time.time()))
    obj['updatedEpoch'] = epoch
    
    list.append(obj)

    try:
        objFileName = "hoh-" + thingy + ".json"
        with open(objFileName, "w") as json_file:
            json.dump(list, json_file, indent=4)
            json_file.close()
    except MyAPIException.MyAPIException as mx:
        logger.error("jsonObjectFile->put - MyException " + str(mx))
    except Exception as ex:
        logger.error("jsonObjectFile->put - General Exception " + str(ex))
    finally:
        logger.info("jsonObjectFile->put - Finally")

    logger.info("jsonObjectFile->put exit")
    return 1
