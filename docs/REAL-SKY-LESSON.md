# Looks Right. Is It Right?

One offline lesson, built from a checkout. It is not included in the npm package.
Python 3.11+, the existing Node dependencies and Chrome are needed to build the PNG.
No provider, server, network, GPU, campaign artwork or web fonts are used in playback.

```sh
python3 .agents/skills/real-sky-poster/scripts/lesson.py --output /tmp/my-sky-lesson
```

The destination must not exist; its parent must exist. The command creates
`lesson.html`, `still.html` and `still.png` (1200×630). A rendering failure leaves
the HTML for inspection and exits nonzero. Use a new destination when retrying.
Move the HTML anywhere. Arrow keys advance moments; buttons and the labelled
time slider work independently. No answers are stored. Without JavaScript all
five moments and the default 04:00 UTC diagram remain readable.

Edit plain-text copy with `--profile PATH`, using the keys and five heading/body
objects in `.agents/skills/real-sky-poster/profiles/looks-right.json`. Both outputs
carry its SHA-256. Dates, observer and twelve stars are deliberately fixed.

The shared projection is azimuthal equidistant: zenith centre, north top, east
right, radius proportional to zenith distance. This is a diagram, not an optical
view. Individual geometric altitudes below zero are excluded; sizes are symbolic.
No refraction or proper motion is modelled. All 60 positions match independent
reference directions within 1° and agree on horizon classification. Source URLs,
catalogue IDs, input coordinates, data hashes and library versions are in
`tests/skills/real-sky-poster/fixtures/reference-sky.csv`.

Regenerate only in an isolated environment with Skyfield 1.54, NumPy 2.5.2,
jplephem 2.24 and sgp4 2.27. Download `catalog.gz` and `de421.bsp` from the CSV's
URLs into a temporary directory, then run `reference_sky.py DIRECTORY > candidate.csv`
from `tests/skills/real-sky-poster`. Review the candidate; CI never downloads data.

Before release: check Chrome/Safari offline, keyboard/focus, VoiceOver, 200% zoom,
390×844 and 1440×900 layouts. With five first-time viewers, require four to finish
within four minutes and distinguish constructed, calculated and composed elements.
Record aggregate results only. This human evaluation remains a release checkpoint;
automated tests cannot establish comprehension. Publishing is a separate action.
