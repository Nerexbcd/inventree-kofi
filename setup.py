# -*- coding: utf-8 -*-

import setuptools

from inventree_kofi.version import PLUGIN_VERSION

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-kofi",
    version=PLUGIN_VERSION,
    author="Abílio Páscoa",
    author_email="me@nerexbcd.dev",
    description="InvenTree plugin that Integrates with Kofi",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="inventree inventreeplugins plugins kofi",
    url="https://github.com/Nerexbcd/inventree-kofi",
    license="MIT",

    packages=setuptools.find_packages(),
    
    include_package_data=False,

    install_requires=[
        "inventree-plugins",
        "requests",
        "beautifulsoup4",
    ],

    setup_requires=[
        "wheel",
    ],

    python_requires=">=3.9",

    entry_points={
        "inventree_plugins": [
            "KofiPlugin = inventree_kofi.kofi_Plugin:KofiPlugin",
        ]
    },
)