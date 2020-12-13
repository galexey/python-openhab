# -*- coding: utf-8 -*-
"""python library for accessing the openHAB REST API."""

#
# Georges Toth (c) 2016-present <georges@trypill.org>
#
# python-openhab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-openhab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openhab.  If not, see <http://www.gnu.org/licenses/>.
#

# pylint: disable=bad-indentation


from __future__ import annotations
import logging
import inspect
import re
import typing
import json
import time
import dateutil.parser

import openhab.types
import openhab.events
from datetime import datetime, timedelta

__author__ = 'Georges Toth <georges@trypill.org>'
__license__ = 'AGPLv3+'

class ItemFactory:
  """A factory to get an Item from Openhab, create new or delete existing items in openHAB"""

  def __init__(self,openhabClient:openhab.client.OpenHAB):
    """Constructor.

        Args:
          openhab_conn (openhab.OpenHAB): openHAB object.

        """
    self.openHABClient=openhabClient

  def createOrUpdateItem(self,
                         name: str,
                         type: typing.Union[str, typing.Type[Item]],
                         quantityType: typing.Optional[str] = None,
                         label: typing.Optional[str] = None,
                         category: typing.Optional[str] = None,
                         tags: typing.Optional[typing.List[str]] = None,
                         groupNames: typing.Optional[typing.List[str]] = None,
                         grouptype: typing.Optional[str] = None,
                         functionname: typing.Optional[str] = None,
                         functionparams: typing.Optional[typing.List[str]] = None
                         ) -> Item:
    """creates a new item in openhab if there is no item with name 'name' yet.
    if there is an item with 'name' already in openhab, the item gets updated with the infos provided. be aware that not provided fields will be deleted in openhab.
    consider to get the existing item via 'getItem' and then read out existing fields to populate the parameters here.

    This function blocks until the item is created.


        Args:
          name (str): unique name of the item
          type ( str or any Itemclass): the type used in openhab (like Group, Number, Contact, DateTime, Rollershutter, Color, Dimmer, Switch, Player)
                           server.
                           To create groups use the itemtype 'Group'!
          quantityType (str): optional quantityType ( like Angle, Temperature, Illuminance (see https://www.openhab.org/docs/concepts/units-of-measurement.html))
          label (str): optional openhab label (see https://www.openhab.org/docs/configuration/items.html#label)
          category (str): optional category. no documentation found
          tags (List of str): optional list of tags (see https://www.openhab.org/docs/configuration/items.html#tags)
          groupNames (List of str): optional list of groups this item belongs to.
          grouptype (str): optional grouptype. no documentation found
          functionname (str): optional functionname. no documentation found
          functionparams (List of str): optional list of function Params. no documentation found

        Returns:
          the created Item
        """

    self.createOrUpdateItemAsync(name=name,
                                 type=type,
                                 quantityType=quantityType,
                                 label=label,
                                 category=category,
                                 tags=tags,
                                 groupNames=groupNames,
                                 grouptype=grouptype,
                                 functionname=functionname,
                                 functionparams=functionparams)



    time.sleep(0.05)
    result = None
    retrycounter = 10
    while True:
      try:
        result = self.getItem(name)
        return result
      except Exception as e:
        retrycounter -= 1
        if retrycounter < 0:
          raise e
        else:
          time.sleep(0.05)



  def createOrUpdateItemAsync(self,
                              name:str,
                              type:typing.Union[str, typing.Type[Item]],
                              quantityType:typing.Optional[str]=None,
                              label:typing.Optional[str]=None,
                              category:typing.Optional[str]=None,
                              tags: typing.Optional[typing.List[str]]=None,
                              groupNames: typing.Optional[typing.List[str]]=None,
                              grouptype:typing.Optional[str]=None,
                              functionname:typing.Optional[str]=None,
                              functionparams: typing.Optional[typing.List[str]]=None
                              )->None:
    """creates a new item in openhab if there is no item with name 'name' yet.
      if there is an item with 'name' already in openhab, the item gets updated with the infos provided. be aware that not provided fields will be deleted in openhab.
      consider to get the existing item via 'getItem' and then read out existing fields to populate the parameters here.

      This function does not wait for openhab to create the item. Use this function if you need to create many items quickly.


          Args:
            name (str): unique name of the item
            type ( str or any Itemclass): the type used in openhab (like Group, Number, Contact, DateTime, Rollershutter, Color, Dimmer, Switch, Player)
                             server.
                             To create groups use the itemtype 'Group'!
            quantityType (str): optional quantityType ( like Angle, Temperature, Illuminance (see https://www.openhab.org/docs/concepts/units-of-measurement.html))
            label (str): optional openhab label (see https://www.openhab.org/docs/configuration/items.html#label)
            category (str): optional category. no documentation found
            tags (List of str): optional list of tags (see https://www.openhab.org/docs/configuration/items.html#tags)
            groupNames (List of str): optional list of groups this item belongs to.
            grouptype (str): optional grouptype. no documentation found
            functionname (str): optional functionname. no documentation found
            functionparams (List of str): optional list of function Params. no documentation found


          """
    paramdict: typing.Dict[str, typing.Union[str, typing.List[str], typing.Dict[str, typing.Union[str, typing.List]]]] = {}

    if isinstance(type, str):
      itemtypename=type
    elif inspect.isclass(type):
      if issubclass(type, Item):
        itemtypename=type.TYPENAME
    if quantityType is None:
        paramdict["type"]=itemtypename
    else:
        paramdict["type"] = "{}:{}".format(itemtypename, quantityType)

    paramdict["name"]=name

    if not label is None:
        paramdict["label"]=label

    if not category is None:
        paramdict["category"] = category

    if not tags is None:
        paramdict["tags"] = tags

    if not groupNames is None:
        paramdict["groupNames"] = groupNames

    if not grouptype is None:
        paramdict["groupType"] = grouptype

    if not functionname is None and not functionparams is None:
        paramdict["function"] = {"name":functionname,"params":functionparams}


    jsonBody=json.dumps(paramdict)
    logging.getLogger().debug("about to create item with PUT request:{}".format(jsonBody))
    self.openHABClient.req_json_put('/items/{}'.format(name), jsonData=jsonBody)


  def getItem(self,itemname):
    return self.openHABClient.get_item(itemname)


