#!/usr/bin/env python3
"""Generate app icons: magnifying glass + steroid tube + shield."""

import math
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
NAVY = (30, 58, 95, 255)
TEAL = (42, 181, 165, 255)
WHITE = (255, 255, 255, 255)
LIGHT_BLUE = (240, 246, 255, 255)


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    w, h = x1 - x0, y1 - y0
    radius = min(radius, w // 2, h // 2)
    if w > 2 * radius:
        draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    if h > 2 * radius:
        draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)


def rotate_point(px, py, cx, cy, angle_deg):
    angle = math.radians(angle_deg)
    dx, dy = px - cx, py - cy
    nx = dx * math.cos(angle) - dy * math.sin(angle)
    ny = dx * math.sin(angle) + dy * math.cos(angle)
    return cx + nx, cy + ny


def make_icon(size=1024):
    img = Image.new("RGBA", (SIZE, SIZE), WHITE)
    draw = ImageDraw.Draw(img)

    # ── ① 虫眼鏡 ──────────────────────────────────────────
    # 中心を左上寄りに
    cx, cy = 390, 390
    r_outer = 270
    r_inner = 195
    ring_color = NAVY

    # 影レイヤー
    shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.ellipse([cx - r_outer + 15, cy - r_outer + 15,
                cx + r_outer + 15, cy + r_outer + 15], fill=(0, 0, 0, 40))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(18))
    img.paste(shadow_layer, mask=shadow_layer)

    # レンズ（薄水色で塗りつぶし）
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                 fill=(220, 240, 255, 255))
    # リング（ネイビー）
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                 fill=ring_color)
    # 内側白抜き
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
                 fill=(220, 240, 255, 255))

    # レンズ内のハイライト
    draw.ellipse([cx - r_inner + 20, cy - r_inner + 20,
                  cx - 10, cy - 10],
                 fill=(255, 255, 255, 120))

    # ハンドル
    angle = 45
    hx0, hy0 = cx + r_outer - 30, cy + r_outer - 30
    hw, hh = 85, 310
    handle_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(handle_layer)
    draw_rounded_rect(hd,
                      [hx0, hy0, hx0 + hw, hy0 + hh],
                      radius=42, fill=ring_color)
    handle_layer = handle_layer.rotate(-angle, center=(cx, cy), resample=Image.BICUBIC)
    img.alpha_composite(handle_layer)

    # ── ② チューブ ────────────────────────────────────────
    tube_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    td = ImageDraw.Draw(tube_layer)

    # チューブ基準座標（水平描画してから回転）
    tx0, ty0 = 80, 540
    tube_w, tube_h = 680, 140
    cap_w = 80
    teal_w = 110
    label_w = 220

    # 本体（薄い青白）
    draw_rounded_rect(td, [tx0, ty0, tx0 + tube_w, ty0 + tube_h],
                      radius=tube_h // 2, fill=LIGHT_BLUE)

    # ティール帯
    td.rectangle([tx0 + tube_w - cap_w - teal_w, ty0,
                  tx0 + tube_w - cap_w, ty0 + tube_h], fill=TEAL)

    # ラベル白帯
    label_x = tx0 + tube_w // 2 - label_w // 2
    td.rectangle([label_x, ty0 + 20, label_x + label_w, ty0 + tube_h - 20],
                 fill=WHITE)

    # ラベルテキスト（フォントなしでドット代替: シンプルな横線）
    for i in range(3):
        y_line = ty0 + 45 + i * 22
        td.rectangle([label_x + 10, y_line, label_x + label_w - 10, y_line + 8],
                     fill=NAVY)

    # キャップ（リブ表現）
    cap_x = tx0 + tube_w - cap_w
    for i in range(5):
        rx = cap_x + i * (cap_w // 5)
        td.rectangle([rx, ty0, rx + cap_w // 5 - 3, ty0 + tube_h],
                     fill=(200, 215, 230, 255))
    draw_rounded_rect(td, [cap_x, ty0, tx0 + tube_w, ty0 + tube_h],
                      radius=tube_h // 2, fill=(180, 200, 220, 255))

    # 本体ハイライト
    td.rectangle([tx0 + 30, ty0 + 12, tx0 + tube_w - cap_w - 20, ty0 + 30],
                 fill=(255, 255, 255, 160))

    # 回転してメイン画像に合成
    tube_layer = tube_layer.rotate(-38, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(tube_layer)

    # ── ③ クリーム ────────────────────────────────────────
    # チューブ左端付近（回転後の位置を調整して手動配置）
    cream_cx, cream_cy = 230, 760
    cream_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cream_layer)

    # 影
    cd.ellipse([cream_cx - 55, cream_cy - 25,
                cream_cx + 55, cream_cy + 35], fill=(200, 200, 200, 80))
    cream_layer = cream_layer.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(cream_layer)

    # 盛り（複数楕円の重ね合わせ）
    cream_draw = ImageDraw.Draw(img)
    for ox, oy, rx, ry in [
        (0, 0, 60, 30),
        (-35, -18, 38, 22),
        (30, -15, 42, 25),
        (-15, -32, 30, 18),
        (20, -28, 25, 16),
    ]:
        cream_draw.ellipse([
            cream_cx + ox - rx, cream_cy + oy - ry,
            cream_cx + ox + rx, cream_cy + oy + ry
        ], fill=WHITE)

    # ── ④ シールド（右下）─────────────────────────────────
    sx, sy = 710, 680
    sw, sh = 240, 270

    def shield_poly(cx, cy, w, h):
        hw, hh = w // 2, h // 2
        return [
            (cx - hw, cy - hh),
            (cx + hw, cy - hh),
            (cx + hw, cy),
            (cx, cy + hh),
            (cx - hw, cy),
        ]

    # 影
    shield_shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ssd = ImageDraw.Draw(shield_shadow)
    ssd.polygon(shield_poly(sx + 10, sy + 10, sw, sh), fill=(0, 0, 0, 50))
    shield_shadow = shield_shadow.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(shield_shadow)

    # ネイビー外枠
    draw.polygon(shield_poly(sx, sy, sw, sh), fill=NAVY)
    # ティール内側
    inset = 18
    draw.polygon(shield_poly(sx, sy, sw - inset * 2, sh - inset * 2), fill=TEAL)

    # 白チェックマーク
    ck_pts = [
        (sx - 65, sy - 10),
        (sx - 20, sy + 45),
        (sx + 70, sy - 60),
    ]
    draw.line([ck_pts[0], ck_pts[1], ck_pts[2]], fill=WHITE, width=28)

    # ── 最終リサイズ ───────────────────────────────────────
    return img


def main():
    print("Generating icon at 1024×1024...")
    icon = make_icon()

    for size in [180, 152, 120]:
        out = icon.resize((size, size), Image.LANCZOS)
        path = f"/home/user/steroid-checker/icon-{size}.png"
        out.save(path)
        print(f"  Saved {path}")

    print("Done.")


if __name__ == "__main__":
    main()
