import matplotlib.pyplot

line_styles = [ \
    ('-', "solid line style"),
    ('--', "dashed line style"),
    ('-.', "dash-dot line style"),
    (',', "dotted line style"),
    ('.', "point marker"),
    (',', "pixel marker"),
    ('o', "circle marker"),
    ('v', "triangle_down marker"),
    ('^', "triangle_up marker"),
    ('<', "triangle_left marker"),
    ('>', "triangle_right marker"),
    ('1', "tri_down marker"),
    ('2', "tri_up marker"),
    ('3', "tri_left marker"),
    ('4', "tri_right marker"),
    ('s', "square marker"),
    ('p', "pentagon marker"),
    ('*', "star marker"),
    ('h', "hexagon1 marker"),
    ('H', "hexagon2 marker"),
    ('+', "plus marker"),
    ('x', "x marker"),
    ('D', "diamond marker"),
    ('d', "thin_diamond marker"),
    ('|', "vline marker"),
    ('_', "hline marker"),
],

marker_styles = [ \
    (7, "caretdown"),
    (4, "caretleft"),
    (5, "caretright"),
    (6, "caretup"),
    ('o', "circle"),
    ('D', "diamond"),
    ('h', "hexagon1"),
    ('H', "hexagon2"),
    ('_', "hline"),
    ('', "nothing"),
    ('8', "octagon"),
    ('p', "pentagon"),
    (',', "pixel"),
    ('+', "plus"),
    ('.', "point"),
    ('s', "square"),
    ('*', "star"),
    ('d', "thin_diamond"),
    (3, "tickdown"),
    (0, "tickleft"),
    (1, "tickright"),
    (2, "tickup"),
    ('1', "tri_down"),
    ('3', "tri_left"),
    ('4', "tri_right"),
    ('2', "tri_up"),
    ('v', "triangle_down"),
    ('<', "triangle_left"),
    ('>', "triangle_right"),
    ('^', "triangle_up"),
    ('|', "vline"),
    ('x', "x"),
],

xy_plot_parameters = [ \
    ("linestyle", { \
        "type": "choice",
        "label": "Line style",
        "choices": line_styles,
    }),
    ("color", { \
        "type": "color_choice",
        "label": "Line color"
    }),
    ("alpha", { \
        "type": "float",
        "label": "Alpha",
        "min": 0.0,
        "max": 1.0,
    }),
    ("linewidth", { \
        "type": "float",
        "label": "Line width",
        "min": 0.0,
        "max": 10.0,
    }),
    ("marker", { \
        "type": "choice",
        "label": "Marker style",
        "choices": marker_styles,
    }),
    ("markeredgecolor", { \
        "type": "color_choice",
        "label": "Marker edge color"
    }),
    ("markeredgewidth", { \
        "type": "float",
        "label": "Marker edge width",
        "min": 0.0,
        "max": 10.0,
    }),
    ("markerfacecolor", { \
        "type": "color_choice",
        "label": "Marker face color"
    }),
    ("markerfacecoloralt", { \
        "type": "color_choice",
        "label": "Marker face color 2",
        "min": 0.0,
        "max": 10.0,
    }),
    ("markersize", { \
        "type": "float",
        "label": "Marker size",
        "min": 0.0,
        "max": 10.0,
    }),
]

hist_parameters = [ \
    ("bins", { \
        "type": "integer|list",
        "label": "Number of histogram bins",
    }),
    ("color", { \
        "type": "color_choice",
        "label": "Line color"
    }),
]

charts = [ \
    ("xy_plot", { \
        "command": matplotlib.pyplot.plot,
        "label": "XY plot",
        "dim": 2,
        "multiplot": True,
        "parameters": xy_plot_parameters,
    }),
    ("histogram", { \
        "command": matplotlib.pyplot.hist,
        "label": "1D histogram",
        "dim": 1,
        "multiplot": False,
        "parameters": hist_parameters,
    }),
]