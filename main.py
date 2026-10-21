import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from szj_licenc import (
    LicencSZJ,
    KeretSZJ,
    datum_szj,
    datum_kiiras_szj,
    honapok_szama_szj,
    penz_szj,
    keret_betoltese_szj,
    licencek_betoltese_szj,
    licencek_mentese_szj,
    riport_mentese_szj,
)

LICENC_FAJL = "licencek.csv"
KERET_FAJL = "keret.csv"
RIPORT_FAJL = "riport.csv"
OSZLOPOK = [
    ("sku", "SKU", 80),
    ("nev", "Termék", 300),
    ("tipus", "Típus", 80),
    ("ar", "Ár (Ft/fő/hó)", 90),
    ("darab", "Darab", 55),
    ("kezdete", "Kezdete", 80),
    ("havi", "Havi költség", 115),
    ("eddigi", "Eddigi (időarányos)", 125),
    ("hatralevo", "Hátralévő költség", 125),
    ("teljes", "Teljes EA költség", 125),
]


class M365LicencSZJ:
    def __init__(self, root):
        self.root = root
        self.root.title("M365 licencnyilvántartó és EA költségtervező - Szabó János")
        self.root.geometry("1220x710")
        self.root.resizable(False, False)

        self.licencek = []
        self.ea_kezdete = None
        self.ea_vege = None
        self.datum = None

        self.menu_keszites_szj()
        self.beallitasok_keszites_szj()
        self.tablazat_keszites_szj()
        self.uj_licenc_keszites_szj()
        self.osszesites_keszites_szj()

        self.root.bind("<Return>", self.szamitas_szj)
        self.root.bind("<Escape>", self.kilepes_szj)
        self.tabla.bind("<Double-1>", self.reszletek_szj)

        self.adatok_betoltese_szj()

    def menu_keszites_szj(self):
        menusor = tk.Menu(self.root)

        fajl = tk.Menu(menusor, tearoff=0)
        fajl.add_command(label="CSV adatok újratöltése", command=self.adatok_betoltese_szj)
        fajl.add_command(label="Riport mentése (riport.csv)", command=self.riport_mentes_szj)
        fajl.add_command(label="Kilépés", command=self.kilepes_szj)
        menusor.add_cascade(label="Fájl", menu=fajl)

        sugo = tk.Menu(menusor, tearoff=0)
        sugo.add_command(label="Névjegy", command=self.nevjegy_szj)
        menusor.add_cascade(label="Súgó", menu=sugo)

        self.root.config(menu=menusor)

    def beallitasok_keszites_szj(self):
        keret = tk.Frame(self.root)
        keret.place(x=20, y=15)

        tk.Label(keret, text="Teljes keret (Ft):").grid(row=0, column=0, sticky="w")
        self.keret_mezo = tk.Entry(keret, width=16)
        self.keret_mezo.grid(row=0, column=1, padx=(5, 20))

        tk.Label(keret, text="Elköltött a keretből (%):").grid(row=0, column=2, sticky="w")
        self.elkoltott_mezo = tk.Entry(keret, width=6)
        self.elkoltott_mezo.grid(row=0, column=3, padx=(5, 20))

        tk.Label(keret, text="Ebből Azure prepayment (%):").grid(row=0, column=4, sticky="w")
        self.prepayment_mezo = tk.Entry(keret, width=6)
        self.prepayment_mezo.grid(row=0, column=5, padx=(5, 20))

        tk.Label(keret, text="Számítás dátuma (ÉÉÉÉ-HH-NN):").grid(row=0, column=6, sticky="w")
        self.datum_mezo = tk.Entry(keret, width=12)
        self.datum_mezo.grid(row=0, column=7, padx=(5, 20))

        tk.Button(keret, text="Számítás", width=12, bg="lightblue", command=self.szamitas_szj).grid(row=0, column=8)

        self.ea_cimke = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.ea_cimke.place(x=20, y=50)

    def tablazat_keszites_szj(self):
        tabla_keret = tk.Frame(self.root)
        tabla_keret.place(x=20, y=80)
        self.tabla = ttk.Treeview(tabla_keret, columns=[oszlop[0] for oszlop in OSZLOPOK], show="headings", height=11)
        for azonosito, felirat, szelesseg in OSZLOPOK:
            self.tabla.heading(azonosito, text=felirat)
            if azonosito in ("sku", "nev", "tipus", "kezdete"):
                self.tabla.column(azonosito, width=szelesseg, anchor="w")
            else:
                self.tabla.column(azonosito, width=szelesseg, anchor="e")
        self.tabla.tag_configure("osszesen", font=("Arial", 9, "bold"), background="lightyellow")
        self.tabla.pack(side="left")

        gorgeto = ttk.Scrollbar(tabla_keret, orient="vertical", command=self.tabla.yview)
        gorgeto.pack(side="right", fill="y")
        self.tabla.config(yscrollcommand=gorgeto.set)

    def uj_licenc_keszites_szj(self):
        tk.Label(self.root, text="Új licenc hozzáadása", font=("Arial", 12, "bold")).place(x=20, y=345)
        urlap = tk.Frame(self.root)
        urlap.place(x=20, y=375)

        tk.Label(urlap, text="SKU:").grid(row=0, column=0)
        self.sku_mezo = tk.Entry(urlap, width=11)
        self.sku_mezo.grid(row=0, column=1, padx=(5, 15))

        tk.Label(urlap, text="Termék:").grid(row=0, column=2)
        self.nev_mezo = tk.Entry(urlap, width=35)
        self.nev_mezo.grid(row=0, column=3, padx=(5, 15))

        tk.Label(urlap, text="Típus:").grid(row=0, column=4)
        self.tipus_valaszto = ttk.Combobox(urlap, values=["Alap", "Kiegészítő"], state="readonly", width=10)
        self.tipus_valaszto.current(0)
        self.tipus_valaszto.grid(row=0, column=5, padx=(5, 15))

        tk.Label(urlap, text="Ár (Ft/fő/hó):").grid(row=0, column=6)
        self.ar_mezo = tk.Entry(urlap, width=8)
        self.ar_mezo.grid(row=0, column=7, padx=(5, 15))

        tk.Label(urlap, text="Darab:").grid(row=0, column=8)
        self.darab_mezo = tk.Entry(urlap, width=7)
        self.darab_mezo.grid(row=0, column=9, padx=(5, 15))

        tk.Label(urlap, text="Kezdete:").grid(row=0, column=10)
        self.kezdete_mezo = tk.Entry(urlap, width=11)
        self.kezdete_mezo.grid(row=0, column=11, padx=(5, 15))

        tk.Button(urlap, text="Hozzáadás", width=12, bg="lightgreen", command=self.licenc_hozzaadas_szj).grid(row=0, column=12)

    def osszesites_keszites_szj(self):
        tk.Label(self.root, text="Keret összesítés", font=("Arial", 12, "bold")).place(x=20, y=420)
        self.osszesites = tk.Label(self.root, text="", justify="left", font=("Consolas", 10))
        self.osszesites.place(x=20, y=450)

        tk.Label(self.root, text="Keret felhasználása", font=("Arial", 12, "bold")).place(x=660, y=420)
        self.vaszon = tk.Canvas(self.root, width=540, height=240, bg="white")
        self.vaszon.place(x=660, y=450)

    def adatok_betoltese_szj(self):
        try:
            keret = keret_betoltese_szj(KERET_FAJL)
            self.licencek = licencek_betoltese_szj(LICENC_FAJL)
            self.ea_kezdete = datum_szj(keret["EA_kezdete"])
            self.ea_vege = datum_szj(keret["EA_fordulo"])
        except (FileNotFoundError, KeyError, ValueError):
            messagebox.showerror("Hiba", "A licencek.csv vagy a keret.csv nem található, vagy hibás az adat benne!")
            return

        self.keret_mezo.delete(0, tk.END)
        self.keret_mezo.insert(0, keret["Teljes_keret"])
        self.elkoltott_mezo.delete(0, tk.END)
        self.elkoltott_mezo.insert(0, keret["Elkoltott_szazalek"])
        self.prepayment_mezo.delete(0, tk.END)
        self.prepayment_mezo.insert(0, keret["Prepayment_szazalek"])
        self.datum_mezo.delete(0, tk.END)
        self.datum_mezo.insert(0, date.today().strftime("%Y-%m-%d"))
        self.kezdete_mezo.delete(0, tk.END)
        self.kezdete_mezo.insert(0, date.today().strftime("%Y-%m-%d"))

        self.szamitas_szj()

    def szamitas_szj(self, event=None):
        if self.ea_vege is None:
            return

        try:
            osszeg = float(self.keret_mezo.get().replace(" ", ""))
            elkoltott = float(self.elkoltott_mezo.get())
            prepayment = float(self.prepayment_mezo.get())
            datum = datum_szj(self.datum_mezo.get())
        except ValueError:
            messagebox.showerror("Hiba", "Hibás adat! A számokat számjegyekkel, a dátumot ÉÉÉÉ-HH-NN alakban add meg.")
            return

        if elkoltott < 0 or elkoltott > 100 or prepayment < 0 or prepayment > 100:
            messagebox.showwarning("Figyelmeztetés", "A százalékok 0 és 100 között legyenek!")
            return

        if datum < self.ea_kezdete or datum >= self.ea_vege:
            messagebox.showwarning(
                "Figyelmeztetés",
                f"A számítás dátuma az EA időszakon belül legyen: "
                f"{datum_kiiras_szj(self.ea_kezdete)} - {datum_kiiras_szj(self.ea_vege)}",
            )
            return

        self.datum = datum
        keret = KeretSZJ(osszeg, elkoltott, prepayment)
        self.tabla_frissites_szj()
        self.osszesites_frissites_szj(keret)

    def licenc_hozzaadas_szj(self):
        if self.ea_vege is None:
            return

        sku = self.sku_mezo.get().strip()
        nev = self.nev_mezo.get().strip()
        if sku == "" or nev == "":
            messagebox.showwarning("Figyelmeztetés", "Az SKU és a termék neve nem lehet üres!")
            return

        for licenc in self.licencek:
            if licenc.sku == sku:
                messagebox.showwarning("Figyelmeztetés", "Ilyen SKU már van a listában!")
                return

        try:
            ar = int(self.ar_mezo.get())
            darab = int(self.darab_mezo.get())
            kezdete = datum_szj(self.kezdete_mezo.get())
        except ValueError:
            messagebox.showerror("Hiba", "Az ár és a darab egész szám legyen, a kezdete ÉÉÉÉ-HH-NN alakú dátum!")
            return

        if ar <= 0 or darab <= 0:
            messagebox.showwarning("Figyelmeztetés", "Az ár és a darab 0-nál nagyobb legyen!")
            return

        if kezdete < self.ea_kezdete or kezdete >= self.ea_vege:
            messagebox.showwarning(
                "Figyelmeztetés",
                f"A kezdete az EA időszakon belül legyen: "
                f"{datum_kiiras_szj(self.ea_kezdete)} - {datum_kiiras_szj(self.ea_vege)}",
            )
            return

        self.licencek.append(LicencSZJ(sku, nev, self.tipus_valaszto.get(), ar, darab, kezdete))
        licencek_mentese_szj(LICENC_FAJL, self.licencek)

        self.sku_mezo.delete(0, tk.END)
        self.nev_mezo.delete(0, tk.END)
        self.ar_mezo.delete(0, tk.END)
        self.darab_mezo.delete(0, tk.END)
        self.szamitas_szj()
        messagebox.showinfo("Hozzáadás", f"A(z) {nev} licenc felvéve és elmentve a licencek.csv fájlba.")

    def tabla_frissites_szj(self):
        for sor in self.tabla.get_children():
            self.tabla.delete(sor)

        havi = 0
        eddigi = 0
        hatralevo = 0
        teljes = 0
        for licenc in self.licencek:
            self.tabla.insert("", tk.END, values=(
                licenc.sku,
                licenc.nev,
                licenc.tipus,
                penz_szj(licenc.ar),
                licenc.darab,
                datum_kiiras_szj(licenc.kezdete),
                penz_szj(licenc.havi_koltseg_szj()),
                penz_szj(licenc.eddigi_koltseg_szj(self.datum)),
                penz_szj(licenc.hatralevo_koltseg_szj(self.datum, self.ea_vege)),
                penz_szj(licenc.teljes_koltseg_szj(self.datum, self.ea_vege)),
            ))
            havi += licenc.havi_koltseg_szj()
            eddigi += licenc.eddigi_koltseg_szj(self.datum)
            hatralevo += licenc.hatralevo_koltseg_szj(self.datum, self.ea_vege)
            teljes += licenc.teljes_koltseg_szj(self.datum, self.ea_vege)

        self.tabla.insert("", tk.END, tags=("osszesen",), values=(
            "", "Összesen", "", "", "", "",
            penz_szj(havi), penz_szj(eddigi), penz_szj(hatralevo), penz_szj(teljes),
        ))

    def osszesites_frissites_szj(self, keret):
        osszes_honap = honapok_szama_szj(self.ea_kezdete, self.ea_vege)
        eltelt_honap = honapok_szama_szj(self.ea_kezdete, self.datum)
        hatralevo_honap = honapok_szama_szj(self.datum, self.ea_vege)
        self.ea_cimke.config(
            text=f"EA időszak: {datum_kiiras_szj(self.ea_kezdete)} - {datum_kiiras_szj(self.ea_vege)} "
                 f"({osszes_honap} hónap)    Eltelt: {eltelt_honap} hónap    Hátralévő a fordulóig: {hatralevo_honap} hónap"
        )

        havi = sum(licenc.havi_koltseg_szj() for licenc in self.licencek)
        hatralevo = sum(licenc.hatralevo_koltseg_szj(self.datum, self.ea_vege) for licenc in self.licencek)
        varhato = keret.elkoltott_szj() + hatralevo
        maradek = keret.osszeg - varhato

        sorok = [
            ("Teljes keret:", keret.osszeg),
            (f"Elköltött ({keret.elkoltott_szazalek:g}%):", keret.elkoltott_szj()),
            (f"  ebből Azure prepayment ({keret.prepayment_szazalek:g}%):", keret.prepayment_szj()),
            ("  ebből licenc:", keret.elkoltott_licenc_szj()),
            ("Licencek havi költsége:", havi),
            ("Hátralévő licencköltség a fordulóig:", hatralevo),
            ("Várható összes költség:", varhato),
            ("Maradék keret a fordulóig:", maradek),
        ]
        szoveg = ""
        for nev, ertek in sorok:
            szoveg += f"{nev:<40}{penz_szj(ertek):>22}\n"

        if maradek < 0:
            szoveg += "\nFIGYELEM: a keret a fordulóig nem elég!"
            self.osszesites.config(text=szoveg, fg="red")
        else:
            szoveg += "\nA keret a fordulóig elegendő."
            self.osszesites.config(text=szoveg, fg="darkgreen")

        self.grafikon_rajzolas_szj(keret, hatralevo, maradek)

    def grafikon_rajzolas_szj(self, keret, hatralevo, maradek):
        self.vaszon.delete("all")

        reszek = [
            ("Elköltött licenc", keret.elkoltott_licenc_szj(), "steelblue"),
            ("Azure prepayment (SQL, VM)", keret.prepayment_szj(), "orange"),
            ("Hátralévő licenc a fordulóig", hatralevo, "mediumpurple"),
        ]
        if maradek > 0:
            reszek.append(("Maradék keret", maradek, "lightgreen"))

        osszesen = sum(resz[1] for resz in reszek)
        skala = max(keret.osszeg, osszesen)
        if skala <= 0:
            return

        x = 20
        for nev, ertek, szin in reszek:
            szelesseg = ertek / skala * 500
            self.vaszon.create_rectangle(x, 20, x + szelesseg, 70, fill=szin, outline="white")
            x += szelesseg

        if osszesen > keret.osszeg:
            keret_x = 20 + keret.osszeg / skala * 500
            self.vaszon.create_line(keret_x, 10, keret_x, 80, fill="red", width=3)
            self.vaszon.create_text(keret_x, 90, text="keret vége", fill="red")

        y = 115
        for nev, ertek, szin in reszek:
            szazalek = ertek / keret.osszeg * 100
            self.vaszon.create_rectangle(20, y, 35, y + 15, fill=szin)
            self.vaszon.create_text(45, y + 8, anchor="w", text=f"{nev}: {penz_szj(ertek)} ({szazalek:.1f}%)")
            y += 28

    def reszletek_szj(self, event=None):
        kijelolt = self.tabla.selection()
        if len(kijelolt) == 0:
            return
        sorszam = self.tabla.index(kijelolt[0])
        if sorszam >= len(self.licencek):
            return

        licenc = self.licencek[sorszam]
        messagebox.showinfo(
            licenc.sku,
            f"Termék: {licenc.nev}\n"
            f"Típus: {licenc.tipus}\n"
            f"Egységár: {penz_szj(licenc.ar)} / fő / hó\n"
            f"Darabszám: {licenc.darab}\n"
            f"Kezdete: {datum_kiiras_szj(licenc.kezdete)}\n\n"
            f"Havi költség: {penz_szj(licenc.havi_koltseg_szj())}\n"
            f"Éves költség: {penz_szj(licenc.havi_koltseg_szj() * 12)}\n"
            f"Eddigi (időarányos) költség: {penz_szj(licenc.eddigi_koltseg_szj(self.datum))}\n"
            f"Hátralévő a fordulóig: {penz_szj(licenc.hatralevo_koltseg_szj(self.datum, self.ea_vege))}\n"
            f"Teljes EA költség: {penz_szj(licenc.teljes_koltseg_szj(self.datum, self.ea_vege))}",
        )

    def riport_mentes_szj(self):
        if self.datum is None:
            return
        riport_mentese_szj(RIPORT_FAJL, self.licencek, self.datum, self.ea_vege)
        messagebox.showinfo("Mentés", "A riport elmentve a riport.csv fájlba.")

    def nevjegy_szj(self):
        messagebox.showinfo(
            "Névjegy",
            "M365 licencnyilvántartó és EA költségtervező\nKészítette: Szabó János (SZJ)\nSzkript nyelvek - Python",
        )

    def kilepes_szj(self, event=None):
        if messagebox.askyesno("Kilépés", "Biztosan kilépsz?"):
            self.root.destroy()


root = tk.Tk()
app = M365LicencSZJ(root)
root.mainloop()