class Item:
  """Base item class."""

  types = []  # type: typing.List[typing.Type[openhab.types.CommandType]]
  TYPENAME = "unknown"

  def __init__(self, openhab_conn: 'openhab.client.OpenHAB', json_data: dict, auto_update:typing.Optional[bool]=True) -> None:
    """Constructor.

    Args:
      openhab_conn (openhab.OpenHAB): openHAB object.
      json_data (dic): A dict converted from the JSON data returned by the openHAB
                       server.
    """
    self.openhab = openhab_conn
    self.autoUpdate = auto_update
    self.type_ = None
    self.quantityType = None
    self._unitOfMeasure = ""
    self.group = False
    self.name = ''
    self._state = None  # type: typing.Optional[typing.Any]
    self._raw_state = None  # type: typing.Optional[typing.Any]  # raw state as returned by the server
    self._raw_state_event = None # type: typing.str  # raw state as received from Serverevent
    self._members = {}  # type: typing.Dict[str, typing.Any] #  group members (key = item name), for none-group items it's empty

    self.logger = logging.getLogger(__name__)

    self.init_from_json(json_data)
    self.lastCommandSent = datetime.fromtimestamp(0)
    self.lastUpdateSent = datetime.fromtimestamp(0)

    self.openhab.register_item(self)
    self.eventListeners: typing.Dict[typing.Callable[[openhab.events.ItemEvent],None],Item.EventListener]={}
    #typing.List[typing.Callable] = []






  def init_from_json(self, json_data: dict):
    """Initialize this object from a json configuration as fetched from openHAB.

    Args:
      json_data (dict): A dict converted from the JSON data returned by the openHAB
                        server.
    """
    self.name = json_data['name']
    if json_data['type'] == 'Group':
      self.group = True
      if 'groupType' in json_data:
        self.type_ = json_data['groupType']

      # init members
      for i in json_data['members']:
        self.members[i['name']] = self.openhab.json_to_item(i)

    else:
      self.type_ = json_data['type']
      parts=self.type_.split(":")
      if len(parts)==2:
        self.quantityType=parts[1]
    if "editable" in json_data:
      self.editable=json_data['editable']
    if "label" in json_data:
      self.label=json_data['label']
    if "category" in json_data:
      self.category=json_data['category']
    if "tags" in json_data:
      self.tags=json_data['tags']
    if "groupNames" in json_data:
      self.groupNames=json_data['groupNames']

    self.__set_state(json_data['state'])

  @property
  def state(self,fetchFromOpenhab=False) -> typing.Any:
    """The state property represents the current state of the item.

    The state is automatically refreshed from openHAB on reading it.
    Updating the value via this property send an update to the event bus.
    """
    if not self.autoUpdate or fetchFromOpenhab:
      json_data = self.openhab.get_item_raw(self.name)
      self.init_from_json(json_data)

    return self._state

  @state.setter
  def state(self, value: typing.Any):
    self.update(value)


  @property
  def members(self):
    """If item is a type of Group, it will return all member items for this group.

    For none group item empty dictionary will be returned.

    Returns:
      dict: Returns a dict with item names as key and `Item` class instances as value.

    """
    return self._members

  def _validate_value(self, value: typing.Union[str, typing.Type[openhab.types.CommandType]]):
    """Private method for verifying the new value before modifying the state of the item."""
    if self.type_ == 'String':
      if not isinstance(value, (str, bytes)):
        raise ValueError()
    elif self.types:
      validation = False

      for type_ in self.types:
        try:
          type_.validate(value)
        except ValueError:
          pass
        else:
          validation = True

      if not validation:
        raise ValueError('Invalid value "{}"'.format(value))
    else:
      raise ValueError()

  def _parse_rest(self, value: str) -> str:
    """Parse a REST result into a native object."""
    return (value,"")

  def _rest_format(self, value: str) -> typing.Union[str, bytes]:
    """Format a value before submitting to openHAB."""
    _value = value  # type: typing.Union[str, bytes]

    # Only latin-1 encoding is supported by default. If non-latin-1 characters were provided, convert them to bytes.
    try:
      _ = value.encode('latin-1')
    except UnicodeError:
      _value = value.encode('utf-8')

    return _value

  def _isMyOwnChange(self, event):
    """find out if the incoming event is actually just a echo of my previous command or change"""
    now = datetime.now()
    self.logger.debug("_isMyOwnChange:event.source:{}, event.type{}, self._state:{}, event.newValue:{},self.lastCommandSent:{}, self.lastUpdateSent:{} , now:{}".format(event.source,event.type,self._state,event.newValue ,self.lastCommandSent,self.lastUpdateSent,now))
    if event.source == openhab.events.EventSourceOpenhab:
      if event.type in [openhab.events.ItemCommandEventType, openhab.events.ItemStateChangedEventType, openhab.events.ItemStateEventType]:
        if self._state == event.newValue:
          if max(self.lastCommandSent, self.lastUpdateSent) + timedelta(milliseconds=self.openhab.maxEchoToOpenhabMS) > now:
            # this is the echo of the command we just sent to openHAB.
            return True
      return False
    else:
      return True

  def delete(self):
    """deletes the item from openhab """
    self.openhab.req_del('/items/{}'.format(self.name))
    self._state=None
    self.removeAllEventListener()


  def _processExternalEvent(self, event:openhab.events.ItemEvent):
    if not self.autoUpdate: return
    self.logger.info("processing external event")
    newValue,uom=self._parse_rest(event.newValueRaw)
    event.newValue=newValue
    event.unitOfMeasure=uom
    if event.type==openhab.events.ItemStateChangedEventType:
      try:
        oldValue,ouom=self._parse_rest(event.oldValueRaw)
      except:
        event.oldValue=None
        event.oldUnitOfMeasure=None
    isMyOwnChange=self._isMyOwnChange(event)
    self.logger.info("external event:{}".format(event))
    if not isMyOwnChange:
      self.__set_state(value=event.newValueRaw)
      event.newValue=self._state
    for aListener in self.eventListeners.values():
      if event.type in aListener.listeningTypes:
        if not isMyOwnChange or (isMyOwnChange and aListener.alsoGetMyEchosFromOpenHAB):
          try:
            aListener.callbackfunction(self,event)
          except Exception as e:
            self.logger.error("error executing Eventlistener for item:{}.".format(event.itemname),e)

  def _processInternalEvent(self,event:openhab.events.ItemEvent):
    self.logger.info("processing internal event")
    for aListener in self.eventListeners.values():
      if event.type in aListener.listeningTypes:
        if aListener.onlyIfEventsourceIsOpenhab:
          continue
        else:
          try:
            aListener.callbackfunction(self,event)
          except Exception as e:
              self.logger.error("error executing Eventlistener for item:{}.".format(event.itemname),e)


  class EventListener(object):
    """EventListener Objects hold data about a registered event listener"""
    def __init__(self,listeningTypes:typing.Set[openhab.events.EventType],listener:typing.Callable[[openhab.events.ItemEvent],None],onlyIfEventsourceIsOpenhab,alsoGetMyEchosFromOpenHAB):
      """Constructor of an EventListener Object
        Args:
          listeningTypes (openhab.events.EventType or set of openhab.events.EventType): the eventTypes the listener is interested in.
          onlyIfEventsourceIsOpenhab (bool): the listener only wants events that are coming from openhab.
          alsoGetMyEchosFromOpenHAB (bool): the listener also wants to receive events coming from openhab that originally were triggered by commands or changes by our item itself.


      """
      allTypes = {openhab.events.ItemStateEvent.type, openhab.events.ItemCommandEvent.type, openhab.events.ItemStateChangedEvent.type}
      if listeningTypes is None:
        self.listeningTypes = allTypes
      elif not hasattr(listeningTypes, '__iter__'):
        self.listeningTypes = set([listeningTypes])
      elif not listeningTypes:
        self.listeningTypes = allTypes
      else:
        self.listeningTypes = listeningTypes

      self.callbackfunction:typing.Callable[[openhab.events.ItemEvent],None]=listener
      self.onlyIfEventsourceIsOpenhab = onlyIfEventsourceIsOpenhab
      self.alsoGetMyEchosFromOpenHAB=alsoGetMyEchosFromOpenHAB

    def addTypes(self,listeningTypes:typing.Set[openhab.events.EventType]):
      """add aditional listening types
              Args:
                listeningTypes (openhab.events.EventType or set of openhab.events.EventType): the additional eventTypes the listener is interested in.

            """
      if listeningTypes is None: return
      elif not hasattr(listeningTypes, '__iter__'):
        self.listeningTypes.add(listeningTypes)
      elif not listeningTypes:
        return
      else:
        self.listeningTypes.update(listeningTypes)

    def removeTypes(self,listeningTypes:typing.Set[openhab.events.EventType]):
      """remove listening types
          Args:
            listeningTypes (openhab.events.EventType or set of openhab.events.EventType): the eventTypes the listener is not interested in anymore

        """
      if listeningTypes is None:
        self.listeningTypes.clear()
      elif not hasattr(listeningTypes, '__iter__'):
        self.listeningTypes.remove(listeningTypes)
      elif not listeningTypes:
        self.listeningTypes.clear()
      else:
        self.listeningTypes.difference_update(listeningTypes)






  def addEventListener(self,listeningTypes:typing.Set[openhab.events.EventType],listener:typing.Callable[[openhab.items.Item,openhab.events.ItemEvent],None],onlyIfEventsourceIsOpenhab=True,alsoGetMyEchosFromOpenHAB=False):
    """add a Listener interested in changes of items happening in openhab
        Args:
          Args:
          listeningTypes (openhab.events.EventType or set of openhab.events.EventType): the eventTypes the listener is interested in.
          listener (Callable[[openhab.items.Item,openhab.events.ItemEvent],None]: a method with 2 parameters:
            item (openhab.items.Item): the item that received a command, change or update
            event (openhab.events.ItemEvent): the item Event holding the actual change
          onlyIfEventsourceIsOpenhab (bool): the listener only wants events that are coming from openhab.
          alsoGetMyEchosFromOpenHAB (bool): the listener also wants to receive events coming from openhab that originally were triggered by commands or changes by our item itself.


      """

    if listener in self.eventListeners:
      eventListener= self.eventListeners[listener]
      eventListener.addTypes(listeningTypes)
      eventListener.onlyIfEventsourceIsOpenhab=onlyIfEventsourceIsOpenhab
    else:
      eventListener=Item.EventListener(listeningTypes=listeningTypes,listener=listener,onlyIfEventsourceIsOpenhab=onlyIfEventsourceIsOpenhab,alsoGetMyEchosFromOpenHAB=alsoGetMyEchosFromOpenHAB)
      self.eventListeners[listener]=eventListener

  def removeAllEventListener(self):
    self.eventListeners=[]

  def removeEventListener(self,types:typing.List[openhab.events.EventType],listener:typing.Callable[[openhab.events.ItemEvent],None]):
    """removes a previously registered Listener interested in changes of items happening in openhab
            Args:
              Args:
              listeningTypes (openhab.events.EventType or set of openhab.events.EventType): the eventTypes the listener is interested in.
              listener: the previously registered listener method.


          """
    if listener in self.eventListeners:
      eventListener = self.eventListeners[listener]
      eventListener.removeTypes(types)
      if not eventListener.listeningTypes:
        self.eventListeners.pop(listener)





  def __set_state(self, value: str) -> None:
    """Private method for setting the internal state."""
    self._raw_state = value

    if value in ('UNDEF', 'NULL'):
      self._state = None
    else:
      self._state, self._unitOfMeasure = self._parse_rest(value)

  def __str__(self) -> str:
    return '<{0} - {1} : {2}>'.format(self.type_, self.name, self._state)

  def _update(self, value: typing.Any) -> None:
    """Updates the state of an item, input validation is expected to be already done.

    Args:
      value (object): The value to update the item with. The type of the value depends
                      on the item type and is checked accordingly.
    """
    # noinspection PyTypeChecker
    self.lastCommandSent = datetime.now()
    self.openhab.req_put('/items/{}/state'.format(self.name), data=value)


  def update(self, value: typing.Any) -> None:
    """Updates the state of an item.

    Args:
      value (object): The value to update the item with. The type of the value depends
                      on the item type and is checked accordingly.
    """
    oldstate = self._state
    self._validate_value(value)

    v = self._rest_format(value)
    self._state=value
    self._update(v)

    if oldstate == self._state:
      event = openhab.events.ItemStateEvent(itemname=self.name,source=openhab.events.EventSourceInternal, remoteDatatype=self.type_, newValue=self._state, newValueRaw=None, unitOfMeasure=self._unitOfMeasure, asUpdate=True)
    else:
      event = openhab.events.ItemStateChangedEvent(itemname=self.name,
                                                   source=openhab.events.EventSourceInternal,
                                                   remoteDatatype=self.type_,
                                                   newValue=self._state,
                                                   newValueRaw=None,
                                                   unitOfMeasure=self._unitOfMeasure,
                                                   oldRemoteDatatype=self.type_,
                                                   oldValue=oldstate,
                                                   oldValueRaw="",
                                                   oldUnitOfMeasure="",
                                                   asUpdate=True,
                                                   )
    self._processInternalEvent(event)

  # noinspection PyTypeChecker
  def command(self, value: typing.Any) -> None:
    """Sends the given value as command to the event bus.

    Args:
      value (object): The value to send as command to the event bus. The type of the
                      value depends on the item type and is checked accordingly.
    """

    self._validate_value(value)

    v = self._rest_format(value)
    self._state = value
    self.lastCommandSent = datetime.now()
    self.openhab.req_post('/items/{}'.format(self.name), data=v)

    uoM=""
    if hasattr(self,"_unitOfMeasure"):
      uoM=self._unitOfMeasure
    event = openhab.events.ItemCommandEvent(itemname=self.name, source=openhab.events.EventSourceInternal,remoteDatatype=self.type_, newValue=value, newValueRaw=None, unitOfMeasure=uoM)
    self._processInternalEvent(event)


  def update_state_null(self) -> None:
    """Update the state of the item to *NULL*."""
    self._update('NULL')

  def update_state_undef(self) -> None:
    """Update the state of the item to *UNDEF*."""
    self._update('UNDEF')

  def is_state_null(self) -> bool:
    """If the item state is None, use this method for checking if the remote value is NULL."""
    if self.state is None:
      # we need to query the current remote state as else this method will not work correctly if called after
      # either update_state method
      if self._raw_state is None:
        # This should never happen
        raise ValueError('Invalid internal (raw) state.')

      return self._raw_state == 'NULL'

    return False

  def is_state_undef(self) -> bool:
    """If the item state is None, use this method for checking if the remote value is UNDEF."""
    if self.state is None:
      # we need to query the current remote state as else this method will not work correctly if called after
      # either update_state method
      if self._raw_state is None:
        # This should never happen
        raise ValueError('Invalid internal (raw) state.')

      return self._raw_state == 'UNDEF'

    return False



