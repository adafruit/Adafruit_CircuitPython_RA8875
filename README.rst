Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ra8875/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/ra8875/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_RA8875/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_RA8875/actions/
    :alt: Build Status

This is a full featured CircuitPython Library for the RA8875 that included all of the hardware
accelerated drawing functions as the original Arduino library. A lot of the functionality has
been streamlined with a focus on ease of use that is still flexible enough to make full use of
the hardware. For instace, Graphics and Text mode switching is now automatic and handled in the
background.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-ra8875/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ra8875
    
To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ra8875
    
To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-ra8875
    
Usage Example
=============

See examples/ra8875_simpletest.py and examples/ra8875_bmptest.py for examples of the module's usage. When 
running the bmptest, be sure to upload the blinka.bmp image to the root folder as well.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_RA8875/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
