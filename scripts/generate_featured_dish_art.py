"""Render original, consistent bowl-and-chopsticks art for the ten hero dishes."""
from pathlib import Path
import subprocess


ASSET_DIR = Path(__file__).resolve().parents[1] / "static" / "assets"

RECIPES = {
    "featured-salmon-poke": ("Salmon Poke", "#f2b94d", ["salmon", "salmon", "salmon", "avocado", "avocado", "cucumber", "cucumber", "carrot", "nori", "tomato", "sesame"]),
    "featured-tuna-sashimi": ("Ahi Tuna Sashimi", "#e9bd54", ["tuna", "tuna", "tuna", "salmon", "mango", "mango", "cucumber", "nori", "tuna", "ikura", "sesame"]),
    "featured-crispy-tofu": ("Crispy Tofu Buddha", "#a9bd72", ["tofu", "tofu", "tofu", "avocado", "avocado", "cucumber", "carrot", "edamame", "nori", "greens", "sesame"]),
    "featured-unagi": ("Smoked Eel Unagi Don", "#ee9941", ["eel", "eel", "eel", "egg", "cucumber", "cucumber", "ginger", "nori", "eel", "greens", "sesame"]),
    "featured-chirashi": ("Chef Select Chirashi", "#efbd4e", ["salmon", "tuna", "salmon", "prawn", "egg", "ikura", "ikura", "nori", "salmon", "cucumber", "sesame"]),
    "featured-chicken-katsu": ("Chicken Katsu Curry", "#e9a444", ["katsu", "katsu", "katsu", "egg", "cabbage", "cabbage", "carrot", "curry", "katsu", "greens", "sesame"]),
    "featured-garden-quinoa": ("Avocado Quinoa", "#b5c875", ["avocado", "avocado", "avocado", "tomato", "cucumber", "cucumber", "edamame", "carrot", "greens", "tomato", "sesame"]),
    "featured-prawn-soba": ("Chili Soba Prawn", "#e9a24b", ["prawn", "prawn", "prawn", "soba", "soba", "cucumber", "carrot", "greens", "prawn", "tomato", "sesame"]),
    "featured-miso-mushroom": ("Miso Mushroom Tofu", "#c4ad71", ["tofu", "mushroom", "tofu", "mushroom", "mushroom", "greens", "cucumber", "nori", "tofu", "edamame", "sesame"]),
    "featured-jammy-egg": ("Garden Egg Rice", "#e9bd54", ["egg", "egg", "egg", "greens", "cucumber", "cucumber", "carrot", "nori", "egg", "edamame", "sesame"]),
}

POSITIONS = [(310, 495), (390, 455), (480, 440), (570, 445), (660, 480), (710, 535), (660, 585), (570, 610), (470, 615), (370, 600), (300, 555)]


