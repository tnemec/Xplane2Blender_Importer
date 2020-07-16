# Xplane2Blender_Importer
Blender import script for X-Plane up to version 11. Compatible with Blender 2.8

This is experimental code and there is no guarantee that it will work for all files. Even if it does import a model, you will lose many of the parameters. This script is only useful to import some geometry, possibly animations and other properties. If you're looking for a quick way to make modifications to an existing aircraft, this is not the tool for you as you will likely lose some of the original properties.

The plugin will import geometry normals and uv maps to give you a starting point for creating aircraft 3D models. If you want to export the model to use in X-Plane PlaneMaker, you will need to install the most recent Xplane2Blender export plugin: https://github.com/X-Plane/XPlane2Blender

Do not redistribute models from other authors without permission. This applies to use of this plugin and using 3D models from other sources. 

The original import code for older Blender verison is originally from https://github.com/daveprue/XPlane2Blender The license in included in the source.

## Installation
* Unzip and place the xplane11import.py file where ever you like. 
* In Blender, select Edit, Preferences, then Add-ons.
* Click the Install... button and browse to the .py file
* Check the checkbox to enable the plugin
* You should see a new entry in the import menu called "XPlane 11 Object (.obj)"

## Usage
From Blender, simply select File -> Import -> XPlane 11 Object (.obj) and choose the Xplane .obj file. A new collection will be added with the same name as the .obj file. All the objects will be created to this collection.

If you have the Blender 2.8 version of the [Xplane2Blender plugin](https://github.com/X-Plane/XPlane2Blender/releases) installed, it will also create some of the datarefs for you.

The location that the object are placed are based on the data in the obj file. If you are importing into an existing Blender model, your reference origin may differ. In this case, select all the imported objects and move them where you would like. Then object -> apply the location.

## Supported OBJ Properties
The import plugin currently supports these properties. Anything else in the OBJ file will be ignored.
Version 1 is primarily for aircraft design, I'm not planning to support scenery object importing at this time.

| Property | Supported | Version |
| ---- | --- | --- |
| Geometry (triangles) | Yes | 1.0 |
| Geometry (lines) | No |  |
| Geometry (lights) | No |  |
| UV Coordinates | Yes | 1.0 |
| Normals | Yes | 1.0 |
| Animations | Partial | 1.0 |
| Manipulatiors | No | Future |
| Albedo Texture | Yes | 1.0 |
| Lit Texture | Yes | 1.1 |
| Normal Map | Yes | 1.1 |
| Scenery Texture Properties | no |  |
| Custom Attributes | Partial | 1.0 |
| NORMAL_METALNESS | No |  |
| Global Properties | No |  |
| Cockpit Regions | No |  |
| LODs | No |  |
| Conditionalization | No |  |
| PARTICLE_SYSTEM | No |  |
| ATTR_layer_group | No |  |
| MAGNET  | No | Future |
| EMITTER | No | Future |


## Animations
When you create a new model, you can apply keyframes to each object directly with transformation and this will export just fine. 

If you have any nested objects, you should use an armature and add keyframes to the armature instead. Or if the rotation angle is more than one axis simultaneously.

The import should retain the animations in most cases. It creates keyframes on the odd frame numbers. Armatures are created whenever there is a nested obj. This may not reflect how the file was originally created but should work for the common cases. I haven't tested rotation in 2 axes on a single keyframe so this may behave badly. 

## Texture Previews
If the TEXTURE, TEXTURE_NORMAL and TEXTURE_LIT directives are present, the texture files will be added as materials for the object which you can preview in Material Preview or Render Preview. The lit texture is assigned to a mix node but with the slider set to only show the diffuse texture. You can open the shader nodes window and move this mix node slider to preview the night texture. 

## Support:
I created this script for personal use and am not really interested in supporting it or instructing on X-Plane modeling. Take a look at the source code, it's well commented, so you may be able to fix issues yourself.

If you want to learn more about creating 3D models in Blender and about the XPlane2Blender plugin, I suggest visiting the [x-plane.org developer forums](https://forums.x-plane.org/index.php?/forums/forum/45-3d-modeling/). There are many helpful members and information located there. This is a big topic with no "training wheels" to get you started. But it can be rewarding.

## Known Issues:
I have only tested this with a small number of files. It may not work on some files at all. 

This is generally a non-descructive script, but please save and backup your working Blender file before running it. It does not write to the .obj file, just reads it.

If it does import your obj file with no errors, it will likely not match the source Blender file. Objects get reordered, armatures are created when needed and some features will not be imported. This can help as a starting point, not as a way to cleanly convert older models. Models from earlier versions of Blender and the export plugin may not match up well with recent Blender versions.

Nested animations are especially tricky as there are many valid ways to organize the obj file. I'm making some assumptions about the structure, so some files, including the included Laminar Reasearch aircraft may not import cleanly. 

One way to fix this is to copy the obj file and make some changes in a text editor before importing. Specifically, I expect that an ANIM_begin line marks the set of animations for one armature. You can add these to help guide the importer to understand which objects should be parented to others.

The script will not import most of the properties, LODs, lighting and so on. Eventually some of these may be implemented. The code is open source, why not try and extend it yourself?

If the obj was exported with the Print debug info, the importer can name the objects with the original names. Otherwise, everything gets named as OBJ1, OBJ2 and so on. 

## Releases
Visit [Releases](https://github.com/tnemec/Xplane2Blender_Importer/releases) to get the latest stable(ish) version. 

The Master branch includes the current development, so it may have improvements and/or bugs. 


