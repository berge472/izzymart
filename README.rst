IzzyMart 
========

This repo contains a webapp for a kid friendly self checkout system for a pretend store called IzzyMart. It is built using Vue3 with Vuetify for the frontend, and a Python FastAPI backend with MongoDB for data storage.

Demo Vide: 

.. image:: doc/screenshot.png

https://youtu.be/B3PXOTO2d2E?si=Sg4PqpMot2eU77Ay


Using IzzyMart
--------------

There is a live instance of IzzyMart running at: https://izzymart.app that anyone can use. 

Scanning 
~~~~~~~~

The app works best with a barcode scanner (Tested with the `Symcode 2D Bluetooth Scanner <https://www.amazon.com/dp/B01M264K5L>`_ , but it should work with most scanners). Just connect the scanner to your computer/tablet and scan the barcodes of the items to add them to your cart.

You can also enable camera scanning by going to the customization panel (click the store icon in the top left corner) and enabling "Camera Scanning". This will allow you to scan items using your device's camera. This works on some devices but really depends on the camera quality and lighting conditions.


Customization 
~~~~~~~~~~~~~

The customization panel can be opened by clicking the store icon in the top left corner. From here you can change various settings such as:

- Store Name
- Store Colors
- Enable Camera Scanning


Self hosting 
------------

This repo contains helm charts and a docker-compose file for easy self hosting. I will be adding more detailed instructions for this soon... 

