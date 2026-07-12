# real-sky-poster :: smoke test

```bash
python3 tests/skills/real-sky-poster/test_sky.py
```

Runs offline. No image, no GPU, no network, no API spend, no dependencies —
standard library only, in well under a second.

## What it actually proves

The skill makes exactly one claim that matters: *these are the real stars, in
the real places, for the stated date and location.* If that is false, everything
downstream is just a prettier lie. So the test attacks the claim rather than
exercising the plumbing:

| Gate | Why it is the right gate |
|---|---|
| **Polaris altitude == observer latitude** | True anywhere on Earth, any night. If the sidereal-time or alt/az reduction has a bug, this is the first thing to break. Checked at four latitudes including the equator. |
| **Polaris invisible from Sydney** | Below the horizon means below the horizon. A pipeline that will cheerfully draw an invisible constellation is the exact bug this skill exists to fix. |
| **Projection preserves true proportions** | Drawn distances are compared against catalogue angular separations. Tolerance is *relative*, because the projection is gnomonic and inflates distances a few percent away from the tangent point — a deliberate property (it keeps lines straight and rotation true), not an error. A pixel-exact match would mean the projection was doing nothing. |
| **Futureproof opening night** | The regression fixture. Vancouver, 28 Oct 2026, 21:00 PDT — the sky that shipped. Asserts each figure's compass bearing and altitude, *and* that Orion had not risen and Pegasus was behind the viewer. Both were deliberately left off the poster; this proves they had to be. |

The imaging stages (`plate`, `upscale`, `render`, `kit`) need artwork, which the
public repo does not carry by design. Verify those visually, against the
`disturbance()` fidelity gate and the dimension gate in `kit.build()`.
