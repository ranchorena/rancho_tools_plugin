@echo off
call "C:\Program Files\QGIS 3.16\bin\o4w_env.bat"
call "C:\Program Files\QGIS 3.16\bin\qt5_env.bat"
call "C:\Program Files\QGIS 3.16\bin\py3_env.bat"

@echo on
"C:\Program Files\QGIS 3.16\apps\Python37\Scripts\pyrcc5" -o "C:\Users\Admin\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\rancho_tools_plugin\resources.py" "C:\Users\Admin\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\rancho_tools_plugin\resources.qrc"