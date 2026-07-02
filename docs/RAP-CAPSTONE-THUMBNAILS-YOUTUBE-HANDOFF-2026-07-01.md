# RAP Cohort 1 Capstone Thumbnail And YouTube Handoff

Date: 2026-07-01

## Summary

The accepted thumbnail system is V3, a generative, reference-driven pass with
large integrated title treatment, stronger visible RAP/BC+AI presence, and
forest/mycelial art direction. V1 and V2 remain local historical packages, but
V3 supersedes them for delivery.

Local package:

`/Users/kk/Code/rafiki/output/rap-cohort-1-capstone-thumbnails-generative-v3-2026-07-01/`

Final JPGs:

`/Users/kk/Code/rafiki/output/rap-cohort-1-capstone-thumbnails-generative-v3-2026-07-01/final/`

YouTube export bundle:

`/Users/kk/Code/rafiki/output/rap-cohort-1-capstone-thumbnails-generative-v3-2026-07-01/youtube-export/rap-cohort-1-capstone-youtube-thumbnails-v3.zip`

Upload helper:

`/Users/kk/Code/rafiki/output/rap-cohort-1-capstone-thumbnails-generative-v3-2026-07-01/youtube-export/upload_youtube_thumbnails.py`

## Thumbnail Package

- 19 final JPG thumbnails were exported at 1280x720.
- Each final JPG passed the local size check and is under 2 MB.
- File names match the requested participant slugs.
- The V3 pass used generated near-final compositions instead of flat corporate
  overlays. Local correction was reserved as a fallback only.
- The generated output package is intentionally under `output/`, so it is not
  tracked in git.

## YouTube Update Status

Authenticated channel verified:

- Channel ID: `UCn523YAljjrfQHgRq_qUWXg`
- Channel title: `BC + AI Ecosystem Industry Assocation`

Seven custom thumbnails were uploaded successfully:

| Slug | Video ID | YouTube URL |
| --- | --- | --- |
| `bruce-ratzlaff` | `usS4HmxpAYk` | `https://www.youtube.com/watch?v=usS4HmxpAYk` |
| `kerris-hougardy` | `QHlTwufNQl0` | `https://www.youtube.com/watch?v=QHlTwufNQl0` |
| `brittney-ashley` | `BZdwiou5K6E` | `https://www.youtube.com/watch?v=BZdwiou5K6E` |
| `tanya-slingsby` | `ex5Lu1c_b54` | `https://www.youtube.com/watch?v=ex5Lu1c_b54` |
| `melisa-dipietro` | `RolycTPvuso` | `https://www.youtube.com/watch?v=RolycTPvuso` |
| `monique-sherrett` | `UEG_LGtTM-4` | `https://www.youtube.com/watch?v=UEG_LGtTM-4` |
| `jacquie-harder` | `viWQdhniCgY` | `https://www.youtube.com/watch?v=viWQdhniCgY` |

Three mapped uploads were blocked by YouTube's thumbnail upload rate limit:

| Slug | Video ID | Next action |
| --- | --- | --- |
| `stephanie-mckay` | `SqLQm38eDO0` | Retry after the YouTube upload cooldown. |
| `katie-bedford` | `lRz3brRCzlk` | Retry after the YouTube upload cooldown. |
| `allan-baedak` | `c-rtLtFng5A` | Retry after the YouTube upload cooldown. |

Retry command:

```bash
python3 output/rap-cohort-1-capstone-thumbnails-generative-v3-2026-07-01/youtube-export/upload_youtube_thumbnails.py --execute --only stephanie-mckay,katie-bedford,allan-baedak
```

Nine participant thumbnails are ready locally but were not uploaded because the
matching videos were not present on the authenticated channel:

- `manny-minhas`
- `noah-brunn`
- `rachel-krayenhoff`
- `tavis-yeung`
- `rakesh-sharma`
- `david-gloyn-cox`
- `fiann`
- `bobby-motamed`
- `daniel-bashaw`

## Verification Notes

- Dry run verified the 10 mapped videos, titles, files, and channel before any
  upload.
- Live upload updated 7 of 10 mapped videos.
- Targeted retry for the remaining 3 mapped videos was also preflighted and
  then blocked by `uploadRateLimitExceeded`.
- No new videos were uploaded.
- The generic Zoom recording `IeSIcKcsdjY` was not updated.
- No guesses were made for the 9 missing participant videos.
- OAuth credentials stayed in the existing local pipeline work area and were
  not committed or copied into the repo.

## Next

1. Retry the 3 rate-limited YouTube uploads after the cooldown clears.
2. Locate, upload, or publish the 9 missing participant videos, then map their
   thumbnails explicitly before upload.
3. Review the live YouTube grid once all 19 thumbnails are attached, watching
   for scan-readability, logo visibility, and any generated-text artifacts that
   warrant a targeted thumbnail regeneration.
