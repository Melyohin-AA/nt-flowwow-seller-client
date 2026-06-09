# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'nt-flowwow-seller-client'
copyright = '2026, Artem Melekhin'
author = 'Artem Melekhin'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

add_module_names = False
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# Adding the package's code to PATH

import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', '..').resolve()))


# Disabling Jekyll because it ignores '_sources' and '_static' as they start with '_'

def create_nojekyll(app, exception):
    if exception is None:
        Path(app.outdir, ".nojekyll").touch()

def setup(app):
    app.connect("build-finished", create_nojekyll)
