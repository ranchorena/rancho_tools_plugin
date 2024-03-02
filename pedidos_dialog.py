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

from qgis.core import QgsProject,QgsExpression,QgsFeatureRequest,NULL
from qgis.utils import iface
import os
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTime
import configparser

DialogBase, DialogType = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'pedidos.ui'))

class PedidosDialog(DialogType, DialogBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.txtCantidadTotal.setStyleSheet("background:#ffff9d;")
        self.txtCantidadTotalVendidas.setStyleSheet("background:#ffff9d;")
        self.txtValorTotal.setStyleSheet("background:#ffff9d;")
        
        self.tableClienteWidget.setAlternatingRowColors(True)
        darkPalette = self.tableClienteWidget.palette();
        darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(37,37,37));
        darkPalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(73,73,73));
        darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(90,90,124));
        darkPalette.setColor(QtGui.QPalette.Text, Qt.white)
        self.tableClienteWidget.setPalette(darkPalette);
        
        self.tableClienteWidget.verticalHeader().setDefaultSectionSize(20)
        
        # window =  QWidget()
        # layout =  QVBoxLayout()
        # layout.addWidget(self.tableClienteWidget)
        # window.setLayout(layout)
        # window.show()

        # v = QVBoxLayout(self)
        # v.addWidget(window)
             
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'rancho_tools_plugin.ini'))
        self.precioDocena = float(config['variables']['precio_docena'])
        print(self.precioDocena)
   
        self.cargarPedidos()
        
    def cargarPedidos(self):
        filter = "tiene_pedido=1"
        self.buscarClientesByFilter(filter)
                
    
    def buscarClientesByFilter(self, filter):          
        layerActivo = iface.activeLayer()
        if(layerActivo):
            layerActivo.removeSelection()  
            
        layers = QgsProject.instance().mapLayersByName('clientes')
        layer = layers[0]
        iface.setActiveLayer(layer)          
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)

        expresion = QgsExpression(filter)
        clause = QgsFeatureRequest.OrderByClause('nro_pao', ascending=True)
        orderby = QgsFeatureRequest.OrderBy([clause])            
        request = QgsFeatureRequest(expresion)
        request.setOrderBy(orderby)
        features = layer.getFeatures(request)
        
        layer.selectByExpression(filter)
        cantFeatures = layer.selectedFeatureCount()
        if(cantFeatures > 0):
            iface.mapCanvas().zoomToSelected()
        
        cantidadTotal = 0
        cantidadTotalVendidas = 0
        valorTotal = 0
        table = self.tableClienteWidget
        table.setRowCount(cantFeatures)
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels(["Id", "Nro Pao", "Nombre", "Direccion", "Cantidad", "Valor", "Horario", "Regalo", "Observación", "Teléfono"])
        for iCol in range(table.columnCount()):
            table.horizontalHeaderItem(iCol).setBackground(QtGui.QBrush(QtGui.QColor(57,66,72)))
            table.horizontalHeaderItem(iCol).setForeground(QtGui.QBrush(Qt.white)) 

        for idx,feature in enumerate(features):
            #print("Feature:")
            #print(feature.id())
            #print(feature["id"])
            #print(feature["nombre"])
            #print(feature["direccion"])
            item_id = QTableWidgetItem()
            item_id.setData(Qt.EditRole, feature["id"])
            item_id.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            
            item_nro_pao = QTableWidgetItem()
            item_nro_pao.setData(Qt.EditRole, feature["nro_pao"])
            item_nro_pao.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            
            item_nombre = QTableWidgetItem(feature["nombre"])
            direccion = ""
            if(feature["direccion"]):
                direccion = feature["direccion"]
            item_dir = QTableWidgetItem(direccion)
            
            cantidad = float(feature["cantidad"])
            cantidadTotal += cantidad
            item_cantidad = QTableWidgetItem()
            item_cantidad.setData(Qt.EditRole, cantidad)
            item_cantidad.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            #item_cantidad = QTableWidgetItem(feature["cantidad"])
            
            valor = cantidad * self.precioDocena
            item_valor = QTableWidgetItem()
            item_valor.setData(Qt.EditRole, '$ {0:.2f}'.format(valor))
            item_valor.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            
            horario = ""
            if(feature["horario"]):
                horario = QTime(feature["horario"]).toString("hh:mm:ss")
            item_horario = QTableWidgetItem(horario)
            item_horario.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            esRegalo = "";
            if(int(feature["es_regalo"])==1):
                esRegalo = "Es Regalo"
            else:
                valorTotal += valor
                cantidadTotalVendidas += cantidad
            #print(feature["es_regalo"])
            item_es_regalo = QTableWidgetItem(esRegalo)
            observacion = ""
            if(feature["observacion"]):
                observacion = feature["observacion"]
            item_observacion = QTableWidgetItem(observacion)
            telefono = ""
            if(feature["telefono"]):
                telefono = feature["telefono"]
            item_telefono = QTableWidgetItem(telefono)
      
            #item_altura = QTableWidgetItem()
            #altura = 0
            #if(feature["altura"]):
            #    altura = int(feature["altura"])
            #    
            #item_altura.setData(Qt.DisplayRole,feature["altura"])
            
            table.setItem(idx, 0, item_id)
            table.setItem(idx, 1, item_nro_pao)
            table.setItem(idx, 2, item_nombre)
            table.setItem(idx, 3, item_dir)
            table.setItem(idx, 4, item_cantidad)
            table.setItem(idx, 5, item_valor)
            table.setItem(idx, 6, item_horario)
            table.setItem(idx, 7, item_es_regalo)
            table.setItem(idx, 8, item_observacion)
            table.setItem(idx, 9, item_telefono)
        
        header = table.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QtWidgets.QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        
        self.txtCantidadTotal.setText(str(cantidadTotal))
        self.txtCantidadTotal.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.txtCantidadTotalVendidas.setText(str(cantidadTotalVendidas))
        self.txtCantidadTotalVendidas.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        
        #valorTotal = cantidadTotal * self.precioDocena
        self.txtValorTotal.setText('$ {0:.2f}'.format(valorTotal))
        self.txtValorTotal.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)

        iface.activeLayer().removeSelection()
        
        