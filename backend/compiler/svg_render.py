"""
SVG Flowchart Renderer
-------------------------
Takes the positioned graph produced by cfg.build_cfg() and renders it
as a real, scalable, graphical SVG diagram (never ASCII / plain text).
Standard flowchart shapes are used: ovals for start/end, rectangles for
statements, diamonds for conditions, with directional arrows and
Yes/No branch labels. Native <title> tags give hover tooltips.
"""

import html

NODE_W = 190
NODE_H = 56
DIAMOND_W = 210
DIAMOND_H = 84
PAD_TOP = 40
PAD_X = 140

COLORS = {
    "start": ("#7c3aed", "#a78bfa"),
    "end": ("#7c3aed", "#a78bfa"),
    "process": ("#18213a", "#3b82f6"),
    "decision": ("#1c1a33", "#f59e0b"),
}


def _esc(text):
    return html.escape(str(text), quote=True)


def _truncate(text, limit=26):
    text = str(text)
    if len(text) > limit:
        return text[: limit - 1] + "\u2026"
    return text


def _node_box(node):
    """Return (left, top, right, bottom, cx, cy) for a node."""
    x, y = node["x"], node["y"]
    if node["type"] == "decision":
        w, h = DIAMOND_W, DIAMOND_H
    elif node["type"] in ("start", "end"):
        w, h = 150, 54
    else:
        w, h = NODE_W, NODE_H
    return x - w / 2, y - h / 2, x + w / 2, y + h / 2, x, y


def _render_node(node):
    fill, stroke = COLORS[node["type"]]
    left, top, right, bottom, cx, cy = _node_box(node)
    label_full = node["label"]
    label = _truncate(label_full)
    title = f"<title>{_esc(label_full)}{' (line ' + str(node['line']) + ')' if node.get('line') else ''}</title>"

    if node["type"] in ("start", "end"):
        w, h = right - left, bottom - top
        shape = (
            f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        text_color = "#ffffff"
    elif node["type"] == "decision":
        w, h = right - left, bottom - top
        points = f"{cx},{top} {right},{cy} {cx},{bottom} {left},{cy}"
        shape = (
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        text_color = "#fcd34d"
    else:
        shape = (
            f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" rx="10" ry="10" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        text_color = "#dbeafe"

    text = (
        f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="Consolas, Menlo, monospace" font-size="12.5" fill="{text_color}">{_esc(label)}</text>'
    )
    return f'<g class="cfg-node" data-line="{node.get("line",0)}">{title}{shape}{text}</g>'


def _anchor_bottom(node):
    _, _, _, bottom, cx, _ = _node_box(node)
    return cx, bottom


def _anchor_top(node):
    left, top, right, _, cx, _ = _node_box(node)
    return cx, top


def _anchor_right(node):
    _, top, right, bottom, _, cy = _node_box(node)
    return right, cy


def _render_edge(edge, node_by_id, is_loop):
    src = node_by_id[edge["from"]]
    dst = node_by_id[edge["to"]]
    label = edge["label"]

    if is_loop:
        x1, y1 = _anchor_right(src) if src["type"] != "decision" else _anchor_bottom(src)
        x1, y1 = src["x"] + (DIAMOND_W / 2 if src["type"] == "decision" else NODE_W / 2), src["y"]
        # actually draw from bottom of the last body node, curving to the right side of decision
        bx, by = _anchor_bottom(src)
        dx, dy = _anchor_right(dst)
        midx = max(bx, dx) + 90
        path = f"M {bx} {by} C {midx} {by}, {midx} {dy}, {dx} {dy}"
        label_x, label_y = midx, (by + dy) / 2
        stroke = "#f87171"
        dash = 'stroke-dasharray="6,4"'
    else:
        sx, sy = _anchor_bottom(src)
        tx, ty = _anchor_top(dst)
        midy = (sy + ty) / 2
        if abs(sx - tx) < 1:
            path = f"M {sx} {sy} L {tx} {ty}"
        else:
            path = f"M {sx} {sy} L {sx} {midy} L {tx} {midy} L {tx} {ty}"
        label_x, label_y = (sx + tx) / 2 + (14 if sx != tx else 14), midy - 6
        stroke = "#22c55e" if label == "Yes" else ("#f87171" if label == "No" else "#64748b")
        dash = ""

    marker = ' marker-end="url(#arrowhead)"'
    edge_svg = f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="2" {dash}{marker}/>'
    label_svg = ""
    if label:
        label_svg = (
            f'<text x="{label_x}" y="{label_y}" font-family="Consolas, Menlo, monospace" '
            f'font-size="11.5" font-weight="600" fill="{stroke}">{_esc(label)}</text>'
        )
    return edge_svg + label_svg


def render_svg(graph):
    nodes = graph["nodes"]
    edges = graph["edges"]
    bounds = graph["bounds"]

    node_by_id = {n["id"]: n for n in nodes}

    view_min_x = bounds["minX"]
    view_width = bounds["width"]
    view_height = bounds["height"] + PAD_TOP

    defs = (
        '<defs>'
        '<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#94a3b8"/>'
        '</marker>'
        '</defs>'
    )

    edge_svgs = []
    for edge in edges:
        is_loop = edge["label"] == "loop back"
        edge_svgs.append(_render_edge(edge, node_by_id, is_loop))

    node_svgs = [_render_node(n) for n in nodes]

    body = (
        f'<g transform="translate(0,{PAD_TOP})">' + "".join(edge_svgs) + "".join(node_svgs) + "</g>"
    )

    svg = (
        f'<svg viewBox="{view_min_x} 0 {view_width} {view_height}" '
        f'xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" '
        f'font-family="Consolas, Menlo, monospace">'
        f'{defs}{body}</svg>'
    )
    return svg
