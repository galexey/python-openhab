# -*- coding: utf-8 -*-
"""tests for creating and deletion of items """

#
# Alexey Grubauer (c) 2020-present <alexey@ingenious-minds.at>
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
import openhab
import openhab.events
import openhab.items as items
import openhab.ui as ui
import openhab.types
import logging
import time
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)
logging.basicConfig(level=10, format="%(levelno)s:%(asctime)s - %(message)s - %(name)s - PID:%(process)d - THREADID:%(thread)d - %(levelname)s - MODULE:%(module)s, -FN:%(filename)s -FUNC:%(funcName)s:%(lineno)d")

log.error("xx")
log.warning("www")
log.info("iii")
log.debug("ddddd")

base_url_oh3 = 'http://10.10.20.85:8080/rest'
token = "in openhab admin web interface klick your created user (lower left corner). then create new API toker and copy it here"

def test_widgets(myopenhab: openhab.OpenHAB):
  log.info("starting tests 'test widgets'")
  # all_widgets=myopenhab._get_all_widgets_raw()
  # log.info("all widgets:{}".format(all_widgets))
  wf = ui.WidgetFactory(myopenhab)
  awidget = wf.get_widget("test_widget1")

  log.info("test_widget1  widgets:{}".format(awidget))
  awidget.code["tags"].append("testtag")
  log.info("test_widget1.1  widgets:{}".format(awidget))
  awidget.save()
  time.sleep(0.2)


  aw2=wf.create_widget("test_widget2",awidget.code)
  aw2.save()
  time.sleep(0.2)
  wf.delete_widget("test_widget2")






headers = {"Authorization": "{}".format(token)}
myopenhab = openhab.OpenHAB(base_url_oh3, openhab_version= openhab.OpenHAB.Version.OH3 , auto_update=True, http_auth=HTTPBasicAuth(token, ""), http_headers_for_autoupdate=headers)


test_widgets(myopenhab)
