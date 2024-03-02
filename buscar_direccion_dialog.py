# encoding: utf-8
# -----------------------------------------------------------
# Copyright (C) 2018 Matthias Kuhn
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from qgis.core import QgsProject
from qgis.utils import iface
import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

DialogBase, DialogType = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'buscar_direccion.ui'))

class BuscarDireccionDialog(DialogType, DialogBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.btnBuscar.clicked.connect(self.buscarDireccion)
        self.txtCalle.setFocus(True)
    

    def buscarDireccion(self):
        calle = self.txtCalle.text()
        altura = self.txtAltura.text()
        
        if(not altura):
            filter = "lower(calle2) = lower(\'" + calle + "\') or lower(calle) = lower(\'" + calle + "\')"   
        else:
            filter = "(lower(calle2) = lower(\'" + calle + "\') and desde <= " + altura + " and hasta >= " + altura + ") or (lower(calle) = lower(\'" + calle + "\') and desde <= " + altura + " and hasta >= " + altura + ")"   
        
        #QMessageBox.information(None, u'Buscar Dirección', u'Filtro: ' + filter)
        
        layerActivo = iface.activeLayer()
        if(layerActivo):
            layerActivo.removeSelection()
        layers = QgsProject.instance().mapLayersByName('tramos')
        layer = layers[0]
        iface.setActiveLayer(layer)
        
        #groupLayer = layer.parent()
        #groupLayer.setItemVisibilityChecked(True)
        if(not QgsProject.instance().layerTreeRoot().findGroup("Tramos").isVisible()):
            QgsProject.instance().layerTreeRoot().findGroup("Tramos").setItemVisibilityChecked(True)
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        
        #layer.selectByExpression("calle2 = \'Calle 17\'")
        layer.selectByExpression(filter)

        QgsProject.instance().layerTreeRoot().findGroup("Tramos").setExpanded(False)
        
        #print(layer.selectedFeatureCount())
        if(layer.selectedFeatureCount() > 0):
            iface.mapCanvas().zoomToSelected()
            self.close()
        else:
            QMessageBox.information(None, u'Buscar Dirección', u'Dirección no encontrada.')

        layersCliente = QgsProject.instance().mapLayersByName('clientes')
        layerCliente = layersCliente[0]
        iface.setActiveLayer(layerCliente)
        #layer.removeSelection()
        
        