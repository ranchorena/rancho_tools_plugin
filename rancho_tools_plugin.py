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
from .pedidos_wfs_tool import PedidosWFSManager
from .pedidos_wfs_config_dialog import PedidosWFSConfigDialog

class RAnchoTools:
    def __init__(self, iface):
        self.iface = iface
        self.pedidos_wfs_manager = PedidosWFSManager()

    def initGui(self):
        self.toolbar = self.iface.addToolBar("RAncho")
        
        iconOpenFile = os.path.join(os.path.dirname(__file__), 'images\open-file-folder_blue.png')
        self.actionAbrirProyecto = QAction(QIcon(iconOpenFile),u"Abrir Proyecto", self.iface.mainWindow())
        self.actionAbrirProyecto.triggered.connect(self.runOpenProjectGeneralBelgrano)
        
        iconBuscar = os.path.join(os.path.dirname(__file__), 'images\buscar_blue_32x32.png')
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
        
        # Nuevas acciones WFS
        iconWFSConfig = os.path.join(os.path.dirname(__file__), 'images\open-file-folder_blue.png')
        self.actionWFSConfig = QAction(QIcon(iconWFSConfig),u"Configurar WFS Pedidos", self.iface.mainWindow())
        self.actionWFSConfig.triggered.connect(self.runWFSConfig)
        
        iconWFSLoad = os.path.join(os.path.dirname(__file__), 'images\list_blue.png')
        self.actionWFSLoad = QAction(QIcon(iconWFSLoad),u"Cargar Pedidos WFS", self.iface.mainWindow())
        self.actionWFSLoad.triggered.connect(self.runWFSLoad)
        
        iconWFSClick = os.path.join(os.path.dirname(__file__), 'images\punto_blue.png')
        self.actionWFSClick = QAction(QIcon(iconWFSClick),u"Activar Click Pedidos", self.iface.mainWindow())
        self.actionWFSClick.triggered.connect(self.runWFSClickTool)
        
        self.toolbar.addAction(self.actionAbrirProyecto)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action)
        self.toolbar.addAction(self.actionCliente)
        self.toolbar.addAction(self.actionPedidos)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionExport)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionPedidosFiltro)
        self.toolbar.addSeparator()
        # Acciones WFS
        self.toolbar.addAction(self.actionWFSConfig)
        self.toolbar.addAction(self.actionWFSLoad)
        self.toolbar.addAction(self.actionWFSClick)
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
        self.menu.addSeparator()
        # Submenu WFS
        self.menu.addAction(self.actionWFSConfig)
        self.menu.addAction(self.actionWFSLoad)
        self.menu.addAction(self.actionWFSClick)
        
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)
        
        # Verificar auto-carga WFS al inicializar
        self.verificarAutoCargarWFS()

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeToolBarIcon(self.actionCliente)
        self.iface.removeToolBarIcon(self.actionPedidos)
        self.iface.removeToolBarIcon(self.actionExport)
        self.iface.removeToolBarIcon(self.actionPedidosFiltro)
        self.iface.removeToolBarIcon(self.actionWFSConfig)
        self.iface.removeToolBarIcon(self.actionWFSLoad)
        self.iface.removeToolBarIcon(self.actionWFSClick)
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
        del self.actionWFSConfig
        del self.actionWFSLoad
        del self.actionWFSClick
        
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
        
    # Métodos WFS
    def runWFSConfig(self):
        """Abrir diálogo de configuración WFS"""
        self.wfs_config_dialog = PedidosWFSConfigDialog()
        if self.wfs_config_dialog.exec_() == QDialog.Accepted:
            # Si se guardó la configuración, verificar si debe auto-cargar
            self.verificarAutoCargarWFS()
    
    def runWFSLoad(self):
        """Cargar la capa WFS de pedidos"""
        import configparser
        import os
        
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'pedidos_wfs_config.ini')
            if not os.path.exists(config_file):
                QMessageBox.warning(None, "Advertencia", 
                                  "No se ha configurado la conexión WFS.\n"
                                  "Use 'Configurar WFS Pedidos' primero.")
                return
            
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if 'WFS' not in config:
                QMessageBox.warning(None, "Advertencia", "Configuración WFS incompleta.")
                return
            
            wfs_url = config.get('WFS', 'url', fallback='')
            layer_name = config.get('WFS', 'layer_name', fallback='')
            
            if not wfs_url or not layer_name:
                QMessageBox.warning(None, "Advertencia", 
                                  "URL del servidor WFS o nombre de capa no configurados.")
                return
            
            # Construir URI completa
            version = config.get('WFS', 'version', fallback='1.1.0')
            usuario = config.get('WFS', 'usuario', fallback='')
            password = config.get('WFS', 'password', fallback='')
            
            wfs_uri = f"url='{wfs_url}' typename='{layer_name}' version='{version}'"
            if usuario and password:
                wfs_uri += f" username='{usuario}' password='{password}'"
            
            # Cargar la capa usando el manager
            if self.pedidos_wfs_manager.cargarCapaWFS(wfs_uri, layer_name):
                # Verificar si debe activar herramienta automáticamente
                if 'DISPLAY' in config and config.getboolean('DISPLAY', 'auto_click_tool', fallback=False):
                    self.pedidos_wfs_manager.activarHerramientaClick()
                    
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al cargar capa WFS: {str(e)}")
    
    def runWFSClickTool(self):
        """Activar herramienta de click para pedidos WFS"""
        self.pedidos_wfs_manager.activarHerramientaClick()
    
    def verificarAutoCargarWFS(self):
        """Verificar si debe auto-cargar la capa WFS al inicio"""
        import configparser
        import os
        
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'pedidos_wfs_config.ini')
            if os.path.exists(config_file):
                config = configparser.ConfigParser()
                config.read(config_file)
                
                if ('DISPLAY' in config and 
                    config.getboolean('DISPLAY', 'auto_cargar', fallback=False)):
                    # Auto-cargar la capa WFS
                    self.runWFSLoad()
                    
        except Exception as e:
            print(f"Error en auto-carga WFS: {e}")     
        