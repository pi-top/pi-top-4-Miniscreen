====================
Application Overview
====================

This application is built upon the Luma library for communicating to the OLED device.

In most cases, `pt-miniscreen` will play the startup animation once and then switch to a menu interface.

The `TileManager` deals with the core application functionality:

* handling miniscreen button presses
* managing all menus
* checking if the current menu has a new image
* displaying to miniscreen when the image has changed
* pausing displaying to the miniscreen while the user has taken control

Displaying to the miniscreen object is done via the miniscreen object in the pi-top Python SDK.

Each menu is comprised of multiple pages that are navigated between with the miniscreen buttons. Menu pages have actions that can be triggered by using the select button. Each page has a hotspot that represents what is to be displayed on the OLED display while the menu is on that page.


===============
Useful Commands
===============

Restart the service:

..
  sudo systemctl restart pt-miniscreen


===============
Adding Projects
===============

Check out `this <https://forum.pi-top.com/t/wip-guide-adding-projects-to-the-system-menu/643>`_ guide for how to start projects from the menu.
This is a temporary measure, until a better implementation that supports extensibility.


==============
Adding Widgets
==============

Check out `this <https://forum.pi-top.com/t/wip-guide-create-new-system-menu-widgets/644/8>`__ guide for how to add widget pages to the menu.
This is a temporary measure, until a better implementation that supports extensibility.
