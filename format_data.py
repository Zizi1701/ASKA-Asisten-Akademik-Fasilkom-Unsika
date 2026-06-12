import os

def proses_dosen(input_path, output_path):
    print(f"Memproses: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        for baris in f_in:
            baris = baris.strip()
            # Lewati baris kosong atau dekorasi
            if not baris or baris.startswith("===") or "Nama Dosen" in baris or "Total:" in baris or "Format:" in baris:
                continue
            
            # Jika ada separator '|', pecah dan format ulang
            if "|" in baris:
                bagian = [b.strip() for b in baris.split("|")]
                if len(bagian) >= 3:
                    nama, telepon, nidn = bagian[0], bagian[1], bagian[2]
                    # Format RAG-friendly
                    hasil = f"Dosen Fasilkom Unsika bernama {nama} memiliki nomor telepon {telepon} dan NIDN {nidn}.\n"
                    f_out.write(hasil)

def proses_jadwal(input_path, output_path):
    print(f"Memproses: {input_path}")
    hari_saat_ini = ""
    sesi_saat_ini = ""
    
    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        for baris in f_in:
            baris = baris.strip()
            if not baris or baris.startswith("[IF]") or "JADWAL KELAS" in baris:
                continue
                
            # Deteksi Hari
            if baris.startswith("===") and baris.endswith("==="):
                hari_saat_ini = baris.replace("===", "").strip()
                continue
                
            # Deteksi Sesi
            if baris.startswith("SESI"):
                sesi_saat_ini = baris
                continue
                
            # Parsing data jadwal
            if "|" in baris:
                bagian = [b.strip() for b in baris.split("|")]
                if len(bagian) >= 4:
                    kelas, dosen, matkul, ruang = bagian[0], bagian[1], bagian[2], bagian[3]
                    # Bersihkan tanda strip jika tidak ada matkul
                    if matkul == "-":
                        matkul = "Belum ditentukan"
                    if dosen == "-":
                        dosen = "Belum ditentukan"
                        
                    hasil = f"Jadwal hari {hari_saat_ini} {sesi_saat_ini}, Kelas: {kelas}, Mata Kuliah: {matkul}, Dosen: {dosen}, Ruang: {ruang}\n"
                    f_out.write(hasil)

def proses_kalender(input_path, output_path):
    print(f"Memproses: {input_path}")
    kategori_saat_ini = ""
    
    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        for baris in f_in:
            baris = baris.strip()
            if not baris or baris.startswith("===") or baris.startswith("KALENDER") or baris.startswith("TAHUN AKADEMIK"):
                continue
                
            # Jika tidak ada tanda '|', kemungkinan besar ini adalah Judul Kategori atau Catatan
            if "|" not in baris:
                if "Catatan:" in baris or "Perkiraan" in baris:
                    f_out.write(f"Informasi Kalender Akademik: {baris}\n")
                else:
                    kategori_saat_ini = baris
                continue
                
            # Parsing data kegiatan
            if "|" in baris:
                bagian = [b.strip() for b in baris.split("|")]
                if len(bagian) == 2:
                    kiri, kanan = bagian[0], bagian[1]
                    hasil = f"Kategori Kalender: {kategori_saat_ini}. Keterangan: {kiri} - {kanan}\n"
                    f_out.write(hasil)

def main():
    folder_mentah = "data_mentah"
    folder_jadi = "data"
    
    os.makedirs(folder_jadi, exist_ok=True)
    
    # Path file
    file_dosen = "Daftar Dosen Fasilkom Unsika.txt"
    file_jadwal = "Jadwal Kelas Fasilkom Unsika.txt"
    file_kalender = "Kalender Akademik Unsika.txt"
    
    try:
        proses_dosen(os.path.join(folder_mentah, file_dosen), os.path.join(folder_jadi, file_dosen))
        proses_jadwal(os.path.join(folder_mentah, file_jadwal), os.path.join(folder_jadi, file_jadwal))
        proses_kalender(os.path.join(folder_mentah, file_kalender), os.path.join(folder_jadi, file_kalender))
        print("\n✅ Selesai! Semua file tabular berhasil di-flatten dan disimpan di folder 'data/'.")
        print("Silakan jalankan 'python ingest_data.py' sekarang.")
    except FileNotFoundError as e:
        print(f"❌ File tidak ditemukan: {e}. Pastikan Anda menaruh file asli di dalam folder 'data_mentah/'.")

if __name__ == "__main__":
    main()