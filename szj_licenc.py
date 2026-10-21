import csv
from datetime import datetime


class LicencSZJ:
    def __init__(self, sku, nev, tipus, ar, darab, kezdete):
        self.sku = sku
        self.nev = nev
        self.tipus = tipus
        self.ar = ar
        self.darab = darab
        self.kezdete = kezdete

    def havi_koltseg_szj(self):
        return self.ar * self.darab

    def eddigi_koltseg_szj(self, datum):
        return self.havi_koltseg_szj() * honapok_szama_szj(self.kezdete, datum)

    def hatralevo_koltseg_szj(self, datum, ea_vege):
        kezdes = max(self.kezdete, datum)
        return self.havi_koltseg_szj() * honapok_szama_szj(kezdes, ea_vege)

    def teljes_koltseg_szj(self, datum, ea_vege):
        return self.eddigi_koltseg_szj(datum) + self.hatralevo_koltseg_szj(datum, ea_vege)


class KeretSZJ:
    def __init__(self, osszeg, elkoltott_szazalek, prepayment_szazalek):
        self.osszeg = osszeg
        self.elkoltott_szazalek = elkoltott_szazalek
        self.prepayment_szazalek = prepayment_szazalek

    def elkoltott_szj(self):
        return self.osszeg * self.elkoltott_szazalek / 100

    def prepayment_szj(self):
        return self.elkoltott_szj() * self.prepayment_szazalek / 100

    def elkoltott_licenc_szj(self):
        return self.elkoltott_szj() - self.prepayment_szj()


def datum_szj(szoveg):
    return datetime.strptime(szoveg.strip(), "%Y-%m-%d").date()


def datum_kiiras_szj(datum):
    return datum.strftime("%Y.%m.%d.")


def honapok_szama_szj(kezdet, veg):
    honapok = (veg.year - kezdet.year) * 12 + veg.month - kezdet.month
    if honapok < 0:
        return 0
    return honapok


def penz_szj(osszeg):
    return f"{osszeg:,.0f} Ft".replace(",", " ")


def keret_betoltese_szj(fajlnev):
    adatok = {}
    with open(fajlnev, "r", encoding="utf-8-sig") as fajl:
        olvaso = csv.reader(fajl, delimiter=";")
        next(olvaso)
        for sor in olvaso:
            if len(sor) == 2:
                adatok[sor[0]] = sor[1]
    return adatok


def licencek_betoltese_szj(fajlnev):
    licencek = []
    with open(fajlnev, "r", encoding="utf-8-sig") as fajl:
        olvaso = csv.reader(fajl, delimiter=";")
        next(olvaso)
        for sor in olvaso:
            if len(sor) == 6:
                licencek.append(LicencSZJ(sor[0], sor[1], sor[2], int(sor[3]), int(sor[4]), datum_szj(sor[5])))
    return licencek


def licencek_mentese_szj(fajlnev, licencek):
    with open(fajlnev, "w", encoding="utf-8-sig", newline="") as fajl:
        iro = csv.writer(fajl, delimiter=";")
        iro.writerow(["SKU", "Termék", "Típus", "Egységár (Ft/fő/hó)", "Darabszám", "Kezdete"])
        for licenc in licencek:
            iro.writerow([licenc.sku, licenc.nev, licenc.tipus, licenc.ar, licenc.darab, licenc.kezdete.strftime("%Y-%m-%d")])


def riport_mentese_szj(fajlnev, licencek, datum, ea_vege):
    with open(fajlnev, "w", encoding="utf-8-sig", newline="") as fajl:
        iro = csv.writer(fajl, delimiter=";")
        iro.writerow(["SKU", "Termék", "Darab", "Havi költség", "Eddigi (időarányos)", "Hátralévő költség", "Teljes EA költség"])
        for licenc in licencek:
            iro.writerow([
                licenc.sku,
                licenc.nev,
                licenc.darab,
                licenc.havi_koltseg_szj(),
                licenc.eddigi_koltseg_szj(datum),
                licenc.hatralevo_koltseg_szj(datum, ea_vege),
                licenc.teljes_koltseg_szj(datum, ea_vege),
            ])
