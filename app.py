import pandas as pd

saldo_awal = 0
bulan_aktif = ""
jumlah_hari = 0

data_keuangan = {}
data_ewallet = {}


# ===== VALIDASI =====
def cek_bulan():
    if bulan_aktif == "":
        print("\nSilakan pilih bulan terlebih dahulu!")
        return False
    return True


# ===== PILIH BULAN =====
def pilih_bulan():
    global bulan_aktif, jumlah_hari

    daftar_bulan = {
        "januari": 31, "februari": 28, "maret": 31,
        "april": 30, "mei": 31, "juni": 30,
        "juli": 31, "agustus": 31, "september": 30,
        "oktober": 31, "november": 30, "desember": 31
    }

    bulan = input("\nPilih bulan (contoh: januari): ").lower()

    if bulan in daftar_bulan:
        bulan_aktif = bulan.capitalize()
        jumlah_hari = daftar_bulan[bulan]

        if bulan_aktif not in data_keuangan:
            data_keuangan[bulan_aktif] = {
                "pemasukan": {},
                "pengeluaran": {}
            }

        print(f"Bulan {bulan_aktif} berhasil dipilih ({jumlah_hari} hari)")
    else:
        print("Bulan tidak valid!")


# ===== INPUT SALDO =====
def input_saldo():
    global saldo_awal
    try:
        saldo_awal = int(input("\nMasukkan saldo awal (contoh: 100000): Rp "))
        print("Saldo berhasil disimpan.")
    except:
        print("Input harus berupa angka!")


# ===== TAMBAH TRANSAKSI =====
def tambah_transaksi():
    if not cek_bulan():
        return

    print("\n=== TAMBAH TRANSAKSI ===")

    try:
        hari = int(input(f"Masukkan hari (1-{jumlah_hari}, contoh: 5): "))
        if hari < 1 or hari > jumlah_hari:
            print("Hari tidak valid!")
            return
    except:
        print("Input harus angka!")
        return

    print("\nJenis transaksi:")
    print("a = pengeluaran (contoh: beli jajan, beli buku)")
    print("b = pemasukan (contoh: uang jajan, hadiah)")

    jenis = input("Masukkan pilihan (a/b): ").lower()
    keterangan = input("Masukkan keterangan (contoh: beli nasi goreng): ")

    try:
        jumlah = int(input("Masukkan jumlah uang (contoh: 10000): Rp "))
    except:
        print("Jumlah harus angka!")
        return

    key = f"Day {hari}"

    if jenis == "a":
        data_keuangan[bulan_aktif]["pengeluaran"].setdefault(key, []).append(
            {"keterangan": keterangan, "jumlah": jumlah}
        )
    elif jenis == "b":
        data_keuangan[bulan_aktif]["pemasukan"].setdefault(key, []).append(
            {"keterangan": keterangan, "jumlah": jumlah}
        )
    else:
        print("Jenis tidak valid!")
        return

    print("Transaksi berhasil ditambahkan.")


# ===== RINGKASAN =====
def ringkasan():
    if not cek_bulan():
        return

    data_bulan = data_keuangan[bulan_aktif]

    masuk = sum(item["jumlah"] for h in data_bulan["pemasukan"].values() for item in h)
    keluar = sum(item["jumlah"] for h in data_bulan["pengeluaran"].values() for item in h)

    akhir = saldo_awal + masuk - keluar

    print(f"\n=== RINGKASAN {bulan_aktif} ===")
    print(f"Pemasukan   : Rp {masuk:,}")
    print(f"Pengeluaran : Rp {keluar:,}")
    print(f"Saldo Akhir : Rp {akhir:,}")

    if saldo_awal == 0:
        print("\nTidak bisa menghitung persentase karena saldo awal = 0")
        return

    persen = (akhir / saldo_awal) * 100
    print(f"Sisa saldo  : {persen:.2f}%")

    if persen >= 70:
        status = "🟢 Aman"
    elif persen >= 40:
        status = "🟡 Waspada"
    elif persen >= 10:
        status = "🟠 Hampir Habis"
    elif persen >= 0:
        status = "🔴 Kritis"
    else:
        status = "❌ Defisit (Pengeluaran melebihi saldo)"

    print(f"Status      : {status}")


