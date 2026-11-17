"""Cut-outs: shaped transparent areas. Always transparent (the avatar shows through), never painted skin.

Spec: torso.cut: {neckline: crew|v|scoop|square|sweetheart, depth: 4-22, width: 10-30,
                  style: sleeved|tank|halter|strapless|off_shoulder, strap_width: 5-14}
Moderation limits (also checked by validate.py): necklines at most 22 rows deep, strapless / off-shoulder
tops start no lower than row 14, straps at least 5 px wide; the chest (rows 24 to the hem) is always covered.
"""
NECKLINES = ("crew", "v", "scoop", "square", "sweetheart")
STYLES = ("sleeved", "tank", "halter", "strapless", "off_shoulder")
MAX_DEPTH = 22
MAX_TOP = 14


def neckline_pts(kind, depth, w, cu=64.0):
    if kind == "v":
        return [(cu - w, -1), (cu, depth), (cu + w, -1)]
    if kind == "square":
        return [(cu - w, -1), (cu - w, depth), (cu + w, depth), (cu + w, -1)]
    if kind == "sweetheart":
        pts = [(cu - w, -1)]
        for i in range(1, 9):
            t = i / 8
            pts.append((cu - w + w * t, depth * 0.55 + depth * 0.45 * t - 3 * (1 - abs(2 * t - 1))))
        for i in range(1, 9):
            t = i / 8
            pts.append((cu + w * t, depth - depth * 0.45 * t - 3 * (1 - abs(2 * t - 1))))
        return pts + [(cu + w, -1)]
    # crew / scoop: a curve
    import math
    n = 14
    return [(cu - w * math.cos(math.pi * i / n), -1 + (depth + 1) * math.sin(math.pi * i / n)) for i in range(n + 1)]


def torso_cut(fx, cut, trim_col, c, rgba, shade):
    """Clear alpha on the torso strip (fx["alpha"]) and draw a finished edge (binding) where cloth stops."""
    if not cut:
        return
    a = fx["alpha"]
    kind = cut.get("neckline", "crew")
    depth = min(MAX_DEPTH, float(cut.get("depth", 6)))
    w = float(cut.get("width", 16))
    style = cut.get("style", "sleeved")
    M = 48
    if kind != "crew" or depth > 4:
        pts = neckline_pts(kind, depth, w)
        a.polygon(pts + [(pts[-1][0], -M), (pts[0][0], -M)], 0)        # front neckline (+ the matching top-face area)
        c.line(pts, rgba(shade(trim_col, 0.9)), 1.2)                       # binding along the neckline
        back = [(u + 192, v * 0.4) for u, v in neckline_pts("crew", min(depth, 6), w)]
        a.polygon(back + [(back[-1][0], -M), (back[0][0], -M)], 0)
    if style in ("tank", "halter", "strapless", "off_shoulder"):
        top = MAX_TOP if style in ("strapless", "off_shoulder") else 0
        sw = max(5.0, float(cut.get("strap_width", 8)))
        if style == "strapless":
            a.band(-M, min(top, float(cut.get("top", 10))), 0)
            c.band(min(top, float(cut.get("top", 10))), min(top, float(cut.get("top", 10))) + 1.2, rgba(shade(trim_col, 0.9)))
        elif style == "off_shoulder":
            t = min(top, float(cut.get("top", 12)))
            a.band(-M, t, 0)
            c.band(t, t + 2, rgba(shade(trim_col, 0.95)))                  # elastic edge
        else:
            a.band(-M, 0, 0)                                               # top face (shoulders) bare ...
            a.rect(128, -M, 192, 22, 0)                                    # ... and armholes on the side faces
            a.rect(320, -M, 384, 22, 0)
            if style == "halter":
                a.rect(0, -M, 128, 18, 0)                                  # bare shoulders in front ...
                body = [(34, 18), (94, 18), (64 + 6, -1), (64 - 6, -1)]    # ... except the high-neck halter panel
                a.polygon(body, 255)
                for k in (-1, 1):                                          # bound edges rising to the neck
                    c.line([(64 + k * 30, 18), (64 + k * 6, -1)], rgba(trim_col), max(1.2, sw * 0.25))
                c.band(-1, 1, rgba(trim_col))                              # neck band (ties behind the neck)
                a.rect(58, -M, 70, 1, 255)
                a.rect(192, -M, 320, 26, 0)                                # open upper back
                a.rect(128, -M, 192, 26, 0)
                a.rect(320, -M, 384, 26, 0)
            else:
                for u in (34, 86 + 8 - sw, 226, 278 + 8 - sw):             # strap bands over the shoulders (front/back mirror)
                    a.rect(u, -M, u + sw, 2, 255)
                    c.rect(u, -M, u + sw, 2, rgba(shade(trim_col, 0.95)))


def arm_cut(fx, cut):
    """Arms are bare for tank / halter / strapless; off-shoulder leaves the shoulder cap bare."""
    if not cut:
        return
    style = cut.get("style", "sleeved")
    if style in ("tank", "halter", "strapless"):
        fx["alpha"].band(-48, 200, 0)
    elif style == "off_shoulder":
        fx["alpha"].band(-48, 12, 0)
