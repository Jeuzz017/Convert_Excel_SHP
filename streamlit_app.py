if st.button("Proses ke Shapefile"):
        # 1. Konversi ke GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326"
        )

        # 2. Simpan file SHP ke folder sementara di dalam memori
        # Geopandas butuh file fisik untuk menulis shapefile, 
        # jadi kita tulis ke folder '/tmp' (folder sementara di server)
        import os
        gdf.to_file("/tmp/output.shp")
        
        # 3. Masukkan file-file SHP pendukung ke ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in os.listdir("/tmp/"):
                if file.startswith("output."):
                    zf.write(f"/tmp/{file}", file)
        
        # 4. Tampilkan Tombol Unduh
        st.download_button(
            label="Klik untuk Download Shapefile (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="data_spasial.zip",
            mime="application/zip"
        )
        st.success("Data berhasil diproses!")
