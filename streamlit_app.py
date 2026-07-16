import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import io
import zipfile
import os

st.title("Aplikasi Konversi Excel ke Poligon")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    # Asumsi: Ada kolom untuk membedakan poligon (misal: 'id_area')
    group_col = st.selectbox("Pilih kolom pengelompokan (ID Poligon):", df.columns)
    lat_col = st.selectbox("Pilih kolom Latitude:", df.columns)
    lon_col = st.selectbox("Pilih kolom Longitude:", df.columns)

    if st.button("Proses ke Poligon (Shapefile)"):
        polygons = []
        # Mengelompokkan data berdasarkan ID
        for id_area, group in df.groupby(group_col):
            # Mengurutkan koordinat (penting agar poligon tidak acak)
            coords = list(zip(group[lon_col], group[lat_col]))
            if len(coords) >= 3: # Poligon minimal harus punya 3 titik
                polygons.append({'id': id_area, 'geometry': Polygon(coords)})
        
        # Membuat GeoDataFrame
        gdf = gpd.GeoDataFrame(polygons, crs="EPSG:4326")
        
        # Simpan ke folder temporary
        gdf.to_file("/tmp/output.shp")
        
        # Kompres ke ZIP untuk download
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in os.listdir("/tmp/"):
                if f.startswith("output."):
                    zf.write(f"/tmp/{f}", f)
        
        st.download_button("Download Poligon (ZIP)", zip_buffer.getvalue(), "poligon.zip", "application/zip")
        st.success("Berhasil diubah ke Poligon!")
