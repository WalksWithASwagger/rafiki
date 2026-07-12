#!/usr/bin/env python3
"""Offline smoke test for the real-sky-poster skill.

No image, no GPU, no network, no API spend. Standard library only.

The whole skill rests on one claim: these are the real stars, in the real
places, for the stated date and location. If that claim is false, everything
downstream is just a prettier lie. So this test attacks the claim directly.

    python3 tests/skills/real-sky-poster/test_sky.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]
                       / ".claude/skills/real-sky-poster/scripts"))

from sky import Sky, angular_separation  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str) -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        FAILURES.append(name)


def test_polaris_altitude_equals_latitude() -> None:
    """The load-bearing gate. Polaris sits within ~0.7 deg of the celestial
    pole, so its altitude equals the observer's latitude -- anywhere, any night.
    If the sidereal-time or alt/az reduction is wrong, this breaks first."""
    print("\nPolaris altitude == observer latitude")
    for place, lat, lon in [("Vancouver", 49.2827, -123.1207),
                            ("Reykjavik", 64.1466, -21.9426),
                            ("Quito", -0.1807, -78.4678),
                            ("Singapore", 1.3521, 103.8198)]:
        sky = Sky((2026, 10, 29, 4, 0, 0), lat, lon)
        alt, _ = sky.alt_az("Polaris")
        check(place, abs(alt - lat) < 0.75, f"alt {alt:+.2f} vs lat {lat:+.2f}")


def test_southern_hemisphere_cannot_see_polaris() -> None:
    """Below the horizon means below the horizon. A skill that will happily
    draw an invisible constellation is the bug we set out to fix."""
    print("\nPolaris is not visible from the southern hemisphere")
    sky = Sky((2026, 10, 29, 4, 0, 0), -33.8688, 151.2093)   # Sydney
    alt, _ = sky.alt_az("Polaris")
    check("Sydney", alt < 0, f"alt {alt:+.2f} (must be below 0)")


def test_projection_preserves_true_geometry() -> None:
    """A projected figure must keep its real angular proportions.

    The projection is gnomonic (tangent-plane), which is the right choice: it
    keeps straight lines straight and preserves the figure's rotation against
    the horizon. The trade is that it inflates distances away from the tangent
    point -- a few percent across a figure as wide as the Dipper. That is a
    property of the projection, not an error in the catalogue, so the tolerance
    here is relative, not absolute. A pixel-exact match would actually mean the
    projection was doing nothing.
    """
    print("\nProjection preserves the Big Dipper's true proportions")
    sky = Sky((2026, 10, 29, 4, 0, 0), 49.2827, -123.1207)
    ppd = 10.0
    pos = sky.project(["Dubhe", "Merak", "Mizar", "Alkaid"], ppd)

    for a, b in [("Dubhe", "Merak"), ("Mizar", "Alkaid")]:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        drawn = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 / ppd
        true = angular_separation(a, b)
        err = abs(drawn - true) / true
        check(f"{a}-{b}", err < 0.05,
              f"drawn {drawn:.2f} deg vs catalogue {true:.2f} deg ({err:.1%} gnomonic stretch)")


def test_futureproof_opening_night() -> None:
    """The worked example: Vancouver, Wed 28 Oct 2026, 21:00 PDT (= 04:00 UTC
    the 29th). This is the sky that shipped on the festival poster. It is also
    what gives the piece its story -- summer setting west, winter rising east."""
    print("\nFutureproof opening night: Vancouver, 28 Oct 2026, 21:00 PDT")
    sky = Sky((2026, 10, 29, 4, 0, 0), 49.2827, -123.1207)

    for group, want, lo, hi in [("Cygnus", "WSW", 55, 75),
                                ("Lyra", "W", 40, 60),
                                ("Ursa Major", "NNW", 10, 30),
                                ("Cassiopeia", "NE", 55, 75),
                                ("Perseus", "ENE", 28, 48),
                                ("Pleiades", "E", 13, 33)]:
        alt, az = sky.bearing(group)
        got = sky.compass(az)
        check(group, got == want and lo < alt < hi,
              f"{got} alt {alt:.0f} (want {want}, alt {lo}-{hi})")

    # Orion has not risen at 21:00 and Pegasus is behind a north-facing view.
    # Both were deliberately left off the wide crop. Prove they had to be.
    check("Orion below horizon", not sky.is_up("Orion"),
          f"alt {sky.bearing('Orion')[0]:.0f} (has not risen)")
    peg_az = sky.bearing("Pegasus")[1]
    check("Pegasus behind viewer", 100 < peg_az < 200,
          f"az {peg_az:.0f} {sky.compass(peg_az)} (not in a north-facing frame)")


if __name__ == "__main__":
    print("real-sky-poster :: offline astronomy gates")
    test_polaris_altitude_equals_latitude()
    test_southern_hemisphere_cannot_see_polaris()
    test_projection_preserves_true_geometry()
    test_futureproof_opening_night()

    print()
    if FAILURES:
        print(f"FAILED: {', '.join(FAILURES)}")
        sys.exit(1)
    print("All astronomy gates passed. The sky is real.")
