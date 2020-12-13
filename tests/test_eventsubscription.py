from __future__ import annotations
from typing import TYPE_CHECKING, List, Set, Dict, Tuple, Union, Any, Optional, NewType, Callable


import openhab
import openhab.events
import time
import openhab.items as items
import logging
import json
import random
import tests.testutil as testutil
log=logging.getLogger()
logging.basicConfig(level=10,format="%(levelno)s:%(asctime)s - %(message)s - %(name)s - PID:%(process)d - THREADID:%(thread)d - %(levelname)s - MODULE:%(module)s, -FN:%(filename)s -FUNC:%(funcName)s:%(lineno)d")

log.error("xx")
log.warning("www")
log.info("iii")
log.debug("ddddd")



base_url = 'http://10.10.20.81:8080/rest'



testdata:Dict[str,Tuple[str,str,str]]={'OnOff'           : ('ItemCommandEvent','testroom1_LampOnOff','{"type":"OnOff","value":"ON"}'),
                                   'Decimal'         : ('ItemCommandEvent','xx','{"type":"Decimal","value":"170.0"}'),
                                   'DateTime'        : ('ItemCommandEvent','xx','{"type":"DateTime","value":"2020-12-04T15:53:33.968+0100"}'),
                                   'UnDef'           : ('ItemCommandEvent','xx','{"type":"UnDef","value":"UNDEF"}'),
                                   'String'          : ('ItemCommandEvent','xx','{"type":"String","value":"WANING_GIBBOUS"}'),
                                   'Quantitykm'      : ('ItemCommandEvent','xx','{"type":"Quantity","value":"389073.99674024084 km"}'),
                                   'Quantitykm grad' : ('ItemCommandEvent','xx', '{"type":"Quantity","value":"233.32567712620255 °"}'),
                                   'Quantitywm2'     : ('ItemCommandEvent','xx', '{"type":"Quantity","value":"0.0 W/m²"}'),
                                   'Percent'         : ('ItemCommandEvent','xx', '{"type":"Percent","value":"52"}'),
                                   'UpDown'          : ('ItemCommandEvent','xx', '{"type":"UpDown","value":"DOWN"}'),


                                   'OnOffChange'                   : ('ItemStateChangedEvent','xx', '{"type":"OnOff","value":"OFF","oldType":"OnOff","oldValueRaw":"ON"}'),
                                   'DecimalChange'                 : ('ItemStateChangedEvent','xx', '{"type":"Decimal","value":"170.0","oldType":"Decimal","oldValueRaw":"186.0"}'),
                                   'QuantityChange'                : ('ItemStateChangedEvent','xx', '{"type":"Quantity","value":"389073.99674024084 km","oldType":"Quantity","oldValueRaw":"389076.56223012594 km"}'),
                                   'QuantityGradChange'            : ('ItemStateChangedEvent','xx', '{"type":"Quantity","value":"233.32567712620255 °","oldType":"Quantity","oldValueRaw":"233.1365666436372 °"}'),
                                   'DecimalChangeFromNull'         : ('ItemStateChangedEvent','xx', '{"type":"Decimal","value":"0.5","oldType":"UnDef","oldValueRaw":"NULL"}'),
                                   'DecimalChangeFromNullToUNDEF'  : ('ItemStateChangedEvent','xx', '{"type":"Decimal","value":"15","oldType":"UnDef","oldValueRaw":"NULL"}'),
                                   'PercentChange'                 : ('ItemStateChangedEvent','xx', '{"type":"Percent","value":"52","oldType":"UnDef","oldValueRaw":"NULL"}'),


                                   # 'XXX': ('ItemStateChangedEvent', 'XXXXXXXXXX'),
                                   'Datatypechange'                : ('ItemStateChangedEvent','xx', '{"type":"OnOff","value":"ON","oldType":"UnDef","oldValueRaw":"NULL"}')
                                   }
testitems:Dict[str,openhab.items.Item] = {}

def executeParseCheck():
    for testkey in testdata:
        log.info("testing:{}".format(testkey))
        stringToParse=testdata[testkey]










myopenhab = openhab.OpenHAB(base_url,autoUpdate=False)



if False:
    myopenhab = openhab.OpenHAB(base_url, autoUpdate=False)

    testprefix="x1"
    itemname="{}CreateItemTest".format(testprefix)
    itemQuantityType="Angle" # "Length",Temperature,,Pressure,Speed,Intensity,Dimensionless,Angle
    itemtype="Number"

    labeltext="das ist eine testzahl:"
    itemlabel="[{labeltext}%.1f °]".format(labeltext=labeltext)
    itemcategory="{}TestCategory".format(testprefix)
    itemtags:List[str]=["{}testtag1".format(testprefix),"{}testtag2".format(testprefix)]
    itemgroupNames:List[str]=["{}testgroup1".format(testprefix),"{}testgroup2".format(testprefix)]
    grouptype= "{}testgrouptype".format(testprefix)
    functionname="{}testfunctionname".format(testprefix)
    functionparams:List[str]=["{}testfunctionnameParam1".format(testprefix),"{}testfunctionnameParam2".format(testprefix),"{}testfunctionnameParam3".format(testprefix)]



    #paramdict:Dict[str,Union[str,List[str],Dict[str,Union[str,List]]]]={}

    if itemQuantityType is None:
        paramdict["type"]=itemtype
    else:
        paramdict["type"] = "{}:{}".format(itemtype,itemQuantityType)

    paramdict["name"]=itemname

    if not itemlabel is None:
        paramdict["label"]=itemlabel

    if not itemcategory is None:
        paramdict["category"] = itemcategory

    if not itemtags is None:
        paramdict["tags"] = itemtags

    if not itemgroupNames is None:
        paramdict["groupNames"] = itemgroupNames

    if not grouptype is None:
        paramdict["groupType"] = grouptype

    if not functionname is None:
        paramdict["function"] = {"name":functionname,"params":functionparams}


    jsonBody=json.dumps(paramdict)
    print(jsonBody)
    myopenhab.req_json_put('/items/{}'.format(itemname), jsonData=jsonBody)
