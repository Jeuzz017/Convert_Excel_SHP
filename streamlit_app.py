import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

st.title("Aplikasi Konversi Excel ke Shapefile")

# Upload file Excel
file = st.file_uploader("Upload file Excel Anda", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.write("Data Anda:", df.head())
    
    # Pilih kolom koordinat
    lat_col = st.selectbox("Pilih kolom Latitude:", df.columns)
    lon_col = st.selectbox("Pilih kolom Longitude:", df.columns)
    
    if st.button("Proses ke Shapefile"):
        # Konversi ke Geopandas
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326"
        )
        # Simpan sementara
        gdf.to_file("output.shp")
        st.success("Konversi berhasil! File tersedia.")
