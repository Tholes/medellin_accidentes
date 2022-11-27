import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import Choropleth
from streamlit_folium import st_folium, folium_static
from folium.plugins import HeatMap

df = pd.read_csv('datasets/incidentes_viales.csv', sep=';', encoding='utf-8')

def clean_dataset(df):
    standard_comuna = {
        '1':'01',
        '2':'02',
        '3':'03',
        '4':'04',
        '5':'05',
        '6':'06',
        '7':'07',
        '8':'08',
        '9':'09',
        
    } #I choose this values as the incorrect values taking in mind the text and the beginning of the notebook.

    correct_values = set(['01', '02','03', '04', '05', 
                    '06', '07', '08', '09', '10',
                    '11', '12','13', '14', '15',
                    '16', '50', '60', '70', '80', '90'])

    def clean_columna(columna):
        if columna in correct_values:
            return columna
        elif columna in standard_comuna:
            return standard_comuna[columna]
        return None

    df['NUMCOMUNA'] = df.apply(lambda row: clean_columna(row['NUMCOMUNA']), axis = 1 )
    df.LOCATION = df.LOCATION.str.replace("[","").str.replace("]","").str.split(",")
    df["longitud"] = df.LOCATION.apply(lambda x: x[0]).astype(float)
    df["latitud"] = df.LOCATION.apply(lambda x: x[1]).astype(float)
    return df
def load_map():
    my_bar = st.progress(5)
    global df
    df = clean_dataset(df)
    data_geo = gpd.read_file("https://www.medellin.gov.co/mapas/rest/services/ServiciosPlaneacion/POT48_Base/MapServer/3/query?where=1%3D1&outFields=*&outSR=4326&f=json")
    my_bar.progress(25)
    comuna_count_values = df['NUMCOMUNA'].value_counts().sort_index().to_frame()
    sn02_fila = pd.Series(data={'NUMCOMUNA':0}, name='SN02')
    sn01_fila = pd.Series(data={'NUMCOMUNA':0}, name='SN01')
    comu = comuna_count_values.append(sn02_fila, ignore_index=False)
    comu = comu.append(sn01_fila, ignore_index=False)
    comu['index'] = comu.index
    comu.rename(columns = {'NUMCOMUNA':'Cantidad'}, inplace = True)
    df_final = data_geo.merge(comu, left_on="CODIGO", right_on="index", how="outer") 
    df_final = df_final[['OBJECTID', 'CODIGO', 'NOMBRE', 'geometry', 'Cantidad']]
    df_final.index=map(lambda p : str(p),df_final.index)
    position = df[['latitud', 'longitud', 'COMUNA']]
    # Create a base map
    m = folium.Map(location=[position.latitud.mean(), position.longitud.mean()],zoom_start=11)
    #df_final["Cantidad"].quantile([0, 0.25, 0.5, 0.75, 1])

    bins = list(df_final["Cantidad"].quantile([0, 0.25, 0.5, 0.75, 1]))
    # Add a choropleth map to the base map
    my_bar.progress(50)
    Choropleth(geo_data=df_final.geometry.__geo_interface__, 
            data=df_final.Cantidad, 
            key_on="feature.id", 
            columns=['CODIGO', 'Cantidad'],
            fill_color='YlOrRd', 
            legend_name='Cantidad de accidentes',
            nan_fill_color="White", #Use white color if there is no data available for the county
            fill_opacity=0.7,
            line_opacity=0.1,
            #bins= bins
            ).add_to(m)

    #Add Customized Tooltips to the map
    folium.features.GeoJson(
                        data=df_final,
                        name='Cantidad de accidentes por comuna',
                        smooth_factor=2,
                        style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.01},
                        tooltip=folium.features.GeoJsonTooltip(
                            fields=['CODIGO',
                                    'NOMBRE',
                                    'Cantidad',
                                    
                                ],
                            aliases=["Numero de comuna:",
                                    "Nombre:",
                                    "Cantidad de accidentes:",
                                
                                    ], 
                            localize=True,
                            sticky=False,
                            labels=True,
                            style="""
                                background-color: #F0EFEF;
                                border: 2px solid black;
                                border-radius: 3px;
                                box-shadow: 3px;
                            """,
                            max_width=800,),
                                highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                            ).add_to(m) 
    my_bar.progress(80)
    st_data = folium_static(m)
    my_bar.progress(100)

def main():
    st.title('Mapa interactivo de la accidentalidad en la ciudad de Medellín')
    st.write('Dividido por las comunas de Medellín')
    home = open('markdown/descrip_mapa.md', 'r')
    for line in home.readlines():
        st.write(line)
    load_map()
    home = open('markdown/pie_mapa.md', 'r')
    for line in home.readlines():
        st.write(line)
if __name__ == '__main__':
    main()
