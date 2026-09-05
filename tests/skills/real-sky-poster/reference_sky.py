"""Regenerate reference CSV from downloaded V/50 catalog.gz and de421.bsp.

Usage: python reference_sky.py INPUT_DIRECTORY > reference-sky.csv
Requires isolated Skyfield 1.54; never imports Rafiki's calculation/catalogue.
"""
import csv
import gzip
import hashlib
import importlib.metadata
import sys
from pathlib import Path

from skyfield.api import Star, load, load_file, wgs84

HR = {424: "Polaris", 4301: "Dubhe", 4295: "Merak", 4554: "Phecda",
      4660: "Megrez", 4905: "Alioth", 5054: "Mizar", 5191: "Alkaid",
      2061: "Betelgeuse", 1790: "Bellatrix", 1713: "Rigel", 2004: "Saiph"}
source = Path(sys.argv[1])
for name in ("catalog.gz", "de421.bsp"):
    print(f"# {name} sha256: {hashlib.sha256((source / name).read_bytes()).hexdigest()}")
for name in ("skyfield", "numpy", "jplephem", "sgp4"):
    print(f"# {name}: {importlib.metadata.version(name)}")
print("# Sources: https://cdsarc.cds.unistra.fr/ftp/V/50/catalog.gz ; "
      "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de421.bsp")
print("# WGS84 49.2827,-123.1207,0m; UTC 2026-10-29; builtin timescale; "
      "J2000 catalogue positions; no proper motion/parallax; apparent, no refraction")
catalog = {int(row[:4]): row for row in gzip.decompress(
    (source / "catalog.gz").read_bytes()).decode("ascii").splitlines()}
observer = load_file(str(source / "de421.bsp"))["earth"] + wgs84.latlon(49.2827, -123.1207)
times = load.timescale(builtin=True)
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["hour", "name", "hr", "ra_hours", "dec_degrees", "alt", "az"])
for hour in range(3, 8):
    for hr, name in HR.items():
        row = catalog[hr]
        ra = int(row[75:77]) + int(row[77:79]) / 60 + float(row[79:83]) / 3600
        dec = (int(row[84:86]) + int(row[86:88]) / 60 + int(row[88:90]) / 3600)
        dec *= -1 if row[83] == "-" else 1
        alt, az, _ = observer.at(times.utc(2026, 10, 29, hour)).observe(
            Star(ra_hours=ra, dec_degrees=dec)).apparent().altaz()
        writer.writerow([hour, name, hr, f"{ra:.8f}", f"{dec:.8f}",
                         f"{alt.degrees:.8f}", f"{az.degrees:.8f}"])