if False:
    myopenhab = openhab.OpenHAB(base_url,autoUpdate=True)

    itemDimmer=myopenhab.get_item("testroom1_LampDimmer")
    print(itemDimmer)
    itemAzimuth=myopenhab.get_item("testworld_Azimuth")
    print(itemAzimuth)
    itemAzimuth.state=44.0
    itemClock=myopenhab.get_item("myClock")

    expectClock = None
    expectedValue=None


    def onAzimuthChange(item:openhab.items.Item ,event:openhab.events.ItemStateEvent):
        log.info("########################### UPDATE of {itemname} to eventvalue:{eventvalue}(event value raraw:{eventvalueraw}) (itemstate:{itemstate},item_state:{item_state}) from OPENHAB ONLY".format(
            itemname=event.itemname,eventvalue=event.newValue,eventvalueraw=event.newValueRaw, item_state=item._state,itemstate=item.state))

    itemAzimuth.addEventListener(openhab.events.ItemCommandEventType,onAzimuthChange,onlyIfEventsourceIsOpenhab=True)

    def onClockChange(item:openhab.items.Item ,event:openhab.events.ItemStateEvent):
        log.info("########################### UPDATE of {} to {} (itemsvalue:{}) from OPENHAB ONLY".format(event.itemname, event.newValueRaw, item.state))
        if not expectClock is None:
            assert item.state == expectClock

    itemClock.addEventListener(openhab.events.ItemCommandEventType,onClockChange,onlyIfEventsourceIsOpenhab=True)


    def onAzimuthChangeAll(item:openhab.items.Item ,event:openhab.events.ItemStateEvent):
        if event.source == openhab.events.EventSourceInternal:
            log.info("########################### INTERNAL UPDATE of {} to {} (itemsvalue:{}) from internal".format(event.itemname,event.newValueRaw, item.state))
        else:
            log.info("########################### EXTERNAL UPDATE of {} to {} (itemsvalue:{}) from OPENHAB".format(event.itemname, event.newValueRaw, item.state))

    itemAzimuth.addEventListener(openhab.events.ItemCommandEventType,onAzimuthChangeAll,onlyIfEventsourceIsOpenhab=False)

    #print(itemClock)

    time.sleep(2)
    log.info("###################################### starting test 'internal Event'")

    expectClock=2
    itemClock.state=2
    time.sleep(0.1)
    expectClock = None
    testname="OnOff"
    log.info("###################################### starting test '{}'".format(testname))

    def createEventData(type,itemname,payload):
        result={}
        result["type"]=type
        result["topic"]="smarthome/items/{itemname}/state".format(itemname=itemname)
        result["payload"]=payload
        return result


    def onLight_switchCommand(item: openhab.items.Item, event: openhab.events.ItemCommandEvent):
        log.info("########################### COMMAND of {} to {} (itemsvalue:{}) from OPENHAB".format(event.itemname, event.newValueRaw, item.state))

    def onAnyItemCommand(item: openhab.items.Item, event: openhab.events.ItemStateEvent):
        log.info("########################### UPDATE of {} to {} (itemsvalue:{}) from OPENHAB ONLY".format(event.itemname, event.newValueRaw, item.state))
        if not expectedValue is None:
            actualValue=event.newValue
            assert actualValue==expectedValue, "expected value to be {}, but it was {}".format(expectedValue,actualValue)


    testname="OnOff"
    expectedValue="ON"
    type='ItemCommandEvent'
    itemname='testroom1_LampOnOff'
    payload='{"type":"OnOff","value":"ON"}'
    eventData=createEventData(type,itemname,payload)
    testroom1_LampOnOff:openhab.items.SwitchItem = myopenhab.get_item(itemname)
    testroom1_LampOnOff.off()
    time.sleep(0.5)
    testroom1_LampOnOff.addEventListener(types=openhab.events.ItemCommandEventType,listener=onAnyItemCommand,onlyIfEventsourceIsOpenhab=False)
    testroom1_LampOnOff.addEventListener(types=openhab.events.ItemCommandEventType, listener=onLight_switchCommand, onlyIfEventsourceIsOpenhab=False)
    # testroom1_LampOnOff=None
    myopenhab._parseEvent(eventData)


    #itemDimmer = myopenhab.get_item("testroom1_LampDimmer")








    #myopenhab.parseEvent(testdata[testname])
    t=0
    while True:
        time.sleep(10)
        t=t+1
        x=0

        if x==1:
            itemAzimuth=None
        elif x==2:
            azimuthvalue= 55.1 + t
            log.info("-------------------------setting azimuth to {}".format(azimuthvalue))
            itemAzimuth.command(azimuthvalue)
            log.info("-------------------------did set azimuth to {}".format(itemAzimuth.state))
            #we receive an update from openhab immediately.