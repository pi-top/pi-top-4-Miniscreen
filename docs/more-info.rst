====================
Application Overview
====================

This application is built upon the Luma library for communicating to the OLED device.

In most cases, `pt-miniscreen` will play the startup animation once and then switch to a menu interface.

The `TileGroup` deals with the core application functionality:

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


====================
Application Overview
====================

The top level app has main loop running in thread, which waits when a user is using the display, and displays the image for the display context (known as a 'tile group') at the top of the stack. Switching to a new tile group is done by adding it to the app's stack, and returning to a previous tile group is done by popping.

There are 4 total tile groups:
* Bootsplash
* HUD (widget menu)
* Settings
* Screensaver

A "tile group" is just that - a list of bounding boxes that describe how a functionally distinct portion of an image is to be positioned within the displayed image. Tiles can be static, only showing text (for example), or can be dynamic, such as menus. Each tile can have multiple hotspots, which describe a particular object/region within the tile. Each hotspot is created in its own thread, which - if active (i.e. to be displayed) - calls its own render function with a given interval. Note: the interval can be dynamically reset, such as in the case of an animated GIF.

Button press events are handled by the app, which can respond to event announcements to make alterations to the top level tile group - this is how the state manager can invoke the screensaver, for example (i.e. by notifying the app to create a screensaver tile and push it onto the stack). The state manager performs additional button press handling, such as preventing user input during specific situations (e.g. running actions).

Events are handled by using module-level import observer pattern - this produces a singleton-like behaviour that allows for a single interface for responding to different state changes within the app, without higher-level classes requiring extended knowledge of other parts of the application. Optional data can be passed around in this way. Events are primarily used to handle button presses, start/stop actions/temporary tile groups (bootsplash/screensaver), notify the app that an active hotspot has updated its cached image (meaning the app should redraw the next image to the miniscreen), as well as navigating child/parent menus within a menu tile.

All scrolling is done using generators - the same mechanism is used for moving between menu pages as is used for scrolling text.

The general ownership of classes is like so:

``
App -> TileGroup -> Tile -> Hotspot
``

Each tile group uses its 'main' tile to handle button presses, etc. Menu tiles have a menu stack (similar to how the app has a tile group stack), which it uses for entering child menus. Child menus are created as required, similar to tile groups.

Menus have 4 navigation options, depending on context: up/down/child/parent. Some menu pages handle actions on SELECT as opposed to pushing a child menu to the menu tile's stack.

These have a status icon, and broadcast events (mentioned earlier) for changing state. If an action page has a 'get' method, then this used to determine if something is enabled/disabled.

If this cannot be determined, it is left in its default state of UNKNOWN. If a 'get method is not provided, then the icon has a 'play/submit' triangle.

.. ===============
.. Adding Projects
.. ===============

.. Check out `this <https://forum.pi-top.com/t/wip-guide-adding-projects-to-the-system-menu/643>`_ guide for how to start projects from the menu.
.. This is a temporary measure, until a better implementation that supports extensibility.


.. ==============
.. Adding Widgets
.. ==============

.. Check out `this <https://forum.pi-top.com/t/wip-guide-create-new-system-menu-widgets/644/8>`__ guide for how to add widget pages to the menu.
.. This is a temporary measure, until a better implementation that supports extensibility.
