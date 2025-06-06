import pandas as pd
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from math import log
import numpy as np
from collections import Counter
import geopandas as gpd
import json
from shapely.geometry import mapping
from folium.plugins import HeatMapWithTime
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.stats import gaussian_kde
import os

# Establecer el directorio de trabajo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def calcular_metricas(df):
    """
    Calcula métricas de biodiversidad para un conjunto de datos.
    """
    # Riqueza (número de especies únicas)
    riqueza = df['scientific_name'].nunique()
    
    # Abundancia (número total de individuos)
    abundancia = len(df)
    
    # Índice de Shannon-Wiener
    especies_counts = Counter(df['scientific_name'])
    total = sum(especies_counts.values())
    shannon = 0
    for count in especies_counts.values():
        proporcion = count / total
        shannon -= proporcion * log(proporcion, 2)
    
    return {
        'riqueza': riqueza,
        'abundancia': abundancia,
        'shannon': round(shannon, 2)
    }

def crear_caja_info(aves_df, anuros_df, murcis_df):
    """
    Crea una caja HTML con información de biodiversidad.
    """
    # Calcular métricas para cada grupo
    metricas_aves = calcular_metricas(aves_df)
    metricas_anuros = calcular_metricas(anuros_df)
    metricas_murcis = calcular_metricas(murcis_df)
    
    # Combinar todos los datos para métricas totales
    df_total = pd.concat([aves_df, anuros_df, murcis_df])
    metricas_total = calcular_metricas(df_total)
    
    # Crear tabla HTML con estilos
    html = """
    <div style="
        position: fixed;
        bottom: 10px;
        left: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        max-width: 500px;
        z-index: 1000;
    ">
        <h3 style="margin: 0 0 5px 0; color: #333;">Análisis de biodiversidad</h3>
        <p>
        <strong>Elaborado por:</strong> Rafael Torres Ramírez
        </p>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f0f0f0;">
                <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Grupo</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Riqueza<br><small>(especies)</small></th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Abundancia<br><small>(individuos)</small></th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Shannon-Wiener<br><small>(diversidad)</small></th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Fauna</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 8px; border: 1px solid #ddd;">Aves</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Anuros</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 8px; border: 1px solid #ddd;">Murciélagos</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{}</td>
            </tr>
        </table>
        <div style="font-size: 11px; color: #666; margin-top: 8px;">
            <p style="margin: 2px 0;">
                <strong>Riqueza:</strong> Número de especies únicas
            </p>
            <p style="margin: 2px 0;">
                <strong>Abundancia:</strong> Número total de individuos
            </p>
            <p style="margin: 2px 0;">
                <strong>Shannon-Wiener:</strong> Índice de diversidad (mayor valor = mayor diversidad)
            </p>
        </div>
    </div>
    """.format(
        metricas_total['riqueza'], metricas_total['abundancia'], metricas_total['shannon'],
        metricas_aves['riqueza'], metricas_aves['abundancia'], metricas_aves['shannon'],
        metricas_anuros['riqueza'], metricas_anuros['abundancia'], metricas_anuros['shannon'],
        metricas_murcis['riqueza'], metricas_murcis['abundancia'], metricas_murcis['shannon']
    )
    
    return html

def encontrar_hotspots(coordenadas, umbral_densidad=0.75):
    """
    Encuentra puntos de alta densidad usando KDE
    """
    if len(coordenadas) < 3:
        return []
    
    # Calcular la densidad usando KDE
    kde = gaussian_kde(coordenadas.T)
    densidades = kde(coordenadas.T)
    
    # Normalizar las densidades
    densidades = (densidades - densidades.min()) / (densidades.max() - densidades.min())
    
    # Seleccionar puntos con densidad >= umbral
    hotspots_mask = densidades >= umbral_densidad
    hotspots = coordenadas[hotspots_mask]
    
    # Si hay demasiados hotspots, usar DBSCAN para agruparlos
    if len(hotspots) > 0:
        clustering = DBSCAN(eps=0.001, min_samples=2).fit(hotspots)
        centroides = []
        for label in set(clustering.labels_):
            if label != -1:
                mask = clustering.labels_ == label
                cluster_points = hotspots[mask]
                centroide = np.mean(cluster_points, axis=0)
                centroides.append(centroide.tolist())
        return centroides
    return []

