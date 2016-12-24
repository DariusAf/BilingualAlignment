# -*- coding:utf-8 -*-
"""
Some abstract classes to implement the MVC pattern.
"""


class LinkErrorMVC(Exception):
    def __init__(self):
        super(LinkErrorMVC, self).__init__()

    def __str__(self):
        return "MVC not correctly initialized"


class VirtualMVC:
    def __init__(self):
        self._isLinked = {"Model": False, "View": False, "Controller": False}
        self._type = {"Model": False, "View": False, "Controller": False}
        self._model = None
        self._views = []
        self._controller = None

    def mvc_check(self):
        """
        Check if the instance is correctly linked.
        """
        if not ((self._isLinked["Model"] or self._type["Model"]) and
                (self._isLinked["View"] or self._type["View"]) and
                (self._isLinked["Controller"] or self._type["Controller"])):
            raise LinkErrorMVC

    @property
    def model(self):
        self.mvc_check()
        if self._type["Model"]:
            return self
        return self._model

    @property
    def views(self):
        self.mvc_check()
        if self._type["View"]:
            return self
        return self._views

    @property
    def controller(self):
        self.mvc_check()
        if self._type["Controller"]:
            return self
        return self._controller

    def mvc_link_model(self, m):
        if not self._type["Model"]:
            self._model = m
            self._isLinked["Model"] = True

    def mvc_link_views(self, v):
        if not self._type["View"]:
            self._views = v
            self._isLinked["View"] = True

    def mvc_link_controller(self, c):
        if not self._type["Controller"]:
            self._controller = c
            self._isLinked["Controller"] = True


class VirtualModel(VirtualMVC):
    def __init__(self):
        super().__init__()
        self._type["Model"] = True


class VirtualView(VirtualMVC):
    def __init__(self):
        super().__init__()
        self._type["View"] = True


class VirtualController(VirtualMVC):
    def __init__(self):
        super().__init__()
        self._type["Controller"] = True


def link_mvc(model, views, controller):
    model.mvc_link_controller(controller)
    model.mvc_link_views(views)
    controller.mvc_link_model(model)
    controller.mvc_link_views(views)
    for view in views:
        view.mvc_link_model(model)
        view.mvc_link_controller(controller)