# ===== TOTAL PER DAY =====
def total_per_day():
    if not cek_bulan():
        return

    data_bulan = data_keuangan[bulan_aktif]

    print(f"\n=== TOTAL PER DAY ({bulan_aktif}) ===")

    for i in range(1, jumlah_hari + 1):
        key = f"Day {i}"
        masuk = sum(item["jumlah"] for item in data_bulan["pemasukan"].get(key, []))
        keluar = sum(item["jumlah"] for item in data_bulan["pengeluaran"].get(key, []))

        if masuk or keluar:
            print(f"{key} | Masuk: Rp {masuk:,} | Keluar: Rp {keluar:,}")


# ===== EDIT / HAPUS =====
def edit_hapus():
    if not data_keuangan:
        print("\nBelum ada data!")
        return

    print("\n=== EDIT / HAPUS DATA ===")
    bulan_list = list(data_keuangan.keys())
    for i, b in enumerate(bulan_list):
        print(f"{i+1}. {b}")

    try:
        idx = int(input("Masukkan nomor bulan (contoh: 1): ")) - 1
        bulan = bulan_list[idx]
    except:
        print("Input tidak valid!")
        return

    print(f"\nBulan dipilih: {bulan}")
    print("\nPilih jenis:")
    print("a = pengeluaran")
    print("b = pemasukan")

    jenis = input("Masukkan pilihan (a/b): ").lower()

    if jenis == "a":
        kategori = "pengeluaran"
    elif jenis == "b":
        kategori = "pemasukan"
    else:
        print("Pilihan tidak valid!")
        return

    data_bulan = data_keuangan[bulan]
    all_data = []
    for hari in data_bulan[kategori]:
        for item in data_bulan[kategori][hari]:
            all_data.append((hari, item))

    if not all_data:
        print("Tidak ada data.")
        return

    print("\nDaftar data:")
    print("(Nomor | Hari | Keterangan | Jumlah)")
    for i, (h, item) in enumerate(all_data):
        print(f"{i}. {h} | {item['keterangan']} | Rp {item['jumlah']:,}")

    try:
        i = int(input("\nPilih nomor data (contoh: 0): "))
        hari, item = all_data[i]
    except:
        print("Input tidak valid!")
        return

    print("\nPilih aksi:")
    print("e = edit jumlah")
    print("h = hapus data")

    aksi = input("Masukkan pilihan (e/h): ").lower()

    if aksi == "e":
        try:
            jumlah_baru = int(input("Masukkan jumlah baru: Rp "))
            item["jumlah"] = jumlah_baru
            print("Data berhasil diupdate.")
        except:
            print("Harus angka!")
    elif aksi == "h":
        data_bulan[kategori][hari].remove(item)
        print("Data berhasil dihapus.")
    else:
        print("Pilihan tidak valid!")


# ===== E-WALLET TRACKER (BARU) =====
def kelola_ewallet():
    print("\n===== E-WALLET TRACKER =====")
    print("1. Input saldo e-wallet")
    print("2. Catat pengeluaran e-wallet")
    print("3. Lihat ringkasan e-wallet")
    print("4. Simulasi nabung dari e-wallet")

    pilihan = input("Pilih menu: ")

    if pilihan == "1":
        input_saldo_ewallet()
    elif pilihan == "2":
        catat_pengeluaran_ewallet()
    elif pilihan == "3":
        ringkasan_ewallet()
    elif pilihan == "4":
        simulasi_nabung_ewallet()
    else:
        print("Pilihan tidak valid!")


