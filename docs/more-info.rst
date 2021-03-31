====================
Application Overview
====================

This application is built upon the Luma library for communicating to the OLED device.

In most cases, `pt-sys-oled` will play the startup animation once and then switch to a menu interface.

The `MenuManager` deals with the core application functionality:

* handling miniscreen button presses
* managing all menus
* checking if the current menu has a new image
* displaying to miniscreen when the image has changed
* pausing displaying to the miniscreen while the user has taken control

Displaying to the miniscreen object is done via the miniscreen object in the pi-top Python SDK.

Each menu is comprised of multiple pages that are navigated between with the miniscreen buttons. Menu pages have actions that can be triggered by using the select button. Each page has a hotspot that represents what is to be displayed on the OLED display while the menu is on that page.
