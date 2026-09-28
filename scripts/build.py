"""Build the standalone pages.

- index.html (the main page): src/page.html with data/data.json, data/peers.json and data/review.json inlined.
- what-if/index.html: src/what-if.html with data/whatif.json inlined.

src/styles.css and src/charts.js are shared by the main page and the "Какво ако?" page.
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def wrap(body):
    head_end = body.index("</style>") + len("</style>")
    return ('<!doctype html>\n<html lang="bg">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + body[:head_end] + "\n</head>\n<body>\n" + body[head_end:] + "\n</body>\n</html>\n")


def read(path):
    return (root / path).read_text().strip()


def fill(src, **values):
    page = read(src).replace("__STYLES__", read("src/styles.css")).replace("__CHARTS__", read("src/charts.js"))
    for key, path in values.items():
        page = page.replace(f"__{key}__", read(path))
    return wrap(page)


def write(path, html):
    (root / path).parent.mkdir(exist_ok=True)
    (root / path).write_text(html)


write("index.html", fill("src/page.html", DATA="data/data.json", PEERS="data/peers.json", REVIEW="data/review.json"))
write("what-if/index.html", fill("src/what-if.html", WHATIF="data/whatif.json"))
print("wrote index.html and what-if/index.html")
