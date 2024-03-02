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
from PyQt5.QtCore import Qt, QDate

DialogBase, DialogType = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'pedidos_filtro.ui'))

class PedidosFiltroDialog(DialogType, DialogBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.bboxFiltrarPedidos.accepted.connect(self.filtrarPedidos)
        
        fechaHoy = QDate.currentDate()
        self.deFechaDesde.setDate(fechaHoy.addDays(-3))
        self.deFechaDesde.setDisplayFormat("dd/MM/yyyy")
        self.deFechaDesde.setFocus(True)
        self.deFechaHasta.setDate(fechaHoy)
        self.deFechaHasta.setDisplayFormat("dd/MM/yyyy")
    

    def filtrarPedidos(self):
        # fechaDesde = self.deFechaDesde.date().toPyDate()
        # fechaHasta = self.deFechaHasta.date().toPyDate()
        #fechaDesde = self.deFechaDesde.textFromDateTime(self.deFechaDesde.dateTime())
        fechaDesde = self.deFechaDesde.dateTime().toString("dd/MM/yyyy")
        fechaHasta = self.deFechaHasta.dateTime().toString("dd/MM/yyyy")
        # QMessageBox.information(None, u'Filtrar Pedidos', u'Fecha Desde: ' + fechaDesde)
        
        # if(not deFechaDesde):
            # filter = "lower(calle2) = lower(\'" + calle + "\') or lower(calle) = lower(\'" + calle + "\')"   
        # else:
            # filter = "(lower(calle2) = lower(\'" + calle + "\') and desde <= " + altura + " and hasta >= " + altura + ") or (lower(calle) = lower(\'" + calle + "\') and desde <= " + altura + " and hasta >= " + altura + ")"   
        

        layerActivo = iface.activeLayer()
        if(layerActivo):
            layerActivo.removeSelection()
        layers = QgsProject.instance().mapLayersByName('pedido finde')
        layer = layers[0]
        iface.setActiveLayer(layer)
        
        # filter = "fecha >= to_timestamp('04/03/2022', 'DD/MM/YYYY') and fecha <= to_timestamp('06/03/2022', 'DD/MM/YYYY')"
        filter = "fecha >= to_timestamp('" + fechaDesde + "', 'DD/MM/YYYY') and fecha <= to_timestamp('" + fechaHasta + "', 'DD/MM/YYYY')"
        # QMessageBox.information(None, u'Pedidos Filtro', u'Filtro: ' + filter)
        layer.setSubsetString(filter)
        
        if(not QgsProject.instance().layerTreeRoot().findGroup("Pedidos").isVisible()):
            QgsProject.instance().layerTreeRoot().findGroup("Pedidos").setItemVisibilityChecked(True)
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        
        layer.selectByExpression(filter)
        
        canvas = iface.mapCanvas()
        extent = layer.extent()
        canvas.setExtent(extent)
        
        #QgsProject.instance().layerTreeRoot().findGroup("Pedidos").setExpanded(False)
        
        # layersCliente = QgsProject.instance().mapLayersByName('clientes')
        # layerCliente = layersCliente[0]
        # iface.setActiveLayer(layerCliente)

        #print(layer.selectedFeatureCount())
        # if(layer.selectedFeatureCount() > 0):
            # iface.mapCanvas().zoomToSelected()
            # self.close()
        # else:
            # QMessageBox.information(None, u'Pedidos Filtro', u'Pedidos no encontrados en la fecha.')

        #layer.removeSelection()
        
        