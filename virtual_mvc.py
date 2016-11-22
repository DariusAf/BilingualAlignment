# -*- coding:utf-8 -*-

class LinkErrorMVC(Exception):
    def __init__(self):
        super.__init__()

    def __str__(self):
        return "MVC not correctly initialized"


class VirtualPattern:
    def __init__(self):
        self._isLinked = [False,False]
    
    @staticmethod
    def mvc_check(self):
        if not self._isLinked[0] and self._isLinked[1]:
            raise LinkErrorMVC
    

class VirtualModel(VirtualPattern):
    def __init__(self):
        super().__init__()
        self._views = []
        self._controller = None

    def mvc_link_views(self,v):
        self._views = v
        self._isLinked[0] = True
    
    def mvc_link_controller(self,c):
        self._controller = c
        self._isLinked[1] = True


class VirtualView(VirtualPattern):
    def __init__(self):
        super().__init__()
        self._model = None
        self._controller = None

    def mvc_link_model(self,m):
        self._models = m
        self._isLinked[0] = True
    
    def mvc_link_controller(self,c):
        self._controller = c
        self._isLinked[1] = True


class VirtualController(VirtualPattern):
    def __init__(self):
        super().__init__()
        self._views = []
        self._model = None

    def mvc_link_views(self,v):
        self._views = v
        self._isLinked[0] = True
    
    def mvc_link_model(self,m):
        self._models = m
        self._isLinked[1] = True
    