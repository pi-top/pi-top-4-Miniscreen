=============================================
pi-top [4] Miniscreen Widget/Menu Application
=============================================

A simple Python-based widget and menu application that uses the pi-top [4]'s miniscreen OLED display and buttons.

.. TODO: GIF of cycling through the images using CLI capture

--------------------
Build Status: Latest
--------------------

.. image:: https://img.shields.io/github/workflow/status/pi-top/pt-sys-oled/Build,%20Test%20and%20Publish
   :alt: GitHub Workflow Status

.. image:: https://img.shields.io/github/v/tag/pi-top/pt-sys-oled
    :alt: GitHub tag (latest by date)

.. image:: https://img.shields.io/github/v/release/pi-top/pt-sys-oled
    :alt: GitHub release (latest by date)

.. https://img.shields.io/codecov/c/gh/pi-top/pt-sys-oled?token=hfbgB9Got4
..   :alt: Codecov

-----
About
-----

This application aims to provide an easy-to-use interface for accessing commonly useful system information, and to also manage some key settings (such as enabling/disabling SSH/VNC services).

`pt-sys-oled` is included out-of-the-box with pi-topOS.

Ensure that you keep your system up-to-date to enjoy the latest features and bug fixes.

This application is installed as a Python 3 script that is managed by a systemd service, configured to automatically run on startup and restart during software updates.

------------
Installation
------------

`pt-sys-oled` is installed out of the box with pi-topOS, which is available from
pi-top.com_. To install on Raspberry Pi OS or other operating systems, check out the `Using pi-top Hardware with Raspberry Pi OS`_ page on the pi-top knowledge base.

.. _pi-top.com: https://www.pi-top.com/products/os/

.. _Using pi-top Hardware with Raspberry Pi OS: https://knowledgebase.pi-top.com/knowledge/pi-top-and-raspberry-pi-os

----------------
More Information
----------------

Please refer to the `More Info`_ documentation in this repository
for more information about the application.

.. _More Info: https://github.com/pi-top/pt-sys-oled/blob/master/docs/more-info.rst

------------
Contributing
------------

Please refer to the `Contributing`_ document in this repository
for information on contributing to the project.

.. _Contributing: https://github.com/pi-top/pt-sys-oled/blob/master/.github/CONTRIBUTING.md

See the `contributors page`_ on GitHub for more info on contributors.

.. _contributors page: https://github.com/pi-top/pitop/graphs/contributors
