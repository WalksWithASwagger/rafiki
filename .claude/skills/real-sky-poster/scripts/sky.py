"""Real star positions for a given place and moment.

Standard library only, on purpose: the astronomy is the part that must be
verifiable without an image, a GPU, or a network call.

Coordinates are J2000 from the Bright Star Catalogue. Reduction is the classic
one -- local sidereal time, hour angle, then alt/az -- which is accurate to well
under a degree for this era. That is far tighter than any poster needs.

The gate that proves the reduction: Polaris sits at an altitude equal to the
observer's latitude, anywhere on Earth. `python3 tests/skills/real-sky-poster/
test_sky.py` asserts exactly that.
"""

from __future__ import annotations

import math

# name: (RA hours, Dec degrees, V magnitude)
STARS: dict[str, tuple[float, float, float]] = {
    # Ursa Major, the Big Dipper
    "Dubhe": (11.0621, 61.7510, 1.79),
    "Merak": (11.0307, 56.3825, 2.37),
    "Phecda": (11.8972, 53.6948, 2.44),
    "Megrez": (12.2570, 57.0326, 3.31),
    "Alioth": (12.9005, 55.9598, 1.77),
    "Mizar": (13.3987, 54.9254, 2.23),
    "Alkaid": (13.7923, 49.3133, 1.86),
    # Ursa Minor
    "Polaris": (2.5303, 89.2641, 1.98),
    "Kochab": (14.8451, 74.1555, 2.08),
    "Pherkad": (15.3455, 71.8340, 3.05),
    "eps UMi": (16.7661, 82.0373, 4.23),
    "zet UMi": (15.7343, 77.7945, 4.32),
    "del UMi": (17.5369, 86.5865, 4.36),
    "eta UMi": (16.2917, 75.7551, 4.95),
    # Cassiopeia
    "Caph": (0.1528, 59.1498, 2.27),
    "Schedar": (0.6751, 56.5373, 2.24),
    "gam Cas": (0.9451, 60.7167, 2.15),
    "Ruchbah": (1.4303, 60.2353, 2.68),
    "Segin": (1.9066, 63.6701, 3.35),
    # Cygnus
    "Deneb": (20.6905, 45.2803, 1.25),
    "Sadr": (20.3704, 40.2567, 2.23),
    "Albireo": (19.5121, 27.9597, 3.05),
    "del Cyg": (19.7496, 45.1308, 2.87),
    "Gienah": (20.7701, 33.9703, 2.48),
    # Lyra
    "Vega": (18.6156, 38.7837, 0.03),
    "eps Lyr": (18.7390, 39.6703, 4.60),
    "zet Lyr": (18.7462, 37.6051, 4.36),
    "bet Lyr": (18.8346, 33.3627, 3.52),
    "gam Lyr": (18.9824, 32.6896, 3.24),
    # Perseus
    "Mirfak": (3.4054, 49.8612, 1.79),
    "Algol": (3.1361, 40.9556, 2.12),
    "zet Per": (3.9022, 31.8836, 2.85),
    "del Per": (3.7154, 47.7877, 3.01),
    "eps Per": (3.9642, 40.0102, 2.89),
    "gam Per": (3.0800, 53.5065, 2.91),
    # Pleiades (M45)
    "Alcyone": (3.7914, 24.1051, 2.87),
    "Atlas": (3.8194, 24.0534, 3.62),
    "Electra": (3.7479, 24.1133, 3.70),
    "Maia": (3.7638, 24.3675, 3.87),
    "Merope": (3.7721, 23.9480, 4.18),
    "Taygeta": (3.7535, 24.4672, 4.30),
    # Auriga / Taurus
    "Capella": (5.2782, 45.9980, 0.08),
    "Aldebaran": (4.5987, 16.5093, 0.85),
    # Andromeda + Pegasus
    "Alpheratz": (0.1398, 29.0904, 2.06),
    "del And": (0.6555, 30.8610, 3.27),
    "Mirach": (1.1621, 35.6206, 2.06),
    "Almach": (2.0650, 42.3297, 2.10),
    "Scheat": (23.0629, 28.0828, 2.42),
    "Markab": (23.0793, 15.2053, 2.48),
    "Algenib": (0.2206, 15.1836, 2.83),
    # Orion
    "Betelgeuse": (5.9195, 7.4071, 0.50),
    "Rigel": (5.2423, -8.2016, 0.13),
    "Bellatrix": (5.4188, 6.3497, 1.64),
    "Saiph": (5.7959, -9.6696, 2.06),
    "Alnitak": (5.6793, -1.9426, 1.77),
    "Alnilam": (5.6036, -1.2019, 1.69),
    "Mintaka": (5.5334, -0.2991, 2.23),
    # Cepheus
    "Alderamin": (21.3096, 62.5856, 2.45),
    "Alfirk": (21.4776, 70.5607, 3.23),
    "gam Cep": (23.6559, 77.6323, 3.21),
    "iot Cep": (22.8281, 66.2003, 3.52),
    "zet Cep": (22.1810, 58.2012, 3.35),
    # Draco
    "Eltanin": (17.9435, 51.4889, 2.23),
    "Rastaban": (17.5072, 52.3014, 2.79),
    "xi Dra": (17.8925, 56.8727, 3.75),
    "nu Dra": (17.6873, 55.1731, 4.88),
    "del Dra": (19.2093, 67.6615, 3.07),
    "eps Dra": (19.8021, 70.2679, 3.83),
    "zet Dra": (17.1465, 65.7147, 3.17),
    "eta Dra": (16.3999, 61.5141, 2.73),
    "iot Dra": (15.4155, 58.9661, 3.29),
    "Thuban": (14.0730, 64.3758, 3.65),
    "kap Dra": (12.5591, 69.7881, 3.87),
    "lam Dra": (11.5313, 69.3312, 3.82),
}