class DateTimeItem(Item):
  """DateTime item type."""

  types = [openhab.types.DateTimeType]
  TYPENAME = "DateTime"

  def __gt__(self, other):
    return self._state > other

  def __lt__(self, other):
    return not self.__gt__(other)

  def __eq__(self, other):
    return self._state == other

  def __ne__(self, other):
    return not self.__eq__(other)

  def _parse_rest(self, value):
    """Parse a REST result into a native object.

    Args:
      value (str): A string argument to be converted into a datetime.datetime object.

    Returns:
      datetime.datetime: The datetime.datetime object as converted from the string
                         parameter.
    """
    return (dateutil.parser.parse(value),"")

  def _rest_format(self, value):
    """Format a value before submitting to openHAB.

    Args:
      value (datetime.datetime): A datetime.datetime argument to be converted
                                 into a string.

    Returns:
      str: The string as converted from the datetime.datetime parameter.
    """
    # openHAB supports only up to milliseconds as of this writing
    return value.isoformat(timespec='milliseconds')


class PlayerItem(Item):
  """PlayerItem item type."""
  TYPENAME = "Player"

  types = [openhab.types.PlayerType]

  def play(self) -> None:
    """Set the state of the player to PLAY."""
    self.command('PLAY')

  def pause(self) -> None:
    """Set the state of the player to PAUSE."""
    self.command('PAUSE')

  def next(self) -> None:
    """Set the state of the player to NEXT."""
    self.command('NEXT')

  def previous(self) -> None:
    """Set the state of the player to PREVIOUS."""
    self.command('PREVIOUS')


