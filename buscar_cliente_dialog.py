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
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

DialogBase, DialogType = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'buscar_cliente.ui'))

class BuscarClienteDialog(DialogType, DialogBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        iconBuscar = os.path.join(os.path.dirname(__file__), 'buscar.png')
        self.btnBuscarClientes.setIcon(QtGui.QIcon(iconBuscar))
        self.btnBuscarClientes.setIconSize(QtCore.QSize(18,18))
        self.btnBuscarClientes.clicked.connect(self.buscarClientes)
        
        self.btnBuscarClientesPorDireccion.clicked.connect(self.buscarClientesPorDireccion)
        self.btnBuscarClientesPorCalleAltura.clicked.connect(self.buscarClientesPorCalleAltura)
        self.btnGuardarCliente.clicked.connect(self.guardarCliente)
        self.tableClienteWidget.itemClicked.connect(self.clienteClicked)
        self.txtCliente.setFocus(True)
        
        # self.txtSelClienteId.setStyleSheet("QLineEdit{background : lightblue;}")
        #colorReadOnly = QColor(237, 237, 237)
        self.txtSelClienteId.setStyleSheet("background:#ededed;")
        self.txtSelClienteNombre.setStyleSheet("background:#ededed;")
        self.txtHorario.setInputMask("00:00:00")
        
        self.tableClienteWidget.setAlternatingRowColors(True)
        darkPalette = self.tableClienteWidget.palette();
        darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(37,37,37));
        darkPalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(73,73,73));
        darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(90,90,124));
        darkPalette.setColor(QtGui.QPalette.Text, Qt.white)
        self.tableClienteWidget.setPalette(darkPalette);
        
        self.tableClienteWidget.verticalHeader().setDefaultSectionSize(20)
        
        #self.tableClienteWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableClienteWidget.horizontalHeader().setStretchLastSection(True)
        table = self.tableClienteWidget
        for iCol in range(table.columnCount()):
            table.horizontalHeaderItem(iCol).setBackground(QtGui.QBrush(QtGui.QColor(57,66,72)))
            table.horizontalHeaderItem(iCol).setForeground(QtGui.QBrush(Qt.white)) 
    
        
    def buscarClienteById(self, idCliente, cerrarDialog):
        #print("idCliente: " + idCliente)
        #self.clienteId
        filter = "id=" + idCliente

        #QMessageBox.information(None, u'Buscar Cliente', u'Filtro: ' + filter)
        
        iface.activeLayer().removeSelection()
        
        layers = QgsProject.instance().mapLayersByName('clientes - Todos')
        layer = layers[0]
        iface.setActiveLayer(layer)
        
        if(not QgsProject.instance().layerTreeRoot().findGroup("Clientes").isVisible()):
            QgsProject.instance().layerTreeRoot().findGroup("Clientes").setItemVisibilityChecked(True)
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        
        layer.selectByExpression(filter)

        #print(layer.selectedFeatureCount())
        if(layer.selectedFeatureCount() > 0):
            iface.mapCanvas().zoomToSelected()
            if(cerrarDialog):
                self.close()
        else:
            QMessageBox.information(None, u'Buscar Cliente', u'Cliente no encontrado.')
        

    def clienteClicked(self):
        curItem = self.tableClienteWidget.currentItem()
        self.clienteId = self.tableClienteWidget.item(curItem.row(),0).text()
        self.clienteNombre = self.tableClienteWidget.item(curItem.row(),1).text()
        print(self.clienteId)
        print(self.clienteNombre)
        self.txtSelClienteId.setText(self.clienteId)
        self.txtSelClienteNombre.setText(self.clienteNombre)
        self.buscarClienteById(self.clienteId, False)
        
    def buscarClientes(self):
        cliente = self.txtCliente.text()
        filter = "lower(nombre) like lower(\'%" + cliente + "%\')"
        self.buscarClientesByFilter(filter)
         
    def buscarClientesPorDireccion(self):
        direccion = self.txtDireccion.text()
        filter = "lower(direccion) like lower(\'%" + direccion + "%\')"
        self.buscarClientesByFilter(filter)    

    def buscarClientesPorCalleAltura(self):
        calle = self.txtCalle.text()
        altura = self.txtAltura.text()
        filter = "lower(calle) like lower(\'%" + calle + "%\')"
        if(altura):
            filter += " and altura=" + altura
            
        self.buscarClientesByFilter(filter)           
    
    def buscarClientesByFilter(self, filter):      
        layerActivo = iface.activeLayer()
        if(layerActivo):
            layerActivo.removeSelection()    
            
        layers = QgsProject.instance().mapLayersByName('clientes - Todos')
        layer = layers[0]
        iface.setActiveLayer(layer)
        
        if(not QgsProject.instance().layerTreeRoot().findGroup("Clientes").isVisible()):
            QgsProject.instance().layerTreeRoot().findGroup("Clientes").setItemVisibilityChecked(True)
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        
        expresion = QgsExpression(filter)
        request = QgsFeatureRequest(expresion)
        features = layer.getFeatures(request)
        
        layer.selectByExpression(filter)
        cantFeatures = layer.selectedFeatureCount()
        if(cantFeatures > 0):
            iface.mapCanvas().zoomToSelected()
        
        table = self.tableClienteWidget
        table.setRowCount(cantFeatures)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Id", "Nombre", "Direccion", "Calle", "Altura"])
        for iCol in range(table.columnCount()):
            table.horizontalHeaderItem(iCol).setBackground(QtGui.QBrush(QtGui.QColor(57,66,72)))
            table.horizontalHeaderItem(iCol).setForeground(QtGui.QBrush(Qt.white))         
        #table.setVerticalHeaderLabels(["Id", "Nombre", "Direccion"])
        #for feature in features: 
        for idx,feature in enumerate(features):
            #print("Feature:")
            #print(feature.id())
            #print(feature["id"])
            #print(feature["nombre"])
            #print(feature["direccion"])
            item_id = QTableWidgetItem()
            item_id.setData(Qt.EditRole, feature["id"])
            item_id.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            item_nombre = QTableWidgetItem(feature["nombre"])
            direccion = ""
            if(feature["direccion"]):
                direccion = feature["direccion"]
            item_dir = QTableWidgetItem(direccion)
            calle = ""
            if(feature["calle"]):
                calle = feature["calle"]
            item_calle = QTableWidgetItem(calle)
        
            item_altura = QTableWidgetItem()
            altura = 0
            if(feature["altura"]):
                altura = int(feature["altura"])
            item_altura.setData(Qt.DisplayRole,feature["altura"])
            
            table.setItem(idx, 0, item_id)
            table.setItem(idx, 1, item_nombre)
            table.setItem(idx, 2, item_dir)
            table.setItem(idx, 3, item_calle)
            table.setItem(idx, 4, item_altura)
        
        header = table.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        
        QgsProject.instance().layerTreeRoot().findGroup("Clientes").setExpanded(False)
        
        layersCliente = QgsProject.instance().mapLayersByName('clientes')
        layerCliente = layersCliente[0]
        iface.setActiveLayer(layerCliente)
        
        #table.resizeColumnsToContents()
        
        # for j in range(table.columnCount()):
            # table.item(rowIndex, j).setBackground(color)
           
        #item_nombre = QTableWidgetItem("pedro")
        #item_dir = QTableWidgetItem("calle 2 333")
        #item_nombre2 = QTableWidgetItem("juan")
        #item_dir2 = QTableWidgetItem("calle 3 44")
        #item_nombre3 = QTableWidgetItem("jose")
        #item_dir3 = QTableWidgetItem("calle 4 567")
        #item_color.setBackground(get_rgb_from_hex(code))
        #table.setItem(1, 0, item_nombre)
        #table.setItem(1, 1, item_dir)
        #table.setItem(2, 0, item_nombre2)
        #table.setItem(2, 1, item_dir2)
        #table.setItem(3, 0, item_nombre3)
        #table.setItem(3, 1, item_dir3)

    def guardarCliente(self):
        idCliente = self.txtSelClienteId.text()
        print("idCliente: " + idCliente)

        filter = "id=" + idCliente

        #QMessageBox.information(None, u'Buscar Cliente', u'Filtro: ' + filter)
        
        layerActivo = iface.activeLayer()
        if(layerActivo):
            layerActivo.removeSelection()  
        
        layers = QgsProject.instance().mapLayersByName('clientes - Todos')
        layer = layers[0]
        iface.setActiveLayer(layer)
        
        if(not QgsProject.instance().layerTreeRoot().findGroup("Clientes").isVisible()):
            QgsProject.instance().layerTreeRoot().findGroup("Clientes").setItemVisibilityChecked(True)
        
        if(not QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        
        expresion = QgsExpression(filter)
        request = QgsFeatureRequest(expresion)
        features = layer.getFeatures(request)
        
        layer.selectByExpression(filter)
        cantFeatures = layer.selectedFeatureCount()  
        if(cantFeatures > 0):
           feature = next(features)
           featureId = feature["id"]
           docenas = self.sboxDocenas.value()
           nroPao = self.txtNroPao.text()
           tienePedido = 0
           if(self.chkTienePedido.isChecked()):
              tienePedido = 1
           esRegalo = 0
           if(self.chkEsRegalo.isChecked()):
              esRegalo = 1
           observacion = self.txtSelClienteObservacion.text()  
           horario = self.txtHorario.text()
           #print(featureId)
           #print(docenas)
           
           field_idx_cant = layer.fields().indexOf("cantidad")
           field_idx_tiene_pedido = layer.fields().indexOf("tiene_pedido")
           field_idx_nro_pao = layer.fields().indexOf("nro_pao")
           field_idx_es_regalo = layer.fields().indexOf("es_regalo")
           field_idx_observacion = layer.fields().indexOf("observacion")
           field_idx_horario = layer.fields().indexOf("horario")
           
           try:
              #layer.beginEditCommand('Updating cantidad')
              layer.startEditing()
              layer.changeAttributeValue(featureId, field_idx_cant, docenas)
              layer.changeAttributeValue(featureId, field_idx_tiene_pedido, tienePedido)
              if(nroPao):
                layer.changeAttributeValue(featureId, field_idx_nro_pao, nroPao)
              else:
                layer.changeAttributeValue(featureId, field_idx_nro_pao, NULL)
              layer.changeAttributeValue(featureId, field_idx_es_regalo, esRegalo)
              if(observacion):
                layer.changeAttributeValue(featureId, field_idx_observacion, observacion)
              else:
                layer.changeAttributeValue(featureId, field_idx_observacion, NULL)
              if(horario and horario != "::"):
                layer.changeAttributeValue(featureId, field_idx_horario, horario)
              else:
                layer.changeAttributeValue(featureId, field_idx_horario, NULL)
              
              #layer.endEditCommand()
              layer.commitChanges()
              
              print("Registro actualizado: " + str(featureId))
           except e:
              print("Error: " + e)
           
           QgsProject.instance().layerTreeRoot().findGroup("Clientes").setItemVisibilityChecked(False)
           
           layersCliente = QgsProject.instance().mapLayersByName('clientes')
           layerCliente = layersCliente[0]
           iface.setActiveLayer(layerCliente)
           
           iface.mapCanvas().refreshAllLayers()
           
           self.close()
        
        