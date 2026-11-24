# news-image-20261124b

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/faj17/news-image-20261124b/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/faj17/news-image-20261124b/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up Tuesday, 24 November 2026: a classic newspaper front page under the masthead **THE WORLD TODAY**, leading with Ukraine sinking the Russian corvette Merkury off Libya and carrying the rest of the day's world news in columns below it. `main.py` is a small, dependency-free Python script that validates the image and copies it byte-for-byte into the output directory. `render.py` (Pillow) draws the front page from the sourced stories in `RESEARCH.md`.

## Stories on the front page

- **Ukraine sinks Russian warship off Libya** — seven sea drones sink the corvette Merkury at Benghazi and hit the cargo ship Angara.
- **NATO meets in emergency over Poland** — Russian missiles landed in Poland; AWACS early-warning aircraft to deploy.
- **Russia hits Ukraine's energy grid 100 times in a week** — 350,000 without power in Dnipropetrovsk; Dymer strike toll rises to 11.
- **COP31 collapses with no climate pact** — Guterres calls the outcome "deeply disappointing"; side deals still adopted.
- **Indonesia factory fire kills 24** — about 30 still missing at the candy plant in Banten.
- **Nvidia reinstates Huang as CEO** — board votes unanimously; Trump claims credit; Nvidia shares surge 35%.
- **Bitcoin rebounds from two-year low** — near $61,500 after a $55,130 Saturday low; S&P 500 in correction after its worst week since March 2020.
- **Liverpool thrash Man Utd 4–0** — Pochettino loses his debut; Skubal agrees a record $450m Mets deal.

All 37 items on the page trace to sourced stories in `RESEARCH.md` (45 verified stories; 8 verified but not on the page).

## How to run it

```sh
python3 main.py --output out --verbose
```

Pass `--quiet` to suppress all output except errors:

```sh
python3 main.py --output out --quiet
```

The script checks that `entry.png` is a 1024×1024 PNG no larger than 1 MiB with a valid IHDR checksum and trailing IEND chunk, copies it to the output directory, and verifies the copy's SHA-256 digest matches the original before printing the output path, byte size, dimensions and digest. Python 3.13, standard library only — no network access.

To re-render the front page from the story data:

```sh
python3 render.py
```

## Verification

Ran `python3 main.py --output out --verbose` twice into `out/` and `out2/`; both runs printed the same SHA-256 (`8e3d31eda4125b7a7a793f930a918f83a06d00c30cccc986d30a3677ccd2ef6f`), identical to `entry.png` itself — the output is byte-identical across runs. The image is 1024×1024 PNG, 201833 bytes.

## License

MIT — see [LICENSE](LICENSE).

<sub>Entered on [make.fun](https://make.fun/?ref=tzsn25v9&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