class SwitchItem(Item):
  """SwitchItem item type."""


  types = [openhab.types.OnOffType]
  TYPENAME = "Switch"

  def on(self) -> None:
    """Set the state of the switch to ON."""
    self.command('ON')

  def off(self) -> None:
    """Set the state of the switch to OFF."""
    self.command('OFF')

  def toggle(self) -> None:
    """Toggle the state of the switch to OFF to ON and vice versa."""
    if self.state == 'ON':
      self.off()
    else:
      self.on()


class NumberItem(Item):
  """NumberItem item type."""

  types = [openhab.types.DecimalType]
  TYPENAME = "Number"

  def _parse_rest(self, value: str) -> float:
    """Parse a REST result into a native object.

    Args:
      value (str): A string argument to be converted into a float object.

    Returns:
      float: The float object as converted from the string parameter.
      str: The unit Of Measure or empty string
    """

    #m = re.match(r'''^(-?[0-9.]+)''', value)
    try:
      m= re.match("(-?[0-9.]+)\s?(.*)?$", value)

      if m:
        value=m.group(1)
        unitOfMeasure = m.group(2)

        #logging.getLogger().debug("original value:{}, myvalue:{}, my UoM:{}".format(m,value,unitOfMeasure))
        return (float(value),unitOfMeasure)
      else:
        return value
    except Exception as e:
      self.logger.error("error in parsing new value '{}' for '{}'".format(value,self.name),e)

    raise ValueError('{}: unable to parse value "{}"'.format(self.__class__, value))

  def _rest_format(self, value: float) -> str:
    """Format a value before submitting to openHAB.

    Args:
      value (float): A float argument to be converted into a string.

    Returns:
      str: The string as converted from the float parameter.
    """
    return str(value)