def ingredient(kind: str, x: int, y: int, index: int) -> str:
    turn = (-17, 11, 20, -9, 15, -13, 8, 18)[index % 8]
    seed = (index * 17 + x + y) % 7
    if kind in {"salmon", "tuna", "eel", "katsu", "tofu", "mushroom", "mango"}:
        colors = {
            "salmon": ("#fb966c", "#d65c4e"), "tuna": ("#d86b76", "#a83f55"),
            "eel": ("#a84e2c", "#6f3427"), "katsu": ("#e9a34d", "#be642f"),
            "tofu": ("#f3d99b", "#c99456"), "mushroom": ("#98644c", "#624438"),
            "mango": ("#ffc968", "#ec8742"),
        }
        light, dark = colors[kind]
        stripes = "" if kind in {"tofu", "mango"} else f'<path d="M-29 -8 Q0 -23 29 -8 M-28 10 Q0 -5 28 10" fill="none" stroke="#fff0d4" stroke-width="5" opacity=".8"/>'
        return f'<g transform="translate({x} {y}) rotate({turn})"><rect x="-39" y="-29" width="78" height="58" rx="17" fill="{light}" stroke="{dark}" stroke-width="5"/><path d="M-28 -21 Q0 -35 25 -20" fill="none" stroke="#fff4db" stroke-width="7" stroke-linecap="round" opacity=".8"/>{stripes}<circle cx="{seed - 2}" cy="17" r="3.5" fill="#6d4935" opacity=".7"/></g>'
    if kind in {"avocado", "cucumber", "tomato", "edamame", "ikura"}:
        colors = {"avocado": "#8aaf54", "cucumber": "#70a75c", "tomato": "#e66f52", "edamame": "#91b95b", "ikura": "#ee8138"}
        color = colors[kind]
        inner = "<circle r='9' fill='#eff0b2'/>" if kind == "cucumber" else ""
        leaf = "<path d='M-3 -12 Q-16 -26 -20 -12 Q-13 -8 -3 -12' fill='#4d8247'/>" if kind == "tomato" else ""
        size = 26 if kind == "ikura" else 35
        return f'<g transform="translate({x} {y})"><circle r="{size}" fill="{color}" stroke="#fff2cf" stroke-width="5"/><circle cx="-10" cy="-11" r="8" fill="#fff6d9" opacity=".45"/>{inner}{leaf}</g>'
    if kind in {"egg", "prawn"}:
        if kind == "egg":
            return f'<g transform="translate({x} {y}) rotate({turn})"><ellipse rx="43" ry="32" fill="#fff9df" stroke="#d7c8a2" stroke-width="5"/><circle cx="2" cy="1" r="18" fill="#f4b63e"/><circle cx="-3" cy="-4" r="7" fill="#fff2b5" opacity=".8"/></g>'
        return f'<g transform="translate({x} {y}) rotate({turn})"><path d="M-38 12 C-31 -32 35 -36 39 0 C43 28 14 34 -8 21" fill="none" stroke="#c8583f" stroke-width="30" stroke-linecap="round"/><path d="M-35 9 C-28 -29 32 -32 35 0 C38 24 13 28 -7 17" fill="none" stroke="#ffad77" stroke-width="20" stroke-linecap="round"/><path d="M-12 -18 L-9 5 M7 -24 L10 -4 M25 -16 L26 2" stroke="#fff0d2" stroke-width="4"/></g>'
    if kind in {"carrot", "ginger", "nori", "greens", "cabbage", "soba", "curry", "sesame"}:
        if kind == "sesame":
            return f'<ellipse cx="{x}" cy="{y}" rx="5" ry="10" transform="rotate({turn} {x} {y})" fill="#f9edcf" stroke="#8b6b49" stroke-width="2"/>'
        if kind in {"carrot", "ginger", "nori", "cabbage"}:
            color = {"carrot": "#ed8846", "ginger": "#e8a76a", "nori": "#38563f", "cabbage": "#a66c83"}[kind]
            return f'<path d="M{x-34} {y+12} Q{x-12} {y-35} {x+36} {y-12} Q{x+12} {y+12} {x-34} {y+12}" fill="{color}" stroke="#564435" stroke-width="4" stroke-linejoin="round"/>'
        if kind == "greens":
            return f'<path d="M{x-34} {y+20} Q{x-47} {y-20} {x-8} {y-31} Q{x+4} {y-9} {x+36} {y-27} Q{x+43} {y+13} {x+7} {y+27} Q{x-11} {y+4} {x-34} {y+20}" fill="#73a760" stroke="#426c48" stroke-width="4"/>'
        if kind == "soba":
            return f'<path d="M{x-35} {y-8} Q{x-12} {y-30} {x+2} {y-5} T{x+34} {y-9} M{x-34} {y+7} Q{x-10} {y-14} {x+3} {y+10} T{x+33} {y+7}" fill="none" stroke="#8c5537" stroke-width="6" stroke-linecap="round"/>'
        return f'<path d="M{x-32} {y} Q{x} {y-32} {x+32} {y} Q{x} {y+34} {x-32} {y}" fill="#e7ab45" opacity=".75"/>'
    return ""