GROUPS: dict[str, list[str]] = {
    "Ursa Major": ["Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar", "Alkaid"],
    "Ursa Minor": ["Polaris", "Kochab", "Pherkad", "eps UMi", "zet UMi", "del UMi", "eta UMi"],
    "Cassiopeia": ["Caph", "Schedar", "gam Cas", "Ruchbah", "Segin"],
    "Cygnus": ["Deneb", "Sadr", "Albireo", "del Cyg", "Gienah"],
    "Lyra": ["Vega", "eps Lyr", "zet Lyr", "bet Lyr", "gam Lyr"],
    "Perseus": ["Mirfak", "Algol", "zet Per", "del Per", "eps Per", "gam Per"],
    "Pleiades": ["Alcyone", "Atlas", "Electra", "Maia", "Merope", "Taygeta"],
    "Andromeda": ["Alpheratz", "del And", "Mirach", "Almach"],
    "Pegasus": ["Markab", "Scheat", "Alpheratz", "Algenib"],
    "Cepheus": ["Alderamin", "Alfirk", "gam Cep", "iot Cep", "zet Cep"],
    "Draco": [
        "Eltanin", "Rastaban", "xi Dra", "nu Dra", "del Dra", "eps Dra",
        "zet Dra", "eta Dra", "iot Dra", "Thuban", "kap Dra", "lam Dra",
    ],
    "Orion": [
        "Betelgeuse", "Rigel", "Bellatrix", "Saiph", "Alnitak", "Alnilam", "Mintaka",
    ],
    "Auriga": ["Capella"],
    "Taurus": ["Aldebaran"],
}

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


