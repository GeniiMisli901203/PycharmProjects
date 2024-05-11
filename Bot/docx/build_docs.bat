.. _configuration:

.. Configuration file for the Sphinx documentation builder.
..
.. This file only contains a selection of the most common options. For a full list see the documentation:
.. https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------
project = 'Misha Vasya Misha'
copyright = '2024, Misha Vasya Misha'
author = 'Misha Vasya Misha'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for autodoc extension -------------------------------------------

# Document all members (class attributes, methods, etc.) including private ones
autodoc_default_options = {
    'members': True,
    'private-members': True,
    'special-members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document
master_doc = 'index'



