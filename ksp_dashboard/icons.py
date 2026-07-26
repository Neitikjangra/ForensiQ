"""
icons.py
--------
A small, dependency-free inline-SVG icon set used throughout the dashboard
in place of emoji "logos". Every icon is authored as plain SVG primitives
(circle/rect/line/polyline/path) on a 24x24 grid so they render identically
everywhere, scale crisply, and inherit colour via `currentColor` (no network
requests, no icon fonts, no external assets).

Usage:
    from icons import icon
    icon("shield")                       # 18px, default stroke
    icon("bell", size=20, cls="nav-ic")  # custom size / css class
"""

# Each value is the *inner* markup of an <svg> (paths/shapes only).
_ICONS = {
    # ---- brand / general -------------------------------------------------
    "shield": '<path d="M12 2.5l7.5 3v6c0 5-3.2 8.3-7.5 9.7-4.3-1.4-7.5-4.7-7.5-9.7v-6l7.5-3z"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6"/>',
    "grid": '<rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1.5"/><rect x="13" y="3.5" width="7.5" height="7.5" rx="1.5"/><rect x="3.5" y="13" width="7.5" height="7.5" rx="1.5"/><rect x="13" y="13" width="7.5" height="7.5" rx="1.5"/>',
    "sparkles": '<path d="M11 3.5 L13.4 8.6 L18.5 11 L13.4 13.4 L11 18.5 L8.6 13.4 L3.5 11 L8.6 8.6 Z"/><path d="M18.5 2.8 L19.52 4.98 L21.7 6 L19.52 7.02 L18.5 9.2 L17.48 7.02 L15.3 6 L17.48 4.98 Z"/>',
    "message_square": '<path d="M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H10l-4.2 3.4a.6.6 0 0 1-1-.47V16H5a1 1 0 0 1-1-1z"/>',
    "bar_chart": '<line x1="5" y1="20" x2="5" y2="12"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="19" y1="20" x2="19" y2="15"/><line x1="3" y1="20" x2="21" y2="20"/>',
    "map_pin": '<path d="M12 21s7-6.6 7-12a7 7 0 1 0-14 0c0 5.4 7 12 7 12z"/><circle cx="12" cy="9" r="2.4"/>',
    "share": '<circle cx="5.5" cy="12" r="2.5"/><circle cx="18.5" cy="5.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/><line x1="7.7" y1="10.8" x2="16.3" y2="6.7"/><line x1="7.7" y1="13.2" x2="16.3" y2="17.3"/>',
    "trending_up": '<polyline points="3 17 9.5 10.5 13.5 14.5 21 6"/><polyline points="14.5 6 21 6 21 12.5"/>',
    "trending_down": '<polyline points="3 7 9.5 13.5 13.5 9.5 21 18"/><polyline points="21 11.5 21 18 14.5 18"/>',
    "folder_search": '<path d="M3 6.5a1 1 0 0 1 1-1h4.2l1.6 2h9.2a1 1 0 0 1 1 1V17a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><circle cx="11.3" cy="13" r="2.6"/><line x1="13.2" y1="14.9" x2="15" y2="16.7"/>',
    "users": '<circle cx="8.7" cy="8.2" r="3.3"/><path d="M2.8 20c0-3.4 2.6-6.1 5.9-6.1s5.9 2.7 5.9 6.1"/><circle cx="16.6" cy="8" r="2.7"/><path d="M14.6 14c2.7.4 4.9 2.9 4.9 6"/>',
    "car": '<path d="M4.5 16.5V12l1.8-4.3a1.5 1.5 0 0 1 1.4-.9h8.6a1.5 1.5 0 0 1 1.4.9L19.5 12v4.5"/><rect x="3.2" y="12" width="17.6" height="5" rx="1.6"/><circle cx="7.5" cy="18.2" r="1.6"/><circle cx="16.5" cy="18.2" r="1.6"/>',
    "bell": '<path d="M6 10.5a6 6 0 1 1 12 0c0 4 1.2 5.4 1.9 6.1a.7.7 0 0 1-.5 1.2H4.6a.7.7 0 0 1-.5-1.2C4.8 15.9 6 14.5 6 10.5z"/><path d="M9.6 19.6a2.4 2.4 0 0 0 4.8 0"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.7 14"/>',
    "settings": '<path d="M12.0 2.8 L14.53 5.9 L18.51 5.49 L18.1 9.47 L21.2 12.0 L18.1 14.53 L18.51 18.51 L14.53 18.1 L12.0 21.2 L9.47 18.1 L5.49 18.51 L5.9 14.53 L2.8 12.0 L5.9 9.47 L5.49 5.49 L9.47 5.9 Z"/><circle cx="12" cy="12" r="2.9"/>',
    "phone": '<rect x="7" y="2.2" width="10" height="19.6" rx="2.2"/><line x1="10.6" y1="18.2" x2="13.4" y2="18.2"/>',
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.4" y2="16.4"/>',
    "chevron_down": '<polyline points="5.5 8.5 12 15 18.5 8.5"/>',
    "log_out": '<path d="M9.5 21H5.6a1.6 1.6 0 0 1-1.6-1.6V4.6A1.6 1.6 0 0 1 5.6 3H9.5"/><polyline points="15.5 16.5 21 11 15.5 5.5"/><line x1="21" y1="11" x2="9" y2="11"/>',
    # ---- kpi / stat icons ---------------------------------------------
    "file_text": '<path d="M6.2 2.6h8.4l4.2 4.2V20.4a1 1 0 0 1-1 1H6.2a1 1 0 0 1-1-1V3.6a1 1 0 0 1 1-1z"/><path d="M14.6 2.6v4.2h4.2"/><line x1="8.3" y1="12.3" x2="15.7" y2="12.3"/><line x1="8.3" y1="15.9" x2="15.7" y2="15.9"/><line x1="8.3" y1="8.7" x2="11.3" y2="8.7"/>',
    "check_circle": '<circle cx="12" cy="12" r="9"/><polyline points="7.8 12.3 10.5 15 16.3 9"/>',
    "percent": '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="7.3" cy="7.3" r="2.6"/><circle cx="16.7" cy="16.7" r="2.6"/>',
    "user": '<circle cx="12" cy="8.2" r="3.7"/><path d="M4.5 20.5c0-4.1 3.4-7.5 7.5-7.5s7.5 3.4 7.5 7.5"/>',
    "flame": '<path d="M12 3c2.4 2.9 4.8 5.7 4.8 9.3a4.8 4.8 0 0 1-9.6 0c0-1.6.55-2.7 1.4-3.9.3 1.6 1.15 2.3 1.83 1.73C9.6 8.5 10.6 6.9 12 3z"/><path d="M12 9.2c.9 1.4 1.7 2.5 1.7 3.7a1.7 1.7 0 1 1-3.4 0c0-.8.4-1.5.95-2.1"/>',
    "tag": '<path d="M3 11.6V4.6a1 1 0 0 1 1-1h7l9 9-8 8-9-9z"/><circle cx="7.6" cy="7.6" r="1.35"/>',
    "star": '<polygon points="12.0,3.0 14.35,8.76 20.56,9.22 15.8,13.24 17.29,19.28 12.0,16.0 6.71,19.28 8.2,13.24 3.44,9.22 9.65,8.76"/>',
    # ---- alerts ----------------------------------------------------------
    "alert_triangle": '<path d="M12 3.2 L21.5 20 L2.5 20 Z"/><line x1="12" y1="9.3" x2="12" y2="14.3"/><circle cx="12" cy="16.9" r="0.9" fill="currentColor" stroke="none"/>',
    "lock": '<rect x="5" y="10.8" width="14" height="9.4" rx="2"/><path d="M8 10.8V7.4a4 4 0 0 1 8 0v3.4"/>',
    "alert_circle": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="7.6" x2="12" y2="13"/><circle cx="12" cy="16.3" r="0.9" fill="currentColor" stroke="none"/>',
    # ---- settings / profile ----------------------------------------------
    "upload": '<path d="M12 15.5V4.5"/><polyline points="7.5 9 12 4.5 16.5 9"/><path d="M4.5 15.5v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-3"/>',
    "image": '<rect x="3.2" y="4.2" width="17.6" height="15.6" rx="2"/><circle cx="8.3" cy="9.3" r="1.7"/><path d="M4 17.5l5.3-5.3a1.5 1.5 0 0 1 2.1 0l1.9 1.9"/><path d="M12.5 15.5l2.7-2.7a1.5 1.5 0 0 1 2.1 0l2.5 2.5"/>',
    "save": '<path d="M5 4h11l3.5 3.5v12A1.5 1.5 0 0 1 18 21H5a1.5 1.5 0 0 1-1.5-1.5v-14A1.5 1.5 0 0 1 5 4z"/><path d="M8 4v5h7V4"/><path d="M7.5 21v-6.5h9V21"/>',
    "x": '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>',
    "paperclip": '<path d="M18.5 10.2 10 18.7a3.6 3.6 0 0 1-5-5l9-9a2.6 2.6 0 0 1 3.6 3.6l-8.6 8.6a1.4 1.4 0 0 1-2-2l7.6-7.6"/>',
    "building": '<rect x="4.5" y="3.5" width="10" height="17" rx="1"/><line x1="7.5" y1="7" x2="7.5" y2="7.01"/><line x1="11" y1="7" x2="11" y2="7.01"/><line x1="7.5" y1="10.5" x2="7.5" y2="10.51"/><line x1="11" y1="10.5" x2="11" y2="10.51"/><line x1="7.5" y1="14" x2="7.5" y2="14.01"/><line x1="11" y1="14" x2="11" y2="14.01"/><path d="M14.5 9.5H19a.5.5 0 0 1 .5.5v10.5h-5"/>',
    "mail": '<rect x="3.2" y="5.2" width="17.6" height="13.6" rx="1.6"/><polyline points="3.6 6 12 12.5 20.4 6"/>',
    "id": '<rect x="3" y="5" width="18" height="14" rx="1.8"/><circle cx="8.3" cy="12" r="2.2"/><path d="M5.7 16.3c.4-1.5 1.5-2.4 2.6-2.4s2.2.9 2.6 2.4"/><line x1="13.6" y1="9.6" x2="18" y2="9.6"/><line x1="13.6" y1="12.6" x2="18" y2="12.6"/><line x1="13.6" y1="15.6" x2="16.3" y2="15.6"/>',
    "cpu": '<rect x="7" y="7" width="10" height="10" rx="1.5"/><rect x="10" y="2.5" width="1.8" height="3"/><rect x="12.5" y="2.5" width="1.8" height="3"/><rect x="10" y="18.5" width="1.8" height="3"/><rect x="12.5" y="18.5" width="1.8" height="3"/><rect x="2.5" y="10" width="3" height="1.8"/><rect x="2.5" y="12.5" width="3" height="1.8"/><rect x="18.5" y="10" width="3" height="1.8"/><rect x="18.5" y="12.5" width="3" height="1.8"/>',
    "download": '<path d="M12 4.5v11"/><polyline points="7.5 11 12 15.5 16.5 11"/><path d="M4.5 15.5v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-3"/>',
    "filter": '<path d="M3.5 4.5h17L14 12.5v6l-4 2v-8z"/>',
    "sort": '<path d="M7 4.5v13"/><polyline points="4 7.5 7 4.5 10 7.5"/><path d="M17 19.5v-13"/><polyline points="20 16.5 17 19.5 14 16.5"/>',
    "print": '<polyline points="6.5 8.5 6.5 3.5 17.5 3.5 17.5 8.5"/><rect x="4" y="8.5" width="16" height="8" rx="1.5"/><rect x="6.5" y="13" width="11" height="7.5"/>',
    "menu": '<line x1="3.5" y1="6.5" x2="20.5" y2="6.5"/><line x1="3.5" y1="12" x2="20.5" y2="12"/><line x1="3.5" y1="17.5" x2="20.5" y2="17.5"/>',
    "flag": '<path d="M5 21V4"/><path d="M5 4.5h13l-3.2 4 3.2 4H5"/>',
}


def icon(name, size=18, cls="icon", stroke_width=1.8, title=None):
    """Return an inline <svg> element for the given icon name."""
    inner = _ICONS.get(name)
    if inner is None:
        raise KeyError(f"Unknown icon: {name!r}")
    title_tag = f"<title>{title}</title>" if title else ""
    return (
        f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{title_tag}{inner}</svg>'
    )


def icon_names():
    return sorted(_ICONS.keys())


def icon_inner(name):
    """Return the raw inner markup (paths/shapes only, no <svg> wrapper) for
    a given icon name. Useful when embedding an icon inside a hand-built SVG
    that already establishes its own viewport (e.g. a nested <svg x="".."">
    node in a larger diagram)."""
    if name not in _ICONS:
        raise KeyError(f"Unknown icon: {name!r}")
    return _ICONS[name]
