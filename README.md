# Xplane2Blender_Importer
Blender import script for X-Plane up to version 11. Compatible with Blender 2.8

This is experimental code and there is no guarantee that it will work for all files. Even if it does import a model, you will lose many of the parameters. This script is only useful to import some geometry, you will need to add animations and other properties. This is not a tool to make minor edits to a obj and expect to export it intact.

The plugin will import geometry normals and uv maps. If you want to import animations, you will need to install the most recent Xplane2Blender export plugin: https://github.com/X-Plane/XPlane2Blender

Do not redistribute models from other authors without permission. 

The original import code for older Blender verison is originally from https://github.com/daveprue/XPlane2Blender 

## Installation
* Unzip and place the xplane11import.py file where ever you like. 
* In Blender, select Edit, Preferences, then Add-ons.
* Click the Install... button and browse to the .py file
* Check the checkbox to enable the plugin
* You should see a new entry in the import menu called "XPlane 11 Object (.obj)"

## Usage
From Blender, simply select File -> Import -> XPlane 11 Object (.obj) and choose the Xplane .obj file. A new collection will be added with the same name as the .obj file. All the objects will be created to this collection. 

## Known Issues:
The script can only import some types of animations. If the model was build with nested objects with bones, this is more complicated than I can tackle at the moment.

I have only tested this with a small number of files. It may not work on some files at all. 

The script will not import most of the properties, LODs, lighting and so on. Eventually some of these may be implemented. The code is open source, why not try and extend it yourself?

If the obj was exported with the Print debug info, the importer can name the objects with the original names. Otherwise, everything gets named as OBJ1, OBJ2 and so on. 