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

import abc
import datetime
import re
import typing

__author__ = 'Georges Toth <georges@trypill.org>'
__license__ = 'AGPLv3+'


class CommandType(metaclass=abc.ABCMeta):
  """Base command data_type class."""

  @classmethod
  @abc.abstractmethod
  def validate(cls, value: typing.Any) -> None:
    """Value validation method. As this is the base class which should not be used\
    directly, we throw a NotImplementedError exception.

    Args:
      value (Object): The value to validate. The data_type of the value depends on the item
                      data_type and is checked accordingly.

    Raises:
      NotImplementedError: Raises NotImplementedError as the base class should never
                           be used directly.
    """
    raise NotImplementedError()


class StringType(CommandType):
  """StringType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are andy of data_type string.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    if not isinstance(value, str):
      raise ValueError()


class OnOffType(StringType):
  """OnOffType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``ON`` and ``OFF``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['ON', 'OFF']:
      raise ValueError()


class OpenCloseType(StringType):
  """OpenCloseType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``OPEN`` and ``CLOSED``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['OPEN', 'CLOSED']:
      raise ValueError()


class ColorType(StringType):
  """ColorType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are in format H,S,B.
    Value ranges:
      H(ue): 0-360
      S(aturation): 0-100
      B(rightness): 0-100

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)
    h, s, b = re.split(',', value)
    if not ((0 <= int(h) <= 360) and (0 <= int(s) <= 100) and (0 <= int(b) <= 100)):
      raise ValueError()


class DecimalType(CommandType):
  """DecimalType data_type class."""

  @classmethod
  def validate(cls, value: typing.Union[float, int]) -> None:
    """Value validation method.

    Valid values are any of data_type ``float`` or ``int``.

    Args:
      value (float): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    if not isinstance(value, (int, float)):
      raise ValueError()


class PercentType(DecimalType):
  """PercentType data_type class."""

  @classmethod
  def validate(cls, value: typing.Union[float, int]) -> None:
    """Value validation method.

    Valid values are any of data_type ``float`` or ``int`` and must be greater of equal to 0
    and smaller or equal to 100.

    Args:
      value (float): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if not 0 <= value <= 100:
      raise ValueError()


class IncreaseDecreaseType(StringType):
  """IncreaseDecreaseType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``INCREASE`` and ``DECREASE``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['INCREASE', 'DECREASE']:
      raise ValueError()


class DateTimeType(CommandType):
  """DateTimeType data_type class."""

  @classmethod
  def validate(cls, value: datetime.datetime) -> None:
    """Value validation method.

    Valid values are any of data_type ``datetime.datetime``.

    Args:
      value (datetime.datetime): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    if not isinstance(value, datetime.datetime):
      raise ValueError()


class UpDownType(StringType):
  """UpDownType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``UP`` and ``DOWN``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['UP', 'DOWN']:
      raise ValueError()


class StopType(StringType):
  """UpDownType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``UP`` and ``DOWN``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['STOP']:
      raise ValueError()


class PlayerType(StringType):
  """PlayerType data_type class."""

  @classmethod
  def validate(cls, value: str) -> None:
    """Value validation method.

    Valid values are ``PLAY``, ``PAUSE``, ``NEXT``, ``PREVIOUS``, ``REWIND``, and ``FASTFORWARD``.

    Args:
      value (str): The value to validate.

    Raises:
      ValueError: Raises ValueError if an invalid value has been specified.
    """
    super().validate(value)

    if value not in ['PLAY', 'PAUSE', 'NEXT', 'PREVIOUS', 'REWIND', 'FASTFORWARD']:
      raise ValueError()