def input_saldo_ewallet():
    print("\n=== INPUT SALDO E-WALLET ===")
    daftar = ["GoPay", "ShopeePay", "DANA", "OVO", "LinkAja"]
    for i, nama in enumerate(daftar):
        print(f"{i+1}. {nama}")

    try:
        idx = int(input("Pilih e-wallet (contoh: 1): ")) - 1
        nama_ewallet = daftar[idx]
        saldo = int(input(f"Masukkan saldo {nama_ewallet}: Rp "))

        if nama_ewallet not in data_ewallet:
            data_ewallet[nama_ewallet] = {"saldo": 0, "transaksi": []}

        data_ewallet[nama_ewallet]["saldo"] = saldo
        print(f"Saldo {nama_ewallet} berhasil disimpan: Rp {saldo:,}")
    except:
        print("Input tidak valid!")


def catat_pengeluaran_ewallet():
    if not data_ewallet:
        print("\nBelum ada e-wallet! Input saldo dulu.")
        return

    print("\n=== CATAT PENGELUARAN E-WALLET ===")
    daftar = list(data_ewallet.keys())
    for i, nama in enumerate(daftar):
        print(f"{i+1}. {nama} (Saldo: Rp {data_ewallet[nama]['saldo']:,})")

    try:
        idx = int(input("Pilih e-wallet: ")) - 1
        nama_ewallet = daftar[idx]
    except:
        print("Input tidak valid!")
        return

    keterangan = input("Keterangan (contoh: beli baju flash sale): ")

    print("\nKategori pengeluaran:")
    print("1. Kebutuhan  (makan, transport, bayar tagihan)")
    print("2. Impulsif   (flash sale, jajan random, hiburan)")
    print("3. Tabungan   (transfer ke rekening, investasi)")

    try:
        kat = int(input("Pilih kategori (1/2/3): "))
        kategori_map = {1: "kebutuhan", 2: "impulsif", 3: "tabungan"}
        if kat not in kategori_map:
            print("Kategori tidak valid!")
            return
        kategori = kategori_map[kat]
        jumlah = int(input("Jumlah pengeluaran: Rp "))
    except:
        print("Input tidak valid!")
        return

    data_ewallet[nama_ewallet]["saldo"] -= jumlah
    data_ewallet[nama_ewallet]["transaksi"].append({
        "keterangan": keterangan,
        "kategori": kategori,
        "jumlah": jumlah
    })

    print(f"\nPengeluaran tercatat!")
    print(f"Sisa saldo {nama_ewallet}: Rp {data_ewallet[nama_ewallet]['saldo']:,}")


def ringkasan_ewallet():
    if not data_ewallet:
        print("\nBelum ada data e-wallet!")
        return

    print("\n=== RINGKASAN E-WALLET ===")

    total_saldo = 0
    total_impulsif = 0
    total_kebutuhan = 0
    total_tabungan = 0
    total_keluar = 0

    for nama, info in data_ewallet.items():
        impulsif  = sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "impulsif")
        kebutuhan = sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "kebutuhan")
        tabungan  = sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "tabungan")

        print(f"\n{nama}")
        print(f"  Saldo saat ini : Rp {info['saldo']:,}")
        print(f"  Kebutuhan      : Rp {kebutuhan:,}")
        print(f"  Impulsif       : Rp {impulsif:,}")
        print(f"  Tabungan       : Rp {tabungan:,}")

        total_saldo    += info["saldo"]
        total_impulsif += impulsif
        total_kebutuhan+= kebutuhan
        total_tabungan += tabungan
        total_keluar   += impulsif + kebutuhan + tabungan

    print(f"\n=== TOTAL SEMUA E-WALLET ===")
    print(f"Total saldo tersisa : Rp {total_saldo:,}")
    print(f"Total kebutuhan     : Rp {total_kebutuhan:,}")
    print(f"Total impulsif      : Rp {total_impulsif:,}")
    print(f"Total tabungan      : Rp {total_tabungan:,}")

    if total_keluar > 0:
        persen_impulsif = (total_impulsif / total_keluar) * 100
        print(f"\nPengeluaran impulsif : {persen_impulsif:.1f}%")

        if persen_impulsif >= 50:
            print("⚠️  PERINGATAN: Lebih dari setengah uang e-wallet habis buat hal impulsif!")
            print("💡 Saran: Sisihkan minimal 20% saldo e-wallet ke tabungan sebelum belanja.")
        elif persen_impulsif >= 30:
            print("⚠️  WASPADA: Pengeluaran impulsif cukup tinggi.")
            print("💡 Saran: Tahan diri dari flash sale. Tanya dulu, 'Butuh atau cuma mau?'")
        else:
            print("✅  Bagus! Pengeluaran e-wallet kamu cukup terkontrol.")


