import urllib.request
import json

# todo: make sure there is an _add method to every widget so the default will be to add widget data after a widget has been initialized
# User experience: Make sure a user can either initialize a widget in one line, or by using the add method for every widget.

class Dashboard(object):
    """
    Dashboard object.  Used to hold the dashboard's API key and a collection
    of all the widgets that have been created from this instance.
    push_all() function allows a user to push to all associated dashboards.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.widgets = []

    def __repr__(self):
        return "<DASHBOARD OBJECT, API KEY: {api_key}>".format(
            api_key=self.api_key)

    def push_all(self):
        for widget in self.widgets:
            widget.push()


class Widget(object):
    """
    Main widget object for all other custom widgets to inherit from.  This
    class houses the main push function as well as the final payload
    assembly steps.
    """
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.api_key = dashboard.api_key
        self.widget_key = None
        self.payload = {
            "api_key": self.api_key,
            "data": {
                "item": [

                ]
            }
        }
        dashboard.widgets.append(self)

    def _assemble_data(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass

    def add_data(self, *args, **kwargs):
        pass

    def _assemble_payload(self, _data_module, *args, **kwargs):
        self.payload["data"] = _data_module

    def push(self):
        self._assemble_data()
        _api_endpoint = 'https://push.geckoboard.com/v1/send/'\
                        '{widget_key}'.format(widget_key=self.widget_key)
        _payload_json = json.dumps(self.payload).encode('utf-8')
        _request = urllib.request.Request(url=_api_endpoint,
                                          data=_payload_json
                                          )
        _request.add_header('Content-Type', 'application/json')

        try:
            _response = urllib.request.urlopen(_request)
            _api_status = json.loads(_response.read().decode('utf-8'))
            print("API Success: {}".format(_api_status["success"]))

        except urllib.request.HTTPError as e:
            print(e)


class GeckoboardException(Exception):
    pass


class BarChart(Widget):
    def __init__(self, widget_key, data=None, x_axis_labels=None,
                 x_axis_type=None, y_axis_format=None, y_axis_unit=None,
                 *args, **kwargs):
        super(BarChart, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.data = []
        self.x_axis_labels = x_axis_labels
        self.x_axis_type = x_axis_type
        self.y_axis_format = y_axis_format
        self.y_axis_unit = y_axis_unit


    def add_data(self, data, *args, **kwargs):
        self.data.append({"data": data})


    def add(self, data=None, x_axis_labels=None, x_axis_type=None,
            y_axis_format=None, y_axis_unit=None):

        if self.data[0]["data"] is not None:
            raise GeckoboardException(
                "Widget data has already been initialized."
            )
        else:
            self.data[0]["data"] = data

        if x_axis_labels is not None: self.x_axis_labels = x_axis_labels
        if x_axis_type is not None: self.x_axis_type = x_axis_type
        if y_axis_format is not None: self.y_axis_format = y_axis_format
        if y_axis_unit is not None: self.y_axis_unit = y_axis_unit

    def _assemble_data(self):
        if self.data is None:
            raise GeckoboardException("Widget missing required data.")

        _data = {
            "x_axis": {},
            "y_axis": {},
            "series": self.data
        }

        if self.x_axis_labels is not None:
            _data["x_axis"]["labels"] = self.x_axis_labels

        if self.x_axis_type is not None:
            _data["x_axis"]["type"] = self.x_axis_type

        if self.y_axis_format is not None:
            _data["y_axis"]["format"] = self.y_axis_format

        if self.y_axis_unit is not None:
            _data["y_axis"]["unit"] = self.y_axis_unit

        self._assemble_payload(_data)


class BulletGraph(Widget):
    def __init__(self, widget_key, orientation=None, label=None, axis=None,
                 red_start=None, red_end=None, amber_start=None,
                 amber_end=None, green_start=None, green_end=None,
                 measure_start=None, measure_end=None, projected_start=None,
                 projected_end=None, comparative=None, sublabel=None,
                 *args, **kwargs):
        super(BulletGraph, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.orientation = orientation
        self.data = []

        _necessary = [label, axis, red_start, red_end, amber_start, amber_end,
                      green_start, green_end, measure_start, measure_end,
                      projected_start, projected_end, comparative]
        _necessary_none = list(bool(item is None) for item in _necessary)
        _is_all_none = all(_necessary_none)

        if not _is_all_none:
            self.add_data(label, axis, red_start, red_end, amber_start,
                          amber_end, green_start, green_end, measure_start,
                          measure_end, projected_start, projected_end,
                          comparative)


    def add(self, orientation=None, *args, **kwargs):
        if orientation is not None: self.orientation = orientation


    def add_data(self, label, axis, red_start, red_end, amber_start,
            amber_end, green_start, green_end, measure_start, measure_end,
            projected_start, projected_end, comparative, sublabel=None):

        if len(self.data) >= 4:
            raise GeckoboardException(
                "Bullet Graphs support a maximum of 4 multiples."
            )

        all_or_none = self._all_or_none(label, axis, red_start, red_end,
                                        amber_start, amber_end, green_start,
                                        green_end, measure_start, measure_end,
                                        projected_start, projected_end,
                                        comparative)

        _item_payload = {
                        "label": label,
                        "axis": {
                            "point": axis,
                        },
                        "range": {
                            "red": {
                                "start": red_start,
                                "end": red_end
                            },
                            "amber": {
                                "start": amber_start,
                                "end": amber_end

                            },
                            "green": {
                                "start": green_start,
                                "end": green_end
                            }
                        },
                        "measure": {
                            "current": {
                                "start": measure_start,
                                "end": measure_end
                            },
                        "projected": {
                            "start": projected_start,
                            "end": projected_end
                        }
                    },
                    "comparative": {
                        "point": comparative
                        }
                    }


        self.data.append(_item_payload)


    def _all_or_none(self, label, axis, red_start, red_end, amber_start,
                         amber_end, green_start, green_end, measure_start,
                         measure_end, projected_start, projected_end,
                         comparative):

        # Check to make sure that all or none of the required fields are added
        _necessary = [label, axis, red_start, red_end, amber_start, amber_end,
                      green_start, green_end, measure_start, measure_end,
                      projected_start, projected_end, comparative]
        _necessary_none = list(bool(item is None) for item in _necessary)
        _is_all_none = all(_necessary_none)
        _is_all_not_none = all(not x for x in _necessary_none)
        if (_is_all_none == _is_all_not_none):
            raise GeckoboardException("Missing required data point(s).")
        return True


    def _assemble_data(self):
        _data = {
            "orientation": self.orientation,
            "item": None
        }
        _item = self.data

        if len(_item) == 1:
            _data["item"] = _item[0]
        elif len(_item) > 1 and len(_item) <= 4:
            _data["item"] = _item

        self._assemble_payload(_data)


class Funnel(Widget):
    def __init__(self, widget_key, value=None, label=None, type=None,
                 percentage=None, *args, **kwargs):
        super(Funnel, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.type = type
        self.percentage = percentage
        self.data = []
        if value is not None and label is not None:
            self.data.append({"value": value, "label": label})


    def add_data(self, value, label):
        if len(self.data) >= 8:
            raise GeckoboardException(
                "Funnel widgets support a max of 8 steps."
            )

        _step = {
            "value": value,
            "label": label,
        }
        self.data.append(_step)


    def _assemble_data(self):
        if len(self.data) == 0:
            raise GeckoboardException("Must add at least one value.")

        _data = {
            "item": self.data
        }
        if self.type is not None:
            _data["type"] = self.type

        if self.percentage is not None:
            _data["percentage"] = self.percentage

        self._assemble_payload(_data)


class GeckoMeter(Widget):
    def __init__(self, widget_key, item=None, min_value=None, max_value=None,
                 *args, **kwargs):
        super(GeckoMeter, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.item = item
        self.min_value = min_value
        self.max_value = max_value



    def add_data(self, item, min_value, max_value):
        self.item = item
        self.min_value = min_value
        self.max_value = max_value


    def _assemble_data(self):
        if self.item is None \
                or self.min_value is None \
                or self.max_value is None:
            raise GeckoboardException("Widget missing required data.")

        _data = {
            "item": self.item,
            "min": {
                "value": self.min_value
            },
            "max": {
                "value": self.max_value
            }
        }
        self._assemble_payload(_data)


class HighCharts(Widget):
    def __init__(self, widget_key, highchart=None, *args, **kwargs):
        super(HighCharts, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.highchart = highchart

    def add_data(self, highchart):
        if self.highchart is not None:
            raise GeckoboardException("Widget has data already assigned.")

        self.highchart = highchart

    def _assemble_data(self):
        if not isinstance(self.highchart, str):
            raise TypeError("Highchart must be a string object")
        if self.highchart is None:
            raise GeckoboardException("Widget missing required data.")

        _data = {
            "highchart": self.highchart
        }
        self._assemble_payload(_data)


class Leaderboard(Widget):
    def __init__(self, widget_key, label=None, value=None, previous_rank=None,
                 format=None, unit=None, *args, **kwargs):
        super(Leaderboard, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.format = format
        self.unit = unit
        self.data = []

        if label is not None:
            self.add_data(label, value, previous_rank)


    def add_data(self, label, value=None, previous_rank=None):
        _item = {
            "label": label
        }

        if value is not None:
            _item["value"] = value

        if previous_rank is not None:
            _item["previous_rank"] = previous_rank

        self.data.append(_item)


    def _assemble_data(self):
        if len(self.data) > 22:
            raise GeckoboardException(
                "Leaderboard widget accepts a max of 22 labels"
            )
        elif len(self.data) == 0:
            raise GeckoboardException("Must add at least one value.")

        _data = {
            "items": self.data
        }
        if self.format is not None:
            _data["format"] = self.format

        if self.unit is not None:
            _data["unit"] = self.unit

        self._assemble_payload(_data)


class LineChart(Widget):
    def __init__(self, widget_key, data=None, name=None, incomplete_from=None,
                 type=None, x_axis_labels=None, x_axis_type=None,
                 y_axis_format=None, y_axis_unit=None, *args, **kwargs):
        super(LineChart, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.x_axis_labels = x_axis_labels
        self.x_axis_type = x_axis_type
        self.y_axis_format = y_axis_format
        self.y_axis_unit = y_axis_unit
        self.data = []

        if data is not None:
            self.add_data(data, name, incomplete_from, type)


    def add_data(self, data, name=None, incomplete_from=None, type=None,
                 *args, **kwargs):

        if data is not None and name is not None:
            self.data.append({"data": data, "name": name})
        elif data is not None and name is None:
            self.data.append({"data": data})
        if incomplete_from is not None: self.incomplete_from = incomplete_from
        if type is not None: self.type = type


    def add(self, x_axis_labels=None, x_axis_type=None, y_axis_format=None,
             y_axis_unit=None):
        if x_axis_labels is not None:
            self.x_axis_labels = x_axis_labels
        if x_axis_type is not None:
            self.x_axis_type = x_axis_type
        if y_axis_format is not None:
            self.y_axis_format = y_axis_format
        if y_axis_unit is not None:
            self.y_axis_unit = y_axis_unit


    def _label_data_check(self):
        _is_pairs = [bool(self._data_check(x["data"])) for x in self.data]
        if all(_is_pairs) and self.x_axis_labels is not None:
            raise GeckoboardException("Two x-axis labels provided.")
        elif not all(not x for x in _is_pairs) and not all(_is_pairs):
            raise GeckoboardException("Can not mix pairs and lists.")


    def _data_check(self, data):
        """
        Check whether data is an [x,y] array or as a list [x,y,z].
        """
        if data is None:
            pass
        elif data is not None:
            return bool(any(isinstance(l, list) for l in data))


    def _assemble_data(self):
        if len(self.data) == 0:
            raise GeckoboardException("Must add at least one value.")

        self._label_data_check()  # Run through pair/list data checking.

        _data = {
            "series": self.data,
            "y_axis": {},
            "x_axis": {}
        }

        if self.x_axis_labels is not None:
            _data["x_axis"]["labels"] = self.x_axis_labels

        if self.x_axis_type is not None:
            _data["x_axis"]["type"] = self.x_axis_type

        if self.y_axis_format is not None:
            _data["y_axis"]["format"] = self.y_axis_format

        if self.y_axis_unit is not None:
            _data["y_axis"]["unit"] = self.y_axis_unit

        self._assemble_payload(_data)


class List(Widget):
    def __init__(self, widget_key, text=None, name=None, color=None,
                 description=None, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.widget_key = widget_key
        self.data = []

    def add_data(self, text, name=None, color=None, description=None):
        _data = {
            "title": {
                "text": text
            }
        }

        if name is not None and color is not None:
            _data["label"] = {}

        if name is not None:
            _data["label"]["name"] = name

        if color is not None:
            _data["label"]["color"] = color

        if description is not None:
            _data["description"] = description

        self.data.append(_data)

    def _assemble_data(self, *args, **kwargs):
        self._assemble_payload(self.data)