def crear_marcador_pulsante(mapa, lat, lon, color='red', radio_min=15):
    """
    Crea un marcador pulsante usando CSS
    """
    html = f'<div class="pulsing-dot"></div>'
    
    return folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            html=html,
            class_name='pulsing-dot-container'
        )
    )

def crear_mapa_interactivo():
    """
    Crear un mapa interactivo con todas las capas de grupos y tipos de mapa base.
    """
    # Leer los archivos CSV
    aves_df = pd.read_csv('aves.csv')
    anuros_df = pd.read_csv('anuros.csv')
    murcis_df = pd.read_csv('murcis.csv')

    # Leer el shapefile de áreas verdes
    areas_verdes = gpd.read_file('resultados/areas_verdes.shp')

    # Obtener coordenadas por grupo
    coords_dict = {
        'Aves': aves_df[['latitude', 'longitude']].values,
        'Anuros': anuros_df[['latitude', 'longitude']].values,
        'Murciélagos': murcis_df[['latitude', 'longitude']].values
    }

    # Combinar todas las coordenadas para la capa total
    todas_coords = np.vstack([coords for coords in coords_dict.values()])

    # Calcular el centro del mapa usando todas las coordenadas
    center_lat = np.mean(todas_coords[:, 0])
    center_lon = np.mean(todas_coords[:, 1])

    # Crear el mapa base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='CartoDB dark_matter'  # Establecer el mapa oscuro como predeterminado
    )

    # Añadir CSS para los puntos pulsantes y el control personalizado
    css = """
        <style>
            @keyframes pulse {
                0% {
                    transform: scale(0.5);
                    opacity: 0;
                }
                50% {
                    opacity: 0.8;
                }
                100% {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            .pulsing-dot {
                width: 15px;
                height: 15px;
                background-color: red;
                border-radius: 50%;
                position: relative;
                box-shadow: 0 0 10px red;
            }
            .pulsing-dot::after {
                content: '';
                position: absolute;
                width: 100%;
                height: 100%;
                background-color: red;
                border-radius: 50%;
                animation: pulse 3s infinite;
                z-index: -1;
                left: 0;
                top: 0;
            }
            .pulsing-dot-container {
                background: none !important;
                border: none !important;
            }
            .custom-control {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                z-index: 1000;
                font-family: Arial, sans-serif;
            }
            .custom-control label {
                display: flex;
                align-items: center;
                gap: 5px;
                cursor: pointer;
            }
            .custom-control input[type="checkbox"] {
                cursor: pointer;
            }
        </style>
        <script>
            function togglePulsingDots(show) {
                const dots = document.querySelectorAll('.pulsing-dot-container');
                dots.forEach(dot => {
                    dot.style.display = show ? 'block' : 'none';
                });
            }
            // Iniciar con los puntos ocultos
            document.addEventListener('DOMContentLoaded', function() {
                togglePulsingDots(false);
            });
        </script>
    """
    m.get_root().header.add_child(folium.Element(css))

    # Añadir diferentes tipos de mapas base
    mapas_base = {
        'Oscuro': 'CartoDB dark_matter',
        'Satélite': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'Relieve': 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        'Calles': 'OpenStreetMap'
    }

    for nombre, tiles in mapas_base.items():
        if nombre != 'Oscuro':  # No añadir el mapa oscuro de nuevo
            if nombre in ['Satélite', 'Relieve']:
                folium.TileLayer(
                    tiles=tiles,
                    attr='Google Maps',
                    name=nombre,
                    overlay=False
                ).add_to(m)
            else:
                folium.TileLayer(
                    tiles=tiles,
                    name=nombre,
                    overlay=False
                ).add_to(m)

    # Configurar el gradiente de colores con más contraste
    gradient = {
        0.2: '#2ecc71',  # verde brillante
        0.4: '#27ae60',  # verde oscuro
        0.6: '#f39c12',  # naranja
        0.8: '#e74c3c',  # rojo
        1.0: '#c0392b'   # rojo oscuro
    }

    # Primero añadir la capa que combina todos los datos (activa por defecto)
    feature_group_total = folium.FeatureGroup(name='Densidad Total de Fauna', show=True)
    HeatMap(
        todas_coords.tolist(),
        radius=15,
        blur=20,
        gradient=gradient,
        min_opacity=0.4,
        max_zoom=13
    ).add_to(feature_group_total)
    
    # Añadir hotspots para la capa total
    hotspots_total = encontrar_hotspots(todas_coords)
    for lat, lon in hotspots_total:
        crear_marcador_pulsante(m, lat, lon).add_to(feature_group_total)
    
    feature_group_total.add_to(m)

    # Crear un grupo de feature para cada tipo de fauna (inactivas por defecto)
    for nombre, coords in coords_dict.items():
        feature_group = folium.FeatureGroup(name=f'Densidad de {nombre}', show=False)
        HeatMap(
            coords.tolist(),
            radius=15,
            blur=20,
            gradient=gradient,
            min_opacity=0.4,
            max_zoom=13
        ).add_to(feature_group)
        
        # Añadir hotspots para cada grupo
        hotspots = encontrar_hotspots(coords)
        for lat, lon in hotspots:
            crear_marcador_pulsante(m, lat, lon).add_to(feature_group)
            
        feature_group.add_to(m)

    # Añadir grupo de áreas verdes
    areas_verdes_group = folium.FeatureGroup(name='Áreas Verdes', show=False)
    
    # Estilo para los tooltips
    tooltip_style = """
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid #333;
    border-radius: 3px;
    box-shadow: 3px 3px 3px rgba(0,0,0,0.2);
    padding: 5px;
    font-family: Arial;
    font-size: 12px;
    """

    # Convertir geometrías a GeoJSON y añadirlas al mapa
    for idx, row in areas_verdes.iterrows():
        # Convertir la geometría a GeoJSON usando shapely.geometry.mapping
        geojson = mapping(row.geometry)
        
        # Crear un nombre para el área
        nombre_area = row.get('nombre', f'Área Verde {idx + 1}')

        # Crear un feature group individual para cada área
        area_group = folium.FeatureGroup(name=nombre_area)
        
        # Añadir el polígono al mapa con tooltip
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'fillColor': '#228B22',
                'color': '#228B22',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_child(folium.Tooltip(
            nombre_area,
            style=tooltip_style
        )).add_to(areas_verdes_group)

    areas_verdes_group.add_to(m)

    # Añadir una leyenda
    colormap = cm.LinearColormap(
        colors=['#2ecc71', '#27ae60', '#f39c12', '#e74c3c', '#c0392b'],
        vmin=0,
        vmax=100,
        caption='Densidad de Fauna'
    )
    colormap.add_to(m)

    # Añadir control de capas
    folium.LayerControl(
        position='topright',
        collapsed=False
    ).add_to(m)

    # Añadir la caja de información
    m.get_root().html.add_child(folium.Element(crear_caja_info(aves_df, anuros_df, murcis_df)))

    # Añadir control personalizado para los puntos pulsantes
    control_html = """
    <div class="custom-control">
        <label>
            <input type="checkbox" onchange="togglePulsingDots(this.checked)">
            Mostrar puntos de alta densidad
        </label>
    </div>
    """
    m.get_root().html.add_child(folium.Element(control_html))

    # Guardar el mapa en la carpeta actual
    m.save('mapa_interactivo_fauna.html')

# Crear el mapa interactivo
if __name__ == '__main__':
    crear_mapa_interactivo()
