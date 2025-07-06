# encoding: utf-8
# -----------------------------------------------------------
# Diálogo de configuración WFS para pedidos
# -----------------------------------------------------------

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt
import configparser
import os

class PedidosWFSConfigDialog(QDialog):
    """Diálogo para configurar la conexión WFS de pedidos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.cargarConfiguracion()
        
    def setupUI(self):
        self.setWindowTitle("Configuración WFS - Pedidos")
        self.setMinimumSize(500, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Grupo de configuración WFS
        wfs_group = QGroupBox("Configuración del Servicio WFS")
        wfs_layout = QFormLayout()
        
        # URL del servidor WFS
        self.txt_wfs_url = QLineEdit()
        self.txt_wfs_url.setPlaceholderText("http://localhost:8080/geoserver/wfs")
        wfs_layout.addRow("URL del Servidor WFS:", self.txt_wfs_url)
        
        # Nombre de la capa
        self.txt_layer_name = QLineEdit()
        self.txt_layer_name.setPlaceholderText("workspace:pedidos")
        wfs_layout.addRow("Nombre de la Capa:", self.txt_layer_name)
        
        # Versión WFS
        self.txt_wfs_version = QLineEdit()
        self.txt_wfs_version.setText("1.1.0")
        wfs_layout.addRow("Versión WFS:", self.txt_wfs_version)
        
        # Usuario (opcional)
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario (opcional)")
        wfs_layout.addRow("Usuario:", self.txt_usuario)
        
        # Contraseña (opcional)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Contraseña (opcional)")
        wfs_layout.addRow("Contraseña:", self.txt_password)
        
        wfs_group.setLayout(wfs_layout)
        main_layout.addWidget(wfs_group)
        
        # Grupo de configuración de visualización
        display_group = QGroupBox("Configuración de Visualización")
        display_layout = QFormLayout()
        
        # Auto cargar al inicio
        self.chk_auto_cargar = QCheckBox()
        display_layout.addRow("Cargar automáticamente al inicio:", self.chk_auto_cargar)
        
        # Tamaño de símbolo
        self.spin_symbol_size = QSpinBox()
        self.spin_symbol_size.setRange(1, 20)
        self.spin_symbol_size.setValue(8)
        display_layout.addRow("Tamaño del símbolo:", self.spin_symbol_size)
        
        # Activar herramienta click automáticamente
        self.chk_auto_click_tool = QCheckBox()
        display_layout.addRow("Activar herramienta click automáticamente:", self.chk_auto_click_tool)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        # Botón probar conexión
        self.btn_probar = QPushButton("Probar Conexión")
        self.btn_probar.clicked.connect(self.probarConexion)
        buttons_layout.addWidget(self.btn_probar)
        
        # Botón guardar
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardarConfiguracion)
        buttons_layout.addWidget(self.btn_guardar)
        
        # Botón cancelar
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancelar)
        
        main_layout.addLayout(buttons_layout)
        
        # Información adicional
        info_label = QLabel(
            "<b>Información:</b><br>"
            "Configure aquí la conexión a su servicio WFS de pedidos.<br>"
            "Asegúrese de que el servidor WFS esté accesible y que la capa contenga<br>"
            "los campos: id, nombre, direccion, cantidad, fecha, observaciones"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
    
    def cargarConfiguracion(self):
        """Cargar configuración guardada"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'pedidos_wfs_config.ini')
            if os.path.exists(config_file):
                config = configparser.ConfigParser()
                config.read(config_file)
                
                if 'WFS' in config:
                    self.txt_wfs_url.setText(config.get('WFS', 'url', fallback=''))
                    self.txt_layer_name.setText(config.get('WFS', 'layer_name', fallback=''))
                    self.txt_wfs_version.setText(config.get('WFS', 'version', fallback='1.1.0'))
                    self.txt_usuario.setText(config.get('WFS', 'usuario', fallback=''))
                    self.txt_password.setText(config.get('WFS', 'password', fallback=''))
                
                if 'DISPLAY' in config:
                    self.chk_auto_cargar.setChecked(config.getboolean('DISPLAY', 'auto_cargar', fallback=False))
                    self.spin_symbol_size.setValue(config.getint('DISPLAY', 'symbol_size', fallback=8))
                    self.chk_auto_click_tool.setChecked(config.getboolean('DISPLAY', 'auto_click_tool', fallback=False))
                    
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    
    def guardarConfiguracion(self):
        """Guardar la configuración"""
        try:
            config = configparser.ConfigParser()
            
            config['WFS'] = {
                'url': self.txt_wfs_url.text(),
                'layer_name': self.txt_layer_name.text(),
                'version': self.txt_wfs_version.text(),
                'usuario': self.txt_usuario.text(),
                'password': self.txt_password.text()
            }
            
            config['DISPLAY'] = {
                'auto_cargar': str(self.chk_auto_cargar.isChecked()),
                'symbol_size': str(self.spin_symbol_size.value()),
                'auto_click_tool': str(self.chk_auto_click_tool.isChecked())
            }
            
            config_file = os.path.join(os.path.dirname(__file__), 'pedidos_wfs_config.ini')
            with open(config_file, 'w') as f:
                config.write(f)
            
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar configuración: {str(e)}")
    
    def probarConexion(self):
        """Probar la conexión WFS"""
        url = self.txt_wfs_url.text().strip()
        layer_name = self.txt_layer_name.text().strip()
        
        if not url or not layer_name:
            QMessageBox.warning(self, "Advertencia", "Debe completar al menos la URL y el nombre de la capa.")
            return
        
        try:
            # Importar aquí para evitar errores en el inicio
            from qgis.core import QgsVectorLayer
            
            # Crear URI de prueba
            wfs_uri = f"url='{url}' typename='{layer_name}' version='{self.txt_wfs_version.text()}'"
            
            # Agregar autenticación si está configurada
            usuario = self.txt_usuario.text().strip()
            password = self.txt_password.text().strip()
            if usuario and password:
                wfs_uri += f" username='{usuario}' password='{password}'"
            
            # Probar crear la capa
            test_layer = QgsVectorLayer(wfs_uri, "Test", "WFS")
            
            if test_layer.isValid():
                feature_count = test_layer.featureCount()
                QMessageBox.information(self, "Éxito", 
                                      f"Conexión exitosa!\n"
                                      f"Capa válida con {feature_count} features.")
            else:
                QMessageBox.critical(self, "Error", 
                                   "No se pudo conectar a la capa WFS.\n"
                                   "Verifique la URL y los parámetros.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al probar conexión: {str(e)}")
    
    def obtenerConfiguracion(self):
        """Obtener la configuración actual como diccionario"""
        return {
            'wfs_url': self.txt_wfs_url.text().strip(),
            'layer_name': self.txt_layer_name.text().strip(),
            'version': self.txt_wfs_version.text().strip(),
            'usuario': self.txt_usuario.text().strip(),
            'password': self.txt_password.text().strip(),
            'auto_cargar': self.chk_auto_cargar.isChecked(),
            'symbol_size': self.spin_symbol_size.value(),
            'auto_click_tool': self.chk_auto_click_tool.isChecked()
        }