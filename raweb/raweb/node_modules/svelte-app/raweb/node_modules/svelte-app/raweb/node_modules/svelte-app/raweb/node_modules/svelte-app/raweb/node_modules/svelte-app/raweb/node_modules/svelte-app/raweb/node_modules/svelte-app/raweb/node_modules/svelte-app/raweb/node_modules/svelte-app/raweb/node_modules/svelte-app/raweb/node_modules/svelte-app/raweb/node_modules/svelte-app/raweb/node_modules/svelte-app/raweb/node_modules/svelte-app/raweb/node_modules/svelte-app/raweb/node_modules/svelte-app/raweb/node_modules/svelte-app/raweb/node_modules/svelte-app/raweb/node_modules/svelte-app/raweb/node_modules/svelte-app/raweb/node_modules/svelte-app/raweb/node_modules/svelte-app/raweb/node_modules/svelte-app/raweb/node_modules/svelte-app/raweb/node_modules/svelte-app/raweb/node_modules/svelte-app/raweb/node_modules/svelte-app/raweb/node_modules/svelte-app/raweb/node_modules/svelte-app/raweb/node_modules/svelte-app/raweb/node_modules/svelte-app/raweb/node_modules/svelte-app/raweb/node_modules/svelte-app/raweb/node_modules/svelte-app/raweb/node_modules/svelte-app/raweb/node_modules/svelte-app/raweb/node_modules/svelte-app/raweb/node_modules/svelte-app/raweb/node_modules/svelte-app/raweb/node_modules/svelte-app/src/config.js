// raweb/src/config.js

// URL base para la API del backend
export const API_BASE_URL = "http://localhost:5000";

// Coordenadas iniciales para el mapa
export const INITIAL_COORDINATES = {
  lon: -58.49442773720401,
  lat: -35.76850886708026
};

// Puedes añadir más variables de configuración aquí en el futuro
// Ejemplo:
// export const MAP_DEFAULT_ZOOM = 15;

// Nota: Para un manejo más robusto de entornos (desarrollo, producción),
// se suele usar un sistema de variables de entorno (.env) con herramientas
// como dotenv y plugins específicos para el bundler (ej. rollup-plugin-dotenv).
// Este archivo config.js es una solución más simple para centralizar la configuración
// sin necesidad de instalar dependencias adicionales en este momento.
