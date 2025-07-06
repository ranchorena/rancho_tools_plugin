# encoding: utf-8
# -----------------------------------------------------------
# Herramienta WFS para manejo de pedidos
# -----------------------------------------------------------

from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFeatureRequest, QgsExpression,
    QgsWkbTypes, QgsGeometry, QgsRectangle, QgsNetworkAccessManager
)
from qgis.gui import QgsMapTool, QgsMapCanvas
from qgis.utils import iface
from PyQt5.QtCore import Qt, QUrl, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtGui import QCursor
import requests
import json

class PedidosWFSTool(QgsMapTool):
    """Herramienta para hacer click en pedidos de una capa WFS y mostrar información"""
    
    def __init__(self, canvas, wfs_layer):
        super().__init__(canvas)
        self.canvas = canvas
        self.wfs_layer = wfs_layer
        self.setCursor(QCursor(Qt.CrossCursor))
        
    def canvasReleaseEvent(self, event):
        """Evento cuando se hace click en el canvas"""
        # Obtener el punto clickeado en coordenadas del mapa
        point = self.toMapCoordinates(event.pos())
        
        # Crear un buffer pequeño alrededor del punto para la selección
        tolerance = self.canvas.mapUnitsPerPixel() * 10
        search_rect = QgsRectangle(
            point.x() - tolerance, point.y() - tolerance,
            point.x() + tolerance, point.y() + tolerance
        )
        
        # Buscar features en el área
        request = QgsFeatureRequest()
        request.setFilterRect(search_rect)
        
        features = list(self.wfs_layer.getFeatures(request))
        
        if features:
            # Si hay features, mostrar información del primero
            feature = features[0]
            self.mostrarInfoPedido(feature)
        else:
            QMessageBox.information(None, "Información", "No se encontró ningún pedido en la ubicación seleccionada.")
    
    def mostrarInfoPedido(self, feature):
        """Mostrar información del pedido en un diálogo"""
        dialog = InfoPedidoDialog(feature)
        dialog.exec_()

class InfoPedidoDialog(QDialog):
    """Diálogo para mostrar información del pedido"""
    
    def __init__(self, feature, parent=None):
        super().__init__(parent)
        self.feature = feature
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Información del Pedido")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Obtener información del feature
        pedido_id = self.feature.attribute('id_pedido') or self.feature.attribute('id') or 'N/A'
        nombre = self.feature.attribute('nombre') or 'N/A'
        direccion = self.feature.attribute('direccion') or 'N/A'
        cantidad = self.feature.attribute('cantidad') or 'N/A'
        fecha = self.feature.attribute('fecha') or 'N/A'
        observaciones = self.feature.attribute('observaciones') or 'N/A'
        
        # Crear texto de información
        info_text = f"""
<h3>Información del Pedido</h3>
<b>ID:</b> {pedido_id}<br>
<b>Nombre:</b> {nombre}<br>
<b>Dirección:</b> {direccion}<br>
<b>Cantidad:</b> {cantidad}<br>
<b>Fecha:</b> {fecha}<br>
<b>Observaciones:</b> {observaciones}
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class PedidosWFSManager:
    """Clase para manejar la capa WFS de pedidos"""
    
    def __init__(self):
        self.wfs_layer = None
        self.tool = None
        
    def cargarCapaWFS(self, wfs_uri, layer_name="Pedidos WFS"):
        """Cargar capa WFS de pedidos"""
        try:
            # Crear la capa usando la URI completa que se pasa como parámetro
            self.wfs_layer = QgsVectorLayer(wfs_uri, layer_name, "WFS")
            
            if not self.wfs_layer.isValid():
                QMessageBox.critical(None, "Error", "No se pudo cargar la capa WFS de pedidos.")
                return False
            
            # Agregar al proyecto
            QgsProject.instance().addMapLayer(self.wfs_layer)
            
            # Configurar estilo básico
            self.configurarEstilo()
            
            QMessageBox.information(None, "Éxito", "Capa WFS de pedidos cargada correctamente.")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al cargar capa WFS: {str(e)}")
            return False
    
    def configurarEstilo(self):
        """Configurar el estilo de la capa de pedidos"""
        if self.wfs_layer:
            # Configurar símbolo para puntos de pedidos
            symbol = self.wfs_layer.renderer().symbol()
            symbol.setSize(8)
            symbol.setColor(Qt.red)
            
            # Refrescar la capa
            self.wfs_layer.triggerRepaint()
    
    def activarHerramientaClick(self):
        """Activar la herramienta de click para identificar pedidos"""
        if not self.wfs_layer:
            QMessageBox.warning(None, "Advertencia", "Primero debe cargar la capa WFS de pedidos.")
            return
        
        canvas = iface.mapCanvas()
        self.tool = PedidosWFSTool(canvas, self.wfs_layer)
        canvas.setMapTool(self.tool)
        
        # Activar la capa para asegurar que esté visible
        iface.setActiveLayer(self.wfs_layer)
        
        QMessageBox.information(None, "Herramienta Activada", 
                              "Haga click en cualquier pedido para ver su información.\n"
                              "Para desactivar, seleccione otra herramienta.")
    
    def desactivarHerramientaClick(self):
        """Desactivar la herramienta de click"""
        if self.tool:
            canvas = iface.mapCanvas()
            canvas.unsetMapTool(self.tool)
            self.tool = None
    
    def filtrarPedidosPorFecha(self, fecha_desde, fecha_hasta):
        """Filtrar pedidos por rango de fechas"""
        if not self.wfs_layer:
            QMessageBox.warning(None, "Advertencia", "Primero debe cargar la capa WFS de pedidos.")
            return
        
        # Crear filtro de fecha
        filtro = f"fecha >= '{fecha_desde}' AND fecha <= '{fecha_hasta}'"
        
        # Aplicar filtro
        self.wfs_layer.setSubsetString(filtro)
        
        # Hacer zoom a los pedidos filtrados
        if self.wfs_layer.featureCount() > 0:
            iface.mapCanvas().zoomToLayer(self.wfs_layer)
        else:
            QMessageBox.information(None, "Información", "No se encontraron pedidos en el rango de fechas especificado.")
    
    def obtenerEstadisticas(self):
        """Obtener estadísticas de los pedidos visibles"""
        if not self.wfs_layer:
            return None
        
        total_pedidos = self.wfs_layer.featureCount()
        cantidad_total = 0
        
        # Calcular cantidad total
        for feature in self.wfs_layer.getFeatures():
            cantidad = feature.attribute('cantidad')
            if cantidad:
                cantidad_total += float(cantidad)
        
        return {
            'total_pedidos': total_pedidos,
            'cantidad_total': cantidad_total
        }