class ContactItem(Item):
  """Contact item type."""

  types = [openhab.types.OpenCloseType]
  TYPENAME = "Contact"

  def command(self, *args, **kwargs) -> None:
    """This overrides the `Item` command method.

    Note: Commands are not accepted for items of type contact.
    """
    raise ValueError('This item ({}) only supports updates, not commands!'.format(self.__class__))

  def open(self) -> None:
    """Set the state of the contact item to OPEN."""
    self.state = 'OPEN'

  def closed(self) -> None:
    """Set the state of the contact item to CLOSED."""
    self.state = 'CLOSED'


class DimmerItem(Item):
  """DimmerItem item type."""

  types = [openhab.types.OnOffType, openhab.types.PercentType, openhab.types.IncreaseDecreaseType]
  TYPENAME = "Dimmer"

  def _parse_rest(self, value: str) -> int:
    """Parse a REST result into a native object.

    Args:
      value (str): A string argument to be converted into a int object.

    Returns:
      int: The int object as converted from the string parameter.
    """
    return (int(float(value)),"")

  def _rest_format(self, value: typing.Union[str, int]) -> str:
    """Format a value before submitting to OpenHAB.

    Args:
      value: Either a string or an integer; in the latter case we have to cast it to a string.

    Returns:
      str: The string as possibly converted from the parameter.
    """
    if not isinstance(value, str):
      return str(value)

    return value

  def on(self) -> None:
    """Set the state of the dimmer to ON."""
    self.command('ON')

  def off(self) -> None:
    """Set the state of the dimmer to OFF."""
    self.command('OFF')

  def increase(self) -> None:
    """Increase the state of the dimmer."""
    self.command('INCREASE')

  def decrease(self) -> None:
    """Decrease the state of the dimmer."""
    self.command('DECREASE')