class Sky:
    """The sky as seen from one place at one moment.

    utc: (year, month, day, hour, minute, second) -- UTC, not local. Convert
    first; a wrong timezone is the single easiest way to draw the wrong sky.
    """

    def __init__(self, utc: tuple[int, int, int, int, int, float],
                 lat: float, lon: float) -> None:
        self.utc, self.lat, self.lon = utc, lat, lon
        self.lst = self._local_sidereal()

    def _julian_day(self) -> float:
        y, m, d, hh, mm, ss = self.utc
        if m <= 2:
            y, m = y - 1, m + 12
        a = y // 100
        b = 2 - a + a // 4
        day = d + (hh + mm / 60 + ss / 3600) / 24
        return (math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1))
                + day + b - 1524.5)

    def _local_sidereal(self) -> float:
        jd = self._julian_day()
        t = (jd - 2451545.0) / 36525.0
        gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
                + 0.000387933 * t * t - t * t * t / 38710000.0)
        return (gmst + self.lon) % 360.0

    def alt_az(self, name: str) -> tuple[float, float]:
        """Altitude and azimuth in degrees. Azimuth is clockwise from north."""
        ra_hours, dec_deg, _ = STARS[name]
        ha = math.radians((self.lst - ra_hours * 15.0) % 360.0)
        dec, lat = math.radians(dec_deg), math.radians(self.lat)

        alt = math.asin(math.sin(dec) * math.sin(lat)
                        + math.cos(dec) * math.cos(lat) * math.cos(ha))
        az = math.atan2(-math.sin(ha) * math.cos(dec),
                        math.cos(lat) * math.sin(dec)
                        - math.sin(lat) * math.cos(dec) * math.cos(ha))
        return math.degrees(alt), math.degrees(az) % 360.0

    def bearing(self, group: str) -> tuple[float, float]:
        """Mean altitude and azimuth of a group, via unit vectors so it behaves
        near the pole and across the 0/360 azimuth seam."""
        vx = vy = vz = 0.0
        for name in GROUPS[group]:
            alt, az = self.alt_az(name)
            a, z = math.radians(alt), math.radians(az)
            vx += math.cos(a) * math.cos(z)
            vy += math.cos(a) * math.sin(z)
            vz += math.sin(a)
        n = math.sqrt(vx * vx + vy * vy + vz * vz)
        return math.degrees(math.asin(vz / n)), math.degrees(math.atan2(vy, vx)) % 360.0

    def is_up(self, group: str, horizon: float = 5.0) -> bool:
        """Below the horizon means below the horizon. Do not draw it."""
        return self.bearing(group)[0] > horizon

    def project(self, names: list[str], px_per_degree: float) -> dict[str, tuple[float, float]]:
        """Gnomonic projection onto the tangent plane at the group's own centre,
        zenith up. Preserves the figure's true shape AND its true rotation
        against the horizon -- which is what makes a drawn constellation read as
        the real thing rather than a clipart version of it.

        Returns local pixel offsets about the group centroid; y grows downward.
        """
        horiz = {n: self.alt_az(n) for n in names}

        vx = vy = vz = 0.0
        for alt, az in horiz.values():
            a, z = math.radians(alt), math.radians(az)
            vx += math.cos(a) * math.cos(z)
            vy += math.cos(a) * math.sin(z)
            vz += math.sin(a)
        n = math.sqrt(vx * vx + vy * vy + vz * vz)
        alt0 = math.asin(vz / n)
        az0 = math.atan2(vy, vx)

        out: dict[str, tuple[float, float]] = {}
        for name, (alt, az) in horiz.items():
            a, z = math.radians(alt), math.radians(az)
            d = z - az0
            cosc = (math.sin(alt0) * math.sin(a)
                    + math.cos(alt0) * math.cos(a) * math.cos(d))
            xi = math.cos(a) * math.sin(d) / cosc                      # east -> right
            eta = ((math.cos(alt0) * math.sin(a)
                    - math.sin(alt0) * math.cos(a) * math.cos(d)) / cosc)  # zenith -> up
            out[name] = (math.degrees(xi) * px_per_degree,
                         -math.degrees(eta) * px_per_degree)
        return out

    def compass(self, az: float) -> str:
        return COMPASS[int((az + 11.25) % 360 / 22.5)]

    def report(self) -> str:
        """What is actually up, and where. Read this before placing anything."""
        rows = []
        for group in GROUPS:
            alt, az = self.bearing(group)
            flag = "" if alt > 5 else "   <-- BELOW HORIZON, do not draw"
            rows.append(f"  {group:<12} alt {alt:5.1f}  az {az:5.1f} "
                        f"{self.compass(az):<3}{flag}")
        return "\n".join(rows)


def angular_separation(a: str, b: str) -> float:
    """True angular distance between two stars, in degrees. Independent of
    observer -- used to prove a projection preserved the real geometry."""
    ra1, dec1, _ = STARS[a]
    ra2, dec2, _ = STARS[b]
    r1, d1 = math.radians(ra1 * 15), math.radians(dec1)
    r2, d2 = math.radians(ra2 * 15), math.radians(dec2)
    return math.degrees(math.acos(
        min(1.0, math.sin(d1) * math.sin(d2)
            + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2))))
