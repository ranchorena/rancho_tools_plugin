# encoding: utf-8
#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qgis.utils import iface
import os
from datetime import datetime, timedelta, date
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorFileWriter, QgsFields, QgsField
import requests

from .buscar_direccion_dialog import BuscarDireccionDialog
from .buscar_cliente_dialog import BuscarClienteDialog
from .pedidos_dialog import PedidosDialog
from .pedidos_filtro_dialog import PedidosFiltroDialog

class RAnchoTools:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.toolbar = self.iface.addToolBar("RAncho")
        
        iconOpenFile = os.path.join(os.path.dirname(__file__), 'images\open-file-folder_blue.png')
        self.actionAbrirProyecto = QAction(QIcon(iconOpenFile),u"Abrir Proyecto", self.iface.mainWindow())
        self.actionAbrirProyecto.triggered.connect(self.runOpenProjectGeneralBelgrano)
        
        iconBuscar = os.path.join(os.path.dirname(__file__), 'images\buscar_blue.png')
        self.action = QAction(QIcon(iconBuscar),u"Buscar Dirección", self.iface.mainWindow())
        #self.action = QAction(u'Buscar Dir', self.iface.mainWindow())
        #self.action.setWhatsThis("Buscar Dirección en el mapa")
        self.action.setStatusTip("Buscar Dirección tip")        
        self.action.triggered.connect(self.runBuscarDireccion)
        
        iconCliente = os.path.join(os.path.dirname(__file__), 'images\punto_blue.png')
        self.actionCliente = QAction(QIcon(iconCliente),u"Buscar Cliente", self.iface.mainWindow())
        self.actionCliente.triggered.connect(self.runBuscarCliente)
        
        iconPedidos = os.path.join(os.path.dirname(__file__), 'images\list_blue.png')
        self.actionPedidos = QAction(QIcon(iconPedidos),u"Pedidos", self.iface.mainWindow())
        self.actionPedidos.triggered.connect(self.runPedidos)
        
        iconExport = os.path.join(os.path.dirname(__file__), 'images\download_blue.png')
        self.actionExport = QAction(QIcon(iconExport),u"Exportar KML", self.iface.mainWindow())
        self.actionExport.triggered.connect(self.runExportarKML)
        
        iconPedidosFiltro = os.path.join(os.path.dirname(__file__), 'images\filter_512x512_blue.png')
        self.actionPedidosFiltro = QAction(QIcon(iconPedidosFiltro),u"Pedidos Filtro", self.iface.mainWindow())
        self.actionPedidosFiltro.triggered.connect(self.runPedidosFiltro)
        
        self.toolbar.addAction(self.actionAbrirProyecto)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action)
        self.toolbar.addAction(self.actionCliente)
        self.toolbar.addAction(self.actionPedidos)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionExport)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionPedidosFiltro)
        #self.iface.addToolBarIcon(self.action)
        
        #agrega el menu al menu de complementos
        self.iface.addPluginToMenu(u"&Buscar Dirección", self.action)
        self.iface.addPluginToMenu(u"&Buscar Cliente", self.actionCliente)
        self.iface.addPluginToMenu(u"&Exportar KML", self.actionExport)
        
        #self.menu = QMenu("&RAncho", self.iface.mainWindow().menuBar())
        #actions = self.iface.mainWindow().menuBar().actions()
        #lastAction = actions[-1]
        #self.iface.mainWindow().menuBar().insertMenu(lastAction, self.menu)
        #
        #mnuSub1 = self.menu.addMenu('Buscar Dirección')
        #mnuSub1.setIcon(QIcon(icon))
        #mnuAction = mnuSub1.addAction(self.action)
        
        self.menu = QMenu(self.iface.mainWindow())
        self.menu.setObjectName("mnuRancho")
        self.menu.setTitle("RAncho")
        self.menu.addAction(self.actionAbrirProyecto)
        self.menu.addSeparator()
        self.menu.addAction(self.action)
        self.menu.addAction(self.actionCliente)
        self.menu.addAction(self.actionPedidos)
        self.menu.addAction(self.actionExport)
        self.menu.addSeparator()
        self.menu.addAction(self.actionPedidosFiltro)
        
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeToolBarIcon(self.actionCliente)
        self.iface.removeToolBarIcon(self.actionPedidos)
        self.iface.removeToolBarIcon(self.actionExport)
        self.iface.removeToolBarIcon(self.actionPedidosFiltro)
        self.menu.deleteLater()
        
        #Elimina el menu al menu de complementos
        self.iface.removePluginMenu(u"&Buscar Dirección", self.action)
        self.iface.removePluginMenu(u"&Buscar Cliente", self.actionCliente)
        self.iface.removePluginMenu(u"&Exportar KML", self.actionExport)
        
        del self.action
        del self.actionCliente
        del self.actionPedidos
        del self.actionExport
        del self.actionPedidosFiltro
        
        del self.toolbar
        del self.menu
        

    def runBuscarDireccion(self):
        self.dialog = BuscarDireccionDialog()
        #dialog.exec_()
        self.dialog.show()
        
    def runBuscarCliente(self):
        self.dialog = BuscarClienteDialog()
        #dialog.exec_()
        self.dialog.show()

    def runPedidos(self):       
        self.dialog = PedidosDialog()
        self.dialog.setWindowFlags(Qt.Window);
        self.dialog.show()        
     
    def runExportarKML(self):
        layers = QgsProject.instance().mapLayersByName('clientes')
        layer = layers[0]
        fechaReparto = datetime.today() + timedelta(days=1)
        fecha = fechaReparto.strftime('%Y%m%d')
        #fecha = datetime.today().strftime('%Y%m%d_%H-%M-%S')
        #fecha = datetime.today().strftime('%Y%m%d')
        #fileName = r"C:/Temp/KML/Clientes_" + fecha + ".kml"
        fileName = r"C:/RA/OneDrive/OneDrive - Geosystems S.A/Documentos/_Administracion/Emprendimientos/Medialunas_Pao/Clientes_KML/Clientes_" + fecha + ".kml"
        crs = QgsCoordinateReferenceSystem("EPSG:4326")    
        
        #fields = QgsFields()
        #fields.append(QgsField("nombre", QVariant.String))
        #fields.append(QgsField("direccion", QVariant.String))
        #fields.append(QgsField("telefono", QVariant.String))
        #fields=[]
        #fields.append("nombre")
        #fields.append("direccion")
        #fields.append("telefono")
        #keeplist = ['nombre', 'direccion', 'telefono']

        datasource_options = []
        datasource_options += ["NameField=nombre"]
        datasource_options += ["DescriptionField=direccion"]
        QgsVectorFileWriter.writeAsVectorFormat(layer, fileName, "utf-8", crs, "KML", False, datasourceOptions = datasource_options)  
        
        QMessageBox.information(None, u'Exportar KML', u'Se ha generado el archivo: ' + fileName)
    
    def runOpenProjectGeneralBelgrano(self):
        project = QgsProject.instance() 
        project.read('C:/RA/OneDrive/OneDrive - Geosystems S.A/RA/QGIS/General Belgrano.qgz')
        print(project.fileName())
        
        layersCliente = QgsProject.instance().mapLayersByName('clientes')
        layerCliente = layersCliente[0]
        iface.setActiveLayer(layerCliente)
        
        canvas = iface.mapCanvas()
        extent = layerCliente.extent()
        canvas.setExtent(extent)
        
    def runPedidosFiltro(self):       
        self.dialog = PedidosFiltroDialog()
        # self.dialog.setWindowFlags(Qt.Window);
        self.dialog.show()     
        