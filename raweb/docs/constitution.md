# Constitución de RAWEB
1. **Stack simple:** mantener Svelte 3, Rollup y OpenLayers; cualquier nueva dependencia o cambio de framework requiere aprobación explícita.
2. **Spec y código:** todo cambio funcional debe responder a una especificación aprobada; actualizarla si cambia el comportamiento acordado.
3. **Lógica e interfaz:** separar cálculos y reglas de negocio en funciones independientes del DOM; los componentes gestionan presentación y eventos.
4. **Verificación sin dependencias:** ejecutar `npm run build` y verificar el flujo afectado en navegador; no instalar herramientas de testing.
5. **Datos del usuario:** no borrar, sobrescribir ni migrar datos sin autorización; no incluir credenciales ni datos personales en código, documentación o logs.
6. **Idioma:** escribir nuevos identificadores en inglés y textos visibles, comentarios y documentación en español; conservar los nombres de contratos existentes.