class ColorItem(Item):
  """ColorItem item type."""

  types = [openhab.types.OnOffType, openhab.types.PercentType, openhab.types.IncreaseDecreaseType,
           openhab.types.ColorType]
  TYPENAME = "Color"

  def _parse_rest(self, value: str) -> str:
    """Parse a REST result into a native object.

    Args:
      value (str): A string argument to be converted into a str object.

    Returns:
      str: The str object as converted from the string parameter.
    """
    return (str(value),"")

  def _rest_format(self, value: typing.Union[str, int]) -> str:
    """Format a value before submitting to openHAB.

    Args:
      value: Either a string or an integer; in the latter case we have to cast it to a string.

    Returns:
      str: The string as possibly converted from the parameter.
    """
    if not isinstance(value, str):
      return str(value)

    return value

  def on(self) -> None:
    """Set the state of the color to ON."""
    self.command('ON')

  def off(self) -> None:
    """Set the state of the color to OFF."""
    self.command('OFF')

  def increase(self) -> None:
    """Increase the state of the color."""
    self.command('INCREASE')

  def decrease(self) -> None:
    """Decrease the state of the color."""
    self.command('DECREASE')


class RollershutterItem(Item):
  """RollershutterItem item type."""

  types = [openhab.types.UpDownType, openhab.types.PercentType, openhab.types.StopType]
  TYPENAME = "Rollershutter"

  def _parse_rest(self, value: str) -> int:
    """Parse a REST result into a native object.

    Args:
      value (str): A string argument to be converted into a int object.

    Returns:
      int: The int object as converted from the string parameter.
    """
    return (int(float(value)),"")

  def _rest_format(self, value: typing.Union[str, int]) -> str:
    """Format a value before submitting to openHAB.

    Args:
      value: Either a string or an integer; in the latter case we have to cast it to a string.

    Returns:
      str: The string as possibly converted from the parameter.
    """
    if not isinstance(value, str):
      return str(value)

    return value

  def up(self) -> None:
    """Set the state of the dimmer to ON."""
    self.command('UP')

  def down(self) -> None:
    """Set the state of the dimmer to OFF."""
    self.command('DOWN')

  def stop(self) -> None:
    """Set the state of the dimmer to OFF."""
    self.command('STOP')
