# Xplane2Blender_Importer
Blender import script for X-Plane up to version 11. Compatible with Blender 2.8

This is experimental code and there is no guarantee that it will work for all files. Even if it does import a model, you will lose many of the parameters. This script is only useful to import some geometry, you will need to add animations and other properties. This is not a tool to make minor edits to a obj and expect to export it intact.

The plugin will import geometry normals and uv maps. If you want to import animations, you will need to install the most recent Xplane2Blender export plugin: https://github.com/X-Plane/XPlane2Blender

Do not redistribute models from other authors without permission. 

The original import code for older Blender verison is originally from https://github.com/daveprue/XPlane2Blender 

## Known Issues:
The script can only import some types of animations. If the model was build with nested objects with bones, this is more complicated than I can tackle at the moment. 