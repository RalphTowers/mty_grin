# Mapa Interactivo de la bodiversidad en Monterrey.

Este proyecto genera un mapa interactivo que visualiza patrones de biodiversidad y su relación con áreas verdes urbanas. El mapa incluye datos de aves, anuros y murciélagos, junto con capas de densidad y áreas verdes.

## Características

- Mapa de calor interactivo para visualizar densidad de fauna
- Datos separados para aves, anuros y murciélagos
- Capa de áreas verdes con nombres
- Métricas de biodiversidad (riqueza, abundancia, Shannon-Wiener)
- Puntos pulsantes en áreas de alta densidad
- Múltiples mapas base (oscuro, satélite, relieve, calles)

## Requisitos

```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
.
├── data/
│   ├── aves.csv          # Datos de avistamientos de aves
│   ├── anuros.csv        # Datos de avistamientos de anuros
│   ├── murcis.csv        # Datos de avistamientos de murciélagos
│   └── areas_verdes/     # Shapefile de áreas verdes
├── src/
│   └── heat_map.py       # Script principal para generar el mapa
└── requirements.txt      # Dependencias del proyecto
```

## Uso

1. Clona el repositorio:
```bash
git clone https://github.com/[usuario]/mapa-biodiversidad.git
cd mapa-biodiversidad
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta el script:
```bash
cd src
python heat_map.py
```

4. Abre el archivo `mapa_interactivo_fauna.html` en tu navegador.

## Funcionalidades del Mapa

- **Capas de Densidad**: Visualiza la densidad de fauna total o por grupo
- **Áreas Verdes**: Muestra polígonos de áreas verdes con nombres
- **Puntos de Alta Densidad**: Activa/desactiva puntos pulsantes en zonas de alta concentración
- **Métricas de Biodiversidad**: Panel informativo con estadísticas por grupo
- **Mapas Base**: Elige entre diferentes estilos de mapa

## Créditos

Elaborado por: Rafael Torres Ramírez

## Licencia

Este proyecto está bajo la Licencia MIT. 
