# M365 licencnyilvántartó és EA költségtervező

## Hallgató

Szabó János

## Feladat leírása

A program CSV fájlokból beolvassa egy 3 éves Microsoft Enterprise Agreement (2025–2028) Microsoft 365 licenceit és keretét. Kiszámolja a licencek eddigi és a fordulóig hátralévő költségét és megmutatja, hogy a keret elég-e a fordulóig. Új licenc is felvehető, ez a CSV fájlba mentődik.

## Modulok és a modulokban használt függvények

Az indításhoz szükséges modulok (`tkinter`, `datetime`, `csv`) a Python részei, külön telepíteni nem kell semmit.

**tkinter**
- `Tk()`, `title()`, `geometry()`, `resizable()`, `config()`, `bind()`, `mainloop()`, `destroy()`
- `Menu()`, `Frame()`, `Label()`, `Button()`, `Entry()`, `Canvas()`, `ttk.Treeview()`, `ttk.Combobox()`, `ttk.Scrollbar()`
- `messagebox.showinfo()`, `showerror()`, `showwarning()`, `askyesno()`

**datetime** (bemutatandó modul)
- `date.today()`, `datetime.strptime()`, `strftime()`

**csv** 
- `csv.reader()`, `csv.writer()`

**szj_licenc** (saját modul)
- `datum_szj()`, `datum_kiiras_szj()`, `honapok_szama_szj()`, `penz_szj()`
- `keret_betoltese_szj()`, `licencek_betoltese_szj()`, `licencek_mentese_szj()`, `riport_mentese_szj()`

## Osztályok

- `LicencSZJ` – egy licenc adatai és költségei
- `KeretSZJ` – az EA keret és az elköltött összegek
- `M365LicencSZJ` – a program ablaka
