# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
from pathlib import Path

project = "gitmopy"
copyright = "2023, vict0rsch"
author = "vict0rsch"

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

version = [
    line.split("=")[-1].strip().replace('"', "")
    for line in (ROOT / "pyproject.toml").read_text().splitlines()
    if line.startswith("version = ")
][0]
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.viewcode",
    "sphinx_math_dollar",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.todo",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True


# Configuration section from vipyto:
# ----------------------------------

# Configuratiion for sphinx.ext.autodoc & autoapi.extension
# https://autoapi.readthedocs.io/

autodoc_typehints = "description"
autoapi_type = "python"
autoapi_dirs = [str(ROOT / "gitmopy")]
autoapi_member_order = "groupwise"
autoapi_template_dir = "_templates/autoapi"
autoapi_python_class_content = "init"
autoapi_options = [
    "members",
    "undoc-members",
]
autoapi_keep_files = False

# Configuration for sphinx_math_dollar

# sphinx_math_dollar
# https://www.sympy.org/sphinx-math-dollar/

# Note: CHTML is the only output format that works with \mathcal{}
mathjax_path = "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML"
mathjax3_config = {
    "tex": {
        "inlineMath": [
            ["$", "$"],
            ["\\(", "\\)"],
        ],
        "processEscapes": True,
    },
    "jax": ["input/TeX", "output/CommonHTML", "output/HTML-CSS"],
}

# Configuration for sphinx_autodoc_typehints
# https://github.com/tox-dev/sphinx-autodoc-typehints
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
typehints_defaults = "comma"

# Configuration for the MyST (markdown) parser
# https://myst-parser.readthedocs.io/en/latest/intro.html
myst_enable_extensions = ["colon_fence"]

# Configuration for sphinxext.opengraph
# https://sphinxext-opengraph.readthedocs.io/en/latest/

ogp_site_url = "TODO"
ogp_social_cards = {
    "enable": True,
    "image": "./_static/images/SOME_IMAGE",
}