def simulasi_nabung_ewallet():
    print("\n=== SIMULASI NABUNG DARI E-WALLET ===")
    try:
        target    = int(input("Masukkan target tabungan (contoh: 500000): Rp "))
        per_bulan = int(input("Sanggup sisihkan berapa dari e-wallet per bulan? Rp "))

        if per_bulan <= 0:
            print("Jumlah harus lebih dari 0!")
            return

        bulan = target // per_bulan
        sisa  = target % per_bulan

        print(f"\nTarget    : Rp {target:,}")
        print(f"Per bulan : Rp {per_bulan:,}")
        print(f"Estimasi  : {bulan} bulan {'+1 bulan' if sisa > 0 else ''}")

        if bulan <= 3:
            print("🚀 Target sangat realistis! Semangat!")
        elif bulan <= 6:
            print("💪 Butuh kesabaran, tapi bisa! Jangan tergoda flash sale ya.")
        else:
            print(f"📈 Lumayan lama. Coba naikkan sisihan per bulan biar lebih cepat.")
    except:
        print("Input tidak valid!")


# ===== GRAFIK DI COLAB (BARU) =====
def tampilkan_grafik():
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"📊 Dashboard EduBank - {bulan_aktif if bulan_aktif else 'Semua Data'}",
                 fontsize=15, fontweight="bold", color="#2C3E50")
    fig.patch.set_facecolor("#F8F9FA")

    # ===== PIE CHART: Pengeluaran per hari =====
    ax1 = axes[0]
    ax1.set_facecolor("#F8F9FA")

    labels, values = [], []
    if bulan_aktif and bulan_aktif in data_keuangan:
        for hari, items in data_keuangan[bulan_aktif]["pengeluaran"].items():
            total = sum(i["jumlah"] for i in items)
            if total > 0:
                labels.append(hari)
                values.append(total)

    if values:
        colors = plt.cm.Set3.colors[:len(values)]
        wedges, texts, autotexts = ax1.pie(
            values, labels=labels, autopct="%1.1f%%",
            startangle=90, colors=colors,
            wedgeprops={"edgecolor": "white", "linewidth": 2}
        )
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color("#2C3E50")
        ax1.set_title("Pengeluaran per Hari", fontsize=12,
                      fontweight="bold", color="#2C3E50", pad=15)
    else:
        ax1.text(0.5, 0.5, "Belum ada\ndata pengeluaran",
                 ha="center", va="center", transform=ax1.transAxes,
                 fontsize=12, color="#7F8C8D")
        ax1.set_title("Pengeluaran per Hari", fontsize=12,
                      fontweight="bold", color="#2C3E50", pad=15)

    # ===== BAR CHART: E-wallet breakdown =====
    ax2 = axes[1]
    ax2.set_facecolor("#F8F9FA")

    ew_labels, ew_kebutuhan, ew_impulsif, ew_tabungan = [], [], [], []
    for nama, info in data_ewallet.items():
        ew_labels.append(nama)
        ew_kebutuhan.append(sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "kebutuhan"))
        ew_impulsif.append(sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "impulsif"))
        ew_tabungan.append(sum(t["jumlah"] for t in info["transaksi"] if t["kategori"] == "tabungan"))

    if ew_labels:
        x = np.arange(len(ew_labels))
        width = 0.25
        bars1 = ax2.bar(x - width, ew_kebutuhan, width, label="Kebutuhan",
                        color="#27AE60", edgecolor="white", linewidth=1.5)
        bars2 = ax2.bar(x,          ew_impulsif,  width, label="Impulsif",
                        color="#E74C3C", edgecolor="white", linewidth=1.5)
        bars3 = ax2.bar(x + width,  ew_tabungan,  width, label="Tabungan",
                        color="#2980B9", edgecolor="white", linewidth=1.5)

        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax2.text(bar.get_x() + bar.get_width() / 2, h + 500,
                             f"{int(h):,}", ha="center", va="bottom",
                             fontsize=8, color="#2C3E50")

        ax2.set_xticks(x)
        ax2.set_xticklabels(ew_labels, fontsize=10)
        ax2.set_title("Pengeluaran E-Wallet per Kategori", fontsize=12,
                      fontweight="bold", color="#2C3E50", pad=15)
        ax2.set_ylabel("Jumlah (Rp)", color="#2C3E50")
        ax2.legend(fontsize=9)
        ax2.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda val, _: f"Rp {int(val):,}")
        )
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
    else:
        ax2.text(0.5, 0.5, "Belum ada\ndata e-wallet",
                 ha="center", va="center", transform=ax2.transAxes,
                 fontsize=12, color="#7F8C8D")
        ax2.set_title("Pengeluaran E-Wallet per Kategori", fontsize=12,
                      fontweight="bold", color="#2C3E50", pad=15)

    plt.tight_layout(pad=3.0)
    plt.show()
    print("Grafik berhasil ditampilkan!")


