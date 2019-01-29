LICENSES = (
    ("BY", "Attribution"),
    ("BY-NC", "Attribution NonCommercial"),
    ("BY-ND", "Attribution NoDerivatives"),
    ("BY-SA", "Attribution ShareAlike"),
    ("BY-NC-ND", "Attribution NonCommercial NoDerivatives"),
    ("BY-NC-SA", "Attribution NonCommercial ShareAlike"),
    ("PDM", "Public Domain Mark"),
    ("CC0", "Public Domain Dedication"),
)

LICENSE_GROUPS = {
    # All open licenses
    "all": {'BY', 'BY-NC', 'BY-ND', 'BY-SA', 'BY-NC-ND', 'BY-NC-SA', 'PDM',
            'CC0'},
    # All CC licenses
    "all-cc": {'BY', 'BY-NC', 'BY-ND', 'BY-SA', 'BY-NC-ND', 'BY-NC-SA'},
    # All licenses allowing commercial use
    "commercial": {'BY', 'BY-SA', 'BY-ND', 'CC0', 'PDM'},
    # All licenses allowing modifications
    "modification": {'BY', 'BY-SA', 'BY-NC', 'BY-NC-SA', 'CC0', 'PDM'},
}