def make_svg(name: str, accent: str, toppings: list[str]) -> str:
    food = "".join(ingredient(kind, *POSITIONS[index], index) for index, kind in enumerate(toppings))
    rice = "".join(
        f'<ellipse cx="{300 + (index * 73) % 425}" cy="{535 + (index * 47) % 115}" rx="4" ry="2.4" transform="rotate({index * 29} {300 + (index * 73) % 425} {535 + (index * 47) % 115})" fill="#987d5d" opacity=".72"/>'
        for index in range(120)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<defs>
  <linearGradient id="ceramic" x1=".12" y1=".1" x2=".82" y2=".95"><stop stop-color="#fffefa"/><stop offset=".48" stop-color="#f4eee1"/><stop offset="1" stop-color="#d5c8b5"/></linearGradient>
  <linearGradient id="rice" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fff7df"/><stop offset="1" stop-color="#e9d7b4"/></linearGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#a8582e"/><stop offset=".28" stop-color="#f7b151"/><stop offset=".58" stop-color="#ffe0a1"/><stop offset="1" stop-color="#b86b35"/></linearGradient>
  <clipPath id="bowlInterior"><ellipse cx="512" cy="535" rx="294" ry="163"/></clipPath>
</defs>
<ellipse cx="510" cy="837" rx="310" ry="35" fill="#78634e" opacity=".12"/>
<path d="M179 492 C211 326 396 250 553 300 C700 236 846 354 820 512 C803 619 671 661 514 653 C344 660 197 619 179 492Z" fill="{accent}" opacity=".9"/>
<g stroke="#70452f" stroke-linejoin="round">
  <path d="M759 279 L799 263 L634 800 L603 817Z" fill="url(#wood)" stroke-width="7"/>
  <path d="M850 301 L889 286 L704 824 L673 837Z" fill="url(#wood)" stroke-width="7"/>
  <path d="M777 328 L790 323 M862 351 L874 347" stroke="#fff0c9" stroke-width="5" stroke-linecap="round"/>
</g>
<path d="M200 527 Q512 666 824 527 L765 780 Q512 952 259 780Z" fill="url(#ceramic)" stroke="#654d3e" stroke-width="13" stroke-linejoin="round"/>
<path d="M232 562 Q512 691 792 562 L744 758 Q512 902 280 758Z" fill="#eee6d7" opacity=".72"/>
<ellipse cx="512" cy="535" rx="323" ry="190" fill="url(#ceramic)" stroke="#654d3e" stroke-width="13"/>
<ellipse cx="512" cy="535" rx="294" ry="163" fill="url(#rice)" stroke="#b7a68c" stroke-width="6"/>
<g clip-path="url(#bowlInterior)"><path d="M218 544 Q510 653 806 541 L802 705 L218 705Z" fill="#f3e3c3"/>{rice}{food}</g>
<ellipse cx="512" cy="535" rx="294" ry="163" fill="none" stroke="#fffdf5" stroke-width="10" opacity=".9"/>
<path d="M210 565 Q512 820 814 565" fill="none" stroke="#fffdf7" stroke-width="15" opacity=".8"/>
<path d="M288 771 Q512 890 736 771" fill="none" stroke="#b9aa94" stroke-width="8" opacity=".7"/>
<g fill="#fffdf5" opacity=".8"><circle cx="343" cy="426" r="6"/><circle cx="698" cy="454" r="5"/><circle cx="742" cy="511" r="4"/></g>
</svg>'''


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for dish_id, recipe in RECIPES.items():
        name, accent, toppings = recipe
        output = ASSET_DIR / f"{dish_id}.png"
        result = subprocess.run(
            [
                "magick", "-background", "none", "svg:-", "-trim", "+repage",
                "-resize", "900x900", "-gravity", "center", "-background", "none",
                "-extent", "1024x1024", f"png32:{output}",
            ],
            input=make_svg(name, accent, toppings).encode("utf-8"),
            check=False,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
        print(f"Generated {output.name}")


if __name__ == "__main__":
    main()