# ===== EXPORT EXCEL (DIPERCANTIK) =====
def export_excel():
    import os
    from openpyxl import load_workbook
    from openpyxl.styles import (
        PatternFill, Font, Alignment, Border, Side
    )
    from openpyxl.chart import BarChart, Reference
    from openpyxl.chart.series import DataPoint
    from openpyxl.utils import get_column_letter

    rows = []
    summary = {}

    for bulan in data_keuangan:
        masuk = keluar = 0
        for jenis in data_keuangan[bulan]:
            for hari in data_keuangan[bulan][jenis]:
                for item in data_keuangan[bulan][jenis][hari]:
                    rows.append({
                        "Bulan": bulan,
                        "Hari": hari,
                        "Jenis": jenis.capitalize(),
                        "Keterangan": item["keterangan"],
                        "Jumlah (Rp)": item["jumlah"]
                    })
                    if jenis == "pemasukan":
                        masuk += item["jumlah"]
                    else:
                        keluar += item["jumlah"]
        summary[bulan] = (masuk, keluar)

    # Tambahkan data e-wallet ke rows
    ew_rows = []
    for nama, info in data_ewallet.items():
        for t in info["transaksi"]:
            ew_rows.append({
                "E-Wallet": nama,
                "Kategori": t["kategori"].capitalize(),
                "Keterangan": t["keterangan"],
                "Jumlah (Rp)": t["jumlah"]
            })

    if not rows and not ew_rows:
        print("Belum ada data!")
        return

    path = os.path.join(os.getcwd(), "laporan_edubank.xlsx")

    # Helper styles
    def header_fill(hex_color):
        return PatternFill("solid", fgColor=hex_color)

    def thin_border():
        s = Side(style="thin", color="CCCCCC")
        return Border(left=s, right=s, top=s, bottom=s)

    def style_header(cell, bg="2C3E50", fg="FFFFFF", size=11):
        cell.fill = header_fill(bg)
        cell.font = Font(bold=True, color=fg, size=size)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border()

    def style_cell(cell, bold=False, align="left", num_fmt=None, bg=None):
        cell.font = Font(bold=bold, size=10)
        cell.alignment = Alignment(horizontal=align, vertical="center")
        cell.border = thin_border()
        if num_fmt:
            cell.number_format = num_fmt
        if bg:
            cell.fill = header_fill(bg)

    from openpyxl import Workbook
    wb = Workbook()

    # =====================================================
    # SHEET 1: Data Transaksi
    # =====================================================
    ws1 = wb.active
    ws1.title = "Data Transaksi"
    ws1.sheet_view.showGridLines = False
    ws1.row_dimensions[1].height = 30

    headers = ["Bulan", "Hari", "Jenis", "Keterangan", "Jumlah (Rp)"]
    col_widths = [14, 10, 14, 35, 18]

    for col, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws1.cell(row=1, column=col, value=h)
        style_header(cell)
        ws1.column_dimensions[get_column_letter(col)].width = w

    jenis_colors = {"Pemasukan": "E8F8F5", "Pengeluaran": "FDEDEC"}
    for row_idx, row in enumerate(rows, 2):
        bg = jenis_colors.get(row["Jenis"], "FFFFFF")
        values = list(row.values())
        for col_idx, val in enumerate(values, 1):
            cell = ws1.cell(row=row_idx, column=col_idx, value=val)
            num_fmt = '#,##0' if col_idx == 5 else None
            style_cell(cell, align="center" if col_idx < 4 else "left",
                       num_fmt=num_fmt, bg=bg)
        ws1.row_dimensions[row_idx].height = 20

    # =====================================================
    # SHEET 2: Ringkasan Bulanan
    # =====================================================
    ws2 = wb.create_sheet("Ringkasan Bulanan")
    ws2.sheet_view.showGridLines = False
    ws2.row_dimensions[1].height = 30

    headers2 = ["Bulan", "Pemasukan (Rp)", "Pengeluaran (Rp)", "Saldo Akhir (Rp)", "Status"]
    col_widths2 = [16, 20, 20, 20, 16]

    for col, (h, w) in enumerate(zip(headers2, col_widths2), 1):
        cell = ws2.cell(row=1, column=col, value=h)
        style_header(cell, bg="1A5276")
        ws2.column_dimensions[get_column_letter(col)].width = w

    for row_idx, (bulan, (masuk, keluar)) in enumerate(summary.items(), 2):
        akhir = saldo_awal + masuk - keluar
        if akhir >= 0:
            status = "Aman" if (akhir / max(saldo_awal, 1) * 100) >= 70 else "Waspada"
            bg_status = "D5F5E3" if status == "Aman" else "FDEBD0"
        else:
            status = "Defisit"
            bg_status = "FADBD8"

        row_data = [bulan, masuk, keluar, akhir, status]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            num_fmt = '#,##0' if col_idx in [2, 3, 4] else None
            bg = bg_status if col_idx == 5 else ("F2F3F4" if row_idx % 2 == 0 else "FFFFFF")
            style_cell(cell, align="center", num_fmt=num_fmt, bg=bg)
        ws2.row_dimensions[row_idx].height = 22

    # Bar chart ringkasan
    if summary:
        chart = BarChart()
        chart.type = "col"
        chart.grouping = "clustered"
        chart.title = "Pemasukan vs Pengeluaran per Bulan"
        chart.y_axis.title = "Jumlah (Rp)"
        chart.x_axis.title = "Bulan"
        chart.style = 10
        chart.width = 20
        chart.height = 14

        data_ref = Reference(ws2, min_col=2, max_col=3,
                             min_row=1, max_row=len(summary) + 1)
        cats = Reference(ws2, min_col=1,
                         min_row=2, max_row=len(summary) + 1)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats)
        chart.series[0].graphicalProperties.solidFill = "27AE60"
        chart.series[1].graphicalProperties.solidFill = "E74C3C"
        ws2.add_chart(chart, "G2")

    # =====================================================
    # SHEET 3: E-Wallet Tracker
    # =====================================================
    ws3 = wb.create_sheet("E-Wallet Tracker")
    ws3.sheet_view.showGridLines = False
    ws3.row_dimensions[1].height = 30

    headers3 = ["E-Wallet", "Kategori", "Keterangan", "Jumlah (Rp)"]
    col_widths3 = [16, 16, 35, 18]
    kat_colors = {"Kebutuhan": "D5F5E3", "Impulsif": "FADBD8", "Tabungan": "D6EAF8"}

    for col, (h, w) in enumerate(zip(headers3, col_widths3), 1):
        cell = ws3.cell(row=1, column=col, value=h)
        style_header(cell, bg="6C3483")
        ws3.column_dimensions[get_column_letter(col)].width = w

    if ew_rows:
        for row_idx, row in enumerate(ew_rows, 2):
            bg = kat_colors.get(row["Kategori"], "FFFFFF")
            values = list(row.values())
            for col_idx, val in enumerate(values, 1):
                cell = ws3.cell(row=row_idx, column=col_idx, value=val)
                num_fmt = '#,##0' if col_idx == 4 else None
                style_cell(cell, align="center" if col_idx < 3 else "left",
                           num_fmt=num_fmt, bg=bg)
            ws3.row_dimensions[row_idx].height = 20

        # Ringkasan per kategori e-wallet
        start_summary = len(ew_rows) + 3
        ws3.cell(row=start_summary, column=1, value="Ringkasan Kategori").font = \
            Font(bold=True, size=11, color="6C3483")

        total_kat = {"Kebutuhan": 0, "Impulsif": 0, "Tabungan": 0}
        for r in ew_rows:
            total_kat[r["Kategori"]] += r["Jumlah (Rp)"]

        for i, (kat, total) in enumerate(total_kat.items()):
            r = start_summary + 1 + i
            ws3.cell(row=r, column=1, value=kat)
            cell_total = ws3.cell(row=r, column=2, value=total)
            cell_total.number_format = '#,##0'
            ws3.cell(row=r, column=1).fill = header_fill(
                kat_colors.get(kat, "FFFFFF").replace("#", ""))
    else:
        ws3.cell(row=2, column=1, value="Belum ada data e-wallet")

    wb.save(path)
    print(f"\n✅ Export berhasil!")
    print(f"📁 File: laporan_edubank.xlsx")
    print(f"   Sheet 1: Data Transaksi (warna per jenis)")
    print(f"   Sheet 2: Ringkasan Bulanan + Grafik bar chart")
    print(f"   Sheet 3: E-Wallet Tracker (warna per kategori)")


