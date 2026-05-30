from flask import Flask, render_template, jsonify, request, send_file
import json, os, io

app = Flask(__name__)
DATA_FILE = "data.json"

DAFTAR_BULAN = {
    "januari":31,"februari":28,"maret":31,"april":30,"mei":31,"juni":30,
    "juli":31,"agustus":31,"september":30,"oktober":31,"november":30,"desember":31
}
URUTAN_BULAN = list(DAFTAR_BULAN.keys())

def baca_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r") as f:
            return json.load(f)
    return {
        "bulan_aktif": "",
        "jumlah_hari": 0,
        "data_keuangan": {},
        "data_ewallet": {},
        "data_tabungan": {"saldo": 0, "riwayat": []}
    }

def tulis_data(d):
    with open(DATA_FILE,"w") as f:
        json.dump(d, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def api_state():
    return jsonify(baca_data())

@app.route("/api/save", methods=["POST"])
def api_save():
    d = request.get_json()
    tulis_data(d)
    return jsonify({"status": "ok"})

# ── Export Excel ──
@app.route("/api/export-excel")
def api_export_excel():
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.chart import BarChart, Reference
    from openpyxl.utils import get_column_letter

    d = baca_data()
    data_keuangan = d.get("data_keuangan", {})
    data_ewallet  = d.get("data_ewallet", {})
    data_tabungan = d.get("data_tabungan", {"saldo": 0, "riwayat": []})

    def hf(c): return PatternFill("solid", fgColor=c)
    def tb():
        s = Side(style="thin", color="CCCCCC")
        return Border(left=s, right=s, top=s, bottom=s)
    def sh(cell, bg="2C3E50", fg="FFFFFF"):
        cell.fill = hf(bg); cell.font = Font(bold=True, color=fg, size=11)
        cell.alignment = Alignment(horizontal="center", vertical="center"); cell.border = tb()
    def sc(cell, align="left", num_fmt=None, bg=None):
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal=align, vertical="center"); cell.border = tb()
        if num_fmt: cell.number_format = num_fmt
        if bg: cell.fill = hf(bg)

    wb = Workbook()
    first = True
    kc = {"kebutuhan": "D5F5E3", "impulsif": "FADBD8", "tabungan": "D6EAF8"}

    # ── Sheet per bulan ──
    for bulan, data in data_keuangan.items():
        ws = wb.active if first else wb.create_sheet()
        ws.title = bulan[:15]; first = False
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 10
        ws.column_dimensions["B"].width = 35
        ws.column_dimensions["C"].width = 16
        ws.column_dimensions["D"].width = 18

        # Judul
        ws["A1"] = f"LAPORAN KEUANGAN — {bulan.upper()}"
        ws["A1"].font = Font(bold=True, size=13, color="FFFFFF")
        ws["A1"].fill = hf("1A5276")
        ws["A1"].alignment = Alignment(horizontal="center")
        ws.merge_cells("A1:D1")

        # Pemasukan
        ws["A3"] = "PEMASUKAN (SAKU)"; ws["A3"].font = Font(bold=True, color="FFFFFF")
        ws["A3"].fill = hf("27AE60"); ws.merge_cells("A3:D3")
        for ci, h in enumerate(["Hari","Keterangan","Jumlah (Rp)"], 1):
            sh(ws.cell(4, ci, h), bg="1E8449")
        ri = 5; total_masuk = 0
        for hari, items in data.get("pemasukan", {}).items():
            for item in items:
                sc(ws.cell(ri,1,hari), align="center")
                sc(ws.cell(ri,2,item["keterangan"]))
                sc(ws.cell(ri,3,item["jumlah"]), align="right", num_fmt="#,##0", bg="E8F8F5")
                total_masuk += item["jumlah"]; ri += 1
        sc(ws.cell(ri,2,"TOTAL PEMASUKAN"), align="right")
        sc(ws.cell(ri,3,total_masuk), align="right", num_fmt="#,##0", bg="D5F5E3")
        ws.cell(ri,2).font = Font(bold=True); ri += 2

        # Pengeluaran
        ws.cell(ri,1,"PENGELUARAN (SAKU)").font = Font(bold=True, color="FFFFFF")
        ws.cell(ri,1).fill = hf("E74C3C"); ws.merge_cells(f"A{ri}:D{ri}"); ri += 1
        for ci, h in enumerate(["Hari","Keterangan","Kategori","Jumlah (Rp)"], 1):
            sh(ws.cell(ri, ci, h), bg="922B21"); ri += 1
        total_keluar = 0; kat_total = {"kebutuhan":0,"impulsif":0,"tabungan":0}
        for hari, items in data.get("pengeluaran", {}).items():
            for item in items:
                kat = item.get("kategori","kebutuhan")
                sc(ws.cell(ri,1,hari), align="center")
                sc(ws.cell(ri,2,item["keterangan"]))
                sc(ws.cell(ri,3,kat.capitalize()), align="center", bg=kc.get(kat,"FFFFFF"))
                sc(ws.cell(ri,4,item["jumlah"]), align="right", num_fmt="#,##0", bg="FADBD8")
                total_keluar += item["jumlah"]; kat_total[kat] += item["jumlah"]; ri += 1
        sc(ws.cell(ri,3,"TOTAL PENGELUARAN"), align="right")
        sc(ws.cell(ri,4,total_keluar), align="right", num_fmt="#,##0", bg="FADBD8")
        ws.cell(ri,3).font = Font(bold=True); ri += 2

        # Ringkasan bulan
        saldo_awal  = data.get("saldo_awal") or 0
        saldo_akhir = saldo_awal + total_masuk - total_keluar
        total_ew    = sum(info.get("saldo",0) for info in data_ewallet.values())
        saldo_total = saldo_akhir + total_ew

        ws.cell(ri,1,"RINGKASAN").font = Font(bold=True, color="FFFFFF")
        ws.cell(ri,1).fill = hf("8E44AD"); ws.merge_cells(f"A{ri}:D{ri}"); ri += 1
        for label, val in [
            ("Saldo Awal (Saku)", saldo_awal),
            ("Pemasukan Saku",    total_masuk),
            ("Pengeluaran Saku",  total_keluar),
            ("Saldo Saku Akhir",  saldo_akhir),
            ("Total E-Wallet",    total_ew),
            ("SALDO TOTAL",       saldo_total),
            ("Saldo Tabungan",    data_tabungan.get("saldo",0)),
        ]:
            sc(ws.cell(ri,1,label))
            sc(ws.cell(ri,2,val), align="right", num_fmt="#,##0",
               bg="D5F5E3" if val>=0 else "FADBD8")
            if label in ("SALDO TOTAL","Saldo Saku Akhir"):
                ws.cell(ri,1).font = Font(bold=True)
                ws.cell(ri,2).font = Font(bold=True)
            ri += 1

    # ── Sheet Ringkasan Semua Bulan ──
    ws2 = wb.create_sheet("Ringkasan Semua Bulan")
    ws2.sheet_view.showGridLines = False
    hdrs = ["Bulan","Saldo Awal","Pemasukan","Pengeluaran","Saldo Saku Akhir","Total E-Wallet","Saldo Total","Status"]
    widths = [14,18,18,18,20,18,18,14]
    for col,(h,w) in enumerate(zip(hdrs,widths),1):
        sh(ws2.cell(1,col,h), bg="1A5276")
        ws2.column_dimensions[get_column_letter(col)].width = w

    total_ew_all = sum(info.get("saldo",0) for info in data_ewallet.values())
    n_bulan = 0
    for ri2,(bulan,data) in enumerate(data_keuangan.items(), 2):
        saldo_awal  = data.get("saldo_awal") or 0
        masuk  = sum(i["jumlah"] for h in data.get("pemasukan",{}).values()  for i in h)
        keluar = sum(i["jumlah"] for h in data.get("pengeluaran",{}).values() for i in h)
        akhir  = saldo_awal + masuk - keluar
        total  = akhir + total_ew_all
        pct    = (akhir/saldo_awal*100) if saldo_awal>0 else 0
        status = "Aman" if pct>=70 else "Waspada" if pct>=40 else "Hampir Habis" if pct>=10 else "Defisit"
        bg_st  = "D5F5E3" if status=="Aman" else "FDEBD0" if status=="Waspada" else "FADBD8"
        for ci,val in enumerate([bulan,saldo_awal,masuk,keluar,akhir,total_ew_all,total,status],1):
            sc(ws2.cell(ri2,ci,val), align="center",
               num_fmt="#,##0" if ci in [2,3,4,5,6,7] else None,
               bg=bg_st if ci==8 else ("F2F3F4" if ri2%2==0 else "FFFFFF"))
        n_bulan += 1

    if n_bulan > 0:
        chart = BarChart(); chart.type = "col"; chart.style = 10
        chart.width = 22; chart.height = 14; chart.title = "Pemasukan vs Pengeluaran"
        chart.add_data(Reference(ws2,min_col=3,max_col=4,min_row=1,max_row=n_bulan+1), titles_from_data=True)
        chart.set_categories(Reference(ws2,min_col=1,min_row=2,max_row=n_bulan+1))
        chart.series[0].graphicalProperties.solidFill = "27AE60"
        chart.series[1].graphicalProperties.solidFill = "E74C3C"
        ws2.add_chart(chart, "J2")

    # ── Sheet E-Wallet ──
    ws3 = wb.create_sheet("E-Wallet Tracker")
    ws3.sheet_view.showGridLines = False
    hdrs3 = ["E-Wallet","Pengguna","Bulan","Jenis","Kategori","Keterangan","Jumlah (Rp)"]
    widths3 = [20,14,14,14,14,35,18]
    for col,(h,w) in enumerate(zip(hdrs3,widths3),1):
        sh(ws3.cell(1,col,h), bg="6C3483")
        ws3.column_dimensions[get_column_letter(col)].width = w
    ri3 = 2
    for nama,info in data_ewallet.items():
        for t in info.get("transaksi",[]):
            row=[nama,info.get("pengguna","-"),t.get("bulan","-"),
                 t.get("jenis","-").capitalize(),t["kategori"].capitalize(),
                 t["keterangan"],t["jumlah"]]
            for ci,val in enumerate(row,1):
                sc(ws3.cell(ri3,ci,val), align="center" if ci<6 else "left",
                   num_fmt="#,##0" if ci==7 else None, bg=kc.get(t["kategori"],"FFFFFF"))
            ri3 += 1

    # ── Sheet Tabungan ──
    ws4 = wb.create_sheet("Tabungan")
    ws4.sheet_view.showGridLines = False
    ws4["A1"] = "RIWAYAT TABUNGAN"
    ws4["A1"].font = Font(bold=True, size=13, color="FFFFFF")
    ws4["A1"].fill = hf("2980B9")
    ws4["A1"].alignment = Alignment(horizontal="center")
    ws4.merge_cells("A1:C1")
    ws4.column_dimensions["A"].width = 16
    ws4.column_dimensions["B"].width = 18
    ws4.column_dimensions["C"].width = 30
    for ci,h in enumerate(["Jenis","Jumlah (Rp)","Keterangan"],1):
        sh(ws4.cell(2,ci,h), bg="2471A3")
    ri4 = 3
    for r in data_tabungan.get("riwayat",[]):
        sc(ws4.cell(ri4,1,r.get("jenis","-").capitalize()), align="center",
           bg="D5F5E3" if r.get("jenis")=="tambah" else "FADBD8")
        sc(ws4.cell(ri4,2,r.get("jumlah",0)), align="right", num_fmt="#,##0")
        sc(ws4.cell(ri4,3,r.get("keterangan","-")))
        ri4 += 1
    ws4.cell(ri4,1,"SALDO TABUNGAN").font = Font(bold=True)
    sc(ws4.cell(ri4,1,"SALDO TABUNGAN"))
    sc(ws4.cell(ri4,2,data_tabungan.get("saldo",0)), align="right", num_fmt="#,##0", bg="D6EAF8")
    ws4.cell(ri4,1).font = Font(bold=True)
    ws4.cell(ri4,2).font = Font(bold=True)

    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, download_name="laporan_edubank.xlsx", as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
