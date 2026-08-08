import io
import os
import tempfile
import zipfile
import geopandas as gpd
import pandas as pd
import streamlit as st
from shapely.geometry import Polygon

st.set_page_config(
    page_title="Konverter Excel ke Shapefile Poligon", page_icon="🗺️"
)

st.title("🗺️ Aplikasi Konversi Excel ke Poligon (Shapefile)")
st.write(
    "Aplikasi ini mengonversi titik koordinat WGS 1984 dari file Excel menjadi file Shapefile poligon."
)

# Upload file Excel
file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

if file:
    # 1. Mengambil nama asli file Excel tanpa ekstensi .xlsx
    base_name = os.path.splitext(file.name)[0]

    df = pd.read_excel(file)

    st.subheader("📋 Preview Data Excel")
    st.dataframe(df.head())

    st.subheader("⚙️ Pengaturan Kolom Data")
    col1, col2, col3 = st.columns(3)

    with col1:
        group_col = st.selectbox(
            "Pilih Kolom ID Poligon (Pengelompokan):", df.columns
        )
    with col2:
        lat_col = st.selectbox("Pilih Kolom Latitude (Y):", df.columns)
    with col3:
        lon_col = st.selectbox("Pilih Kolom Longitude (X):", df.columns)

    if st.button("🚀 Proses ke Poligon (Shapefile)", type="primary"):
        # 2. Validasi & bersihkan data koordinat agar berupa angka
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
        df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
        clean_df = df.dropna(subset=[lat_col, lon_col])

        polygons = []
        skipped_ids = []

        # 3. Mengelompokkan data berdasarkan ID Poligon
        for id_area, group in clean_df.groupby(group_col):
            coords = list(zip(group[lon_col], group[lat_col]))

            # Syarat geometri: Poligon minimal membutuhkan 3 titik koordinat
            if len(coords) >= 3:
                polygons.append(
                    {group_col: id_area, "geometry": Polygon(coords)}
                )
            else:
                skipped_ids.append(str(id_area))

        if not polygons:
            st.error(
                "❌ Gagal membuat poligon. Pastikan setiap ID Poligon memiliki minimal 3 titik koordinat valid."
            )
        else:
            if skipped_ids:
                st.warning(
                    f"⚠️ ID Poligon berikut dilewati karena titiknya kurang dari 3: {', '.join(skipped_ids)}"
                )

            # 4. Membuat GeoDataFrame WGS 1984 (EPSG:4326)
            gdf = gpd.GeoDataFrame(polygons, crs="EPSG:4326")

            # 5. Simpan ke folder temporary dengan nama sesuai file Excel
            with tempfile.TemporaryDirectory() as temp_dir:
                # Membuat path file Shapefile dengan nama asli Excel (misal: data_lahan.shp)
                shp_path = os.path.join(temp_dir, f"{base_name}.shp")

                gdf.to_file(shp_path)

                # 6. Kompres seluruh file hasil ekspor ke format ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(
                    zip_buffer, "w", zipfile.ZIP_DEFLATED
                ) as zf:
                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        zf.write(file_path, arcname=filename)

                st.success(
                    f"✅ Berhasil mengonversi {len(polygons)} data poligon!"
                )

                # 7. Tombol Unduh File ZIP dengan nama sesuai file Excel
                st.download_button(
                    label=f"📦 Download Shapefile ({base_name}.zip)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{base_name}.zip",
                    mime="application/zip",
                )