# ===== MENU UTAMA =====
while True:
    print("╔══════════════════════╗")
    print("║       EDUBANK        ║")
    print("╠══════════════════════╣")
    print("║ 1.  Pilih Bulan      ║")
    print("║ 2.  Input Saldo      ║")
    print("║ 3.  Tambah Transaksi ║")
    print("║ 4.  Ringkasan        ║")
    print("║ 5.  Total Per Day    ║")
    print("║ 6.  Edit / Hapus     ║")
    print("║ 7.  Export Excel     ║")
    print("║ 8.  E-Wallet Tracker ║")
    print("║ 9.  Tampilkan Grafik ║")
    print("║ 10. Keluar           ║")
    print("╚══════════════════════╝")

    p = input("Pilih menu: ")

    if p == "1":
        pilih_bulan()
    elif p == "2":
        input_saldo()
    elif p == "3":
        tambah_transaksi()
    elif p == "4":
        ringkasan()
    elif p == "5":
        total_per_day()
    elif p == "6":
        edit_hapus()
    elif p == "7":
        export_excel()
    elif p == "8":
        kelola_ewallet()
    elif p == "9":
        tampilkan_grafik()
    elif p == "10":
        print("\nTerima kasih sudah pakai EduBank! 💰")
        break
    else:
        print("Pilihan tidak valid.")
