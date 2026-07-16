import streamlit as st
import geopandas as gpd
import pandas as pd
import io
import zipfile

st.title("Aplikasi Konversi Excel ke Shapefile")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    lat_col = st.selectbox("Pilih kolom Latitude:", df.columns)
    lon_col = st.selectbox("Pilih kolom Longitude:", df.columns)

    if st.button("Proses ke Shapefile"):
        # 1. Konversi ke GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326"
        )

        # 2. Simpan ke buffer ZIP (agar bisa didownload sebagai satu kesatuan)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Menyimpan file ke dalam memori zip
            gdf.to_file(zf.open("output.shp", "w"), driver="ESRI Shapefile")
        
        # 3. Tampilkan Tombol Unduh
        st.download_button(
            label="Klik untuk Download Shapefile (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="data_spasial.zip",
            mime="application/zip"
        )
        st.success("Data siap diunduh!")
