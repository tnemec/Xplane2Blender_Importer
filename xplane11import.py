#---------------------------------------------------------------------------
#
#  Import an X-Plane .obj file into Blender 2.78
#
# Dave Prue <dave.prue@lahar.net>
#
# MIT License
#
# Copyright (c) 2017 David C. Prue
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#---------------------------------------------------------------------------    


# imports obj format up to X-Plane 11 into Blender 2.8+

# Orginal script: https://github.com/daveprue/XPlane2Blender


import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Euler
import itertools
import os

bl_info = {
    "name": "Import X-Plane OBJ",
    "author": "Tony Nemec - original script by David C. Prue",
    "version": (0,1,0),
    "blender": (2,80,0),
    "api": 36273,
    "location": "File > Import/Export > XPlane",
    "description": "Import X-Plane obj",
    "category": "Import-Export"
}

class xplane11import(bpy.types.Operator):
    bl_label = "Import X-Plane OBJ"
    bl_idname = "object.xplane11import"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")


    def execute(self, context):
        global collection
        print("execute %s" % self.filepath)
        # create new collection to match filename
        collection = bpy.data.collections.new(self.filepath.split('\\')[-1].split('.')[0])
        bpy.context.scene.collection.children.link(collection)
        # do the import      
        numObj = self.run((0,0,0))
        print('Imported %d objects' % numObj)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def getMessage(self, messageType):
        if(messageType == 'dataref'):
            return 'Failed to create XPlane dataref. Make sure you have the XPlane2Blender plugin enabled.'
        return ''


    def createKeyframes(self, obKeyframes, ob):
        curFrame = 1
        dataref = ''
        dataref_index = 0
        for kf in obKeyframes:           
            bpy.context.scene.frame_set(curFrame)
            if(len(kf)):
                if(kf[0] == 'loc'):
                    # kf = ('loc', o_t, param1, dataref)
                    if(kf[3] == 'none'):
                        # don't create a keyframe for 'none' dataref
                        continue

                    # first create the Blender keyframe
                    ob.location = kf[1]
                    ob.keyframe_insert(data_path='location', frame=curFrame)

                    curFrame += 2

                    try:
                        # add the xplane dataref
                        if(dataref != kf[3]):
                            dataref = kf[3]
                            # add only once as long as the dataref doesn't change
                            ob.xplane.datarefs.add()
                            dataref_index = len(ob.xplane.datarefs) -1
                            ob.xplane.datarefs[dataref_index].path = dataref

                        # set the dataref value
                        ob.xplane.datarefs[dataref_index].value = kf[2]
                        # add the xplane dataref keyframe
                        bpy.ops.object.add_xplane_dataref_keyframe(index=dataref_index)
                    except Exception as e:
                        print(self.getMessage('dataref'))
                        print(e)

                if(kf[0] == 'rot'):
                    # kf = ('rot',axis,value,angle,dataref)
                    # create the Blender keyframe
                    try:
                        axis = kf[1]
                        angle = kf[3]
                        # Euler rotation is in radians
                        angleRad = math.radians(angle)
                        # multiply the axis with the angle to get the euler rotation
                        # probably a cleaner way to do this
                        euler = ( (axis[0] * angleRad), (axis[1] * angleRad), (axis[2] * angleRad) )
                        ob.rotation_euler = mathutils.Euler(euler, 'XYZ')
                        ob.keyframe_insert(data_path='rotation_euler', frame=curFrame)
                        curFrame += 2

                        try:
                            # add the xplane dataref
                            if(dataref != kf[4]):
                                dataref = kf[4]
                                # add only once as long as the dataref doesn't change
                                ob.xplane.datarefs.add()
                                dataref_index = len(ob.xplane.datarefs) -1
                                ob.xplane.datarefs[dataref_index].path = dataref

                            # set the dataref value
                            ob.xplane.datarefs[dataref_index].value = kf[2]
                            # add the xplane dataref keyframe
                            bpy.ops.object.add_xplane_dataref_keyframe(index=dataref_index)
                        except Exception as e:
                            print(self.getMessage('dataref'))
                            print(e)

                    except Exception as e:
                        print(e)


                if(kf[0] == 'hide' or kf[0] == 'show'):
                    # kf = ('show', v1, v2, dataref)
                    try:
                        dataref = kf[3]
                        ob.xplane.datarefs.add()
                        dataref_index = len(ob.xplane.datarefs) -1
                        ob.xplane.datarefs[dataref_index].path = dataref
                        ob.xplane.datarefs[dataref_index].anim_type = kf[0]            
                        # set two dataref values
                        ob.xplane.datarefs[dataref_index].show_hide_v1 = kf[1]
                        ob.xplane.datarefs[dataref_index].show_hide_v2 = kf[2]
                    except Exception as e:
                        print(self.getMessage('dataref'))
                        print(e)

                # end kf loop

        bpy.context.scene.frame_set(1)
        return 1

    def createArmature(self, name, origin):
        #Create armature and armature object
        arm = bpy.data.armatures.new( name + 'Arm')
        arm.display_type = 'STICK'
        ob = bpy.data.objects.new( name , arm)
        # armature bone should be located at the rotation origin
        ob.location =  origin
        #Link armature object to our collection
        collection.objects.link(ob)

        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        #Make a bone - locate it at the rotation origin
        bone = ob.data.edit_bones.new('Bone')
        bone.head = (0,0,0)
        bone.tail = (0,0.2,0)

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.object.pose.bones["Bone"].rotation_mode = 'XYZ'

        return ob
    
    def createMesh(self, name, origin, verts, faces, mat, uvs, normals, attr):
        # Create mesh and object
        me = bpy.data.meshes.new(name+'Mesh')
        ob = bpy.data.objects.new(name, me)
        #ob.location = Vector((0,0,0))
        ob.location = origin
        ob.show_name = False
        
        # Link object to collection and make active
        collection.objects.link(ob)
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob

        # Apply shade smooth
        bpy.ops.object.shade_smooth()    

        # Create mesh from given verts, faces.
        me.from_pydata(verts, [], faces)

        # Assign the normals for each vertex
        vindex = 0
        for vertex in me.vertices:
            vertex.normal = normals[vindex]
            vindex += 1

        # Update mesh with new data
        me.calc_normals()
        me.update(calc_edges=True)

        # Create uv layer
        uvlayer = me.uv_layers.new()
        me.uv_layers.active = uvlayer

        # Assign the UV coordinates to each vertex
        for face in me.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uvlayer.data[loop_idx].uv = uvs[vert_idx]

        if mat:
            # Assign material to object
            ob.data.materials.append(mat)

        for attribute in attr:
            # add custom attributes
            # this is the raw string from the parser
            try:
                bpy.ops.object.add_xplane_object_attribute()
                ob.xplane.customAttributes[-1].name = attribute[0]
                ob.xplane.customAttributes[-1].value = ' '.join(attribute[1:])
            except Exception as e:
                print(e)

        # cleanup loose vertexes that don't belong in this object
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_loose()
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception as e:
            print(ob.name)
            print(e)

        return ob

    def getOrigin(self, keyframes):
        # if the animation contains rotation, the origin may be different
        origin = Vector((0,0,0))
        tempOrigin = Vector((0,0,0))
        for kf in keyframes:
            if(len(kf)):
                if(kf[0] == 'loc'):
                    # save the first translation position
                    tempOrigin = kf[1]
                if(kf[0] == 'rot'):
                    # if rotation follows translation, save we'll use that as the origin
                    origin = tempOrigin
                    break;
        return origin

    def transformMeshOrigin(self, ob, origin):
        # used to move the mesh origin
        ob.data.transform(mathutils.Matrix.Translation(-origin))
        return

    def translateObject(self, ob, location):
        ob.matrix_world.translation += location
        return

    def addChild(self, objParent, obj,):
        try:
            obj.parent = objParent
            return objParent
        except Exception as e:
            print('failed to parent object: ')
            print(objParent)
            print(e)

        return ()


    def createBlenderObject(self, obj):
        # obj = {label', 'orig',  'verts', 'faces', 'mat', 'uv', 'nrm', 'attr'}

        # create the mesh
        meshObj = self.createMesh(obj['label'], obj['orig'], obj['verts'], obj['faces'], obj['mat'], obj['uv'], obj['nrm'], obj['attr'])      

        return meshObj

    # parse file
    def run(self, origo):
        f = open(self.filepath, 'r')
        lines = f.readlines()
        f.close()
        
        verts = []
        faces = []
        normals = []
        uv = []
        attributes = []
        material = 0
        animID = -1
        armLabel = ''
        parentLabels = []
        animStack = []
        keyframes = []
        trans1 = Vector( ( 0, 0, 0 ) )
        trans2 = Vector( ( 0, 0, 0 ) )
        tempKeyframe = ()
        obLabel = ''
        objID = 0
        objects = []
        armatures = []
        for lineStr in lines:
            line = lineStr.split()
            if (len(line) == 0):
                continue


            if(line[0] == 'TEXTURE'):
                texfilename = line[1]
                # Create texture
                tex = bpy.data.textures.new('Texture', type = 'IMAGE')
                try:
                    tex.image = bpy.data.images.load("%s\\%s" % (os.path.dirname(self.filepath), texfilename))
                except:
                    # Try to load the image as .dds
                    try:
                        base = os.path.splitext(texfilename)[0]
                        tex.image = bpy.data.images.load("%s\\%s" % (os.path.dirname(self.filepath), base + '.dds'))
                    except:
                        print('Cannot find image file: ' + texfilename)

                tex.use_alpha = True

                # Create and add a material
                material = bpy.data.materials.new('Material')
                # Add Texture to the Material via shader nodes
                material.use_nodes = True

                bsdf = material.node_tree.nodes["Principled BSDF"]
                texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
                texImage.image = tex.image
                material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
                continue

            if(line[0] == '#'):
                # if you export with debug mode, labels will be added for each object
                # we can then name the imported objects better
                # save as debug label
                newLabel = '_'.join(line[1:])
                if(obLabel != newLabel):
                    obLabel = newLabel

                continue


            if(line[0] == 'VT'):
                # get verts from line
                vx = float(line[1])
                vy = (float(line[3]) * -1)
                vz = float(line[2])
                verts.append((vx, vy, vz))

                #get normals from line
                vnx = float(line[4])
                vny = float(line[6]) * -1
                vnz = float(line[5])
                normals.append((vnx, vny, vnz))

                #get UV coords from line
                uvx = float(line[7])
                uvy = float(line[8])
                uv.append((uvx, uvy))

                continue
            
            if(line[0] == 'IDX10' or line[0] == 'IDX'):
                faces.extend(map(int, line[1:]))
                continue

            if(line[0].startswith('ATTR_')):
                # found a custom attribute
                attributes.append(line)

            if(line[0] == 'ANIM_begin'):
                if(len(animStack)):
                    # a new nested block started
                    # add all the current keyframes to this stack
                    animStack[-1]['kf'] = keyframes

                # create a new block with unique ID
                animID +=1
                # add a block to the stack
                armLabel = obLabel if obLabel != '' else 'ARM%d' % animID
                animStack.append({'label': armLabel, 'kf': [], 'meshes': []})
                # and track keyframes for this block
                keyframes = []

                continue
                
            if(line[0] == 'ANIM_trans'):
                trans_x = float(line[1])
                trans_y = (float(line[3]) * -1)
                trans_z = float(line[2])
                trans_x2 = float(line[4])
                trans_y2 = (float(line[6]) * -1)
                trans_z2 = float(line[5])
                trans1 = Vector( (trans_x, trans_y, trans_z) )
                trans2 = Vector( (trans_x2, trans_y2, trans_z2) )              

                if(len(line) == 10):
                    # has a dataref
                    dataref = line[9]
                    param1 = float(line[7])
                    param2 = float(line[8])
                    # add two keyframes
                    keyframes.append( ('loc', trans1, param1, dataref) )
                    keyframes.append( ('loc', trans2, param2, dataref) )
                continue

            if(line[0] == 'ANIM_trans_begin'):
                dataref = line[1]
                # start a new keyframe tuple, we will read the position and value later
                tempKeyframe = ('loc',0,0,dataref)
                continue

            if(line[0] == 'ANIM_trans_key'):
                # ANIM_trans_key <value> <x> <y> <z>
                vec = Vector( (float(line[2]), (float(line[4]) * -1), float(line[3])) )
                tempKeyframe = ( tempKeyframe[0], vec, float(line[1]), tempKeyframe[3])
                keyframes.append( tempKeyframe )
                continue

            if(line[0] == 'ANIM_rotate'):
                # ANIM_rotate <x> <y> <z> <r1> <r2> <v1> <v2> [dataref]
                # we'll always use XYZ Euler as the rotation mode as this seems to be the Blender default
                if(len(line) == 9):
                    # has a dataref
                    dataref = line[8]
                    # axis gets mapped as XZY because that will be Blenders XYZ
                    axis = (float(line[1]), float(line[3]), float(line[2]))
                    r1 = float(line[4])
                    r2 = float(line[5])
                    v1 = float(line[6])
                    v2 = float(line[7])                        
                    # add two keyframes
                    keyframes.append( ('rot', axis, v1, r1, dataref) )
                    keyframes.append( ('rot', axis, v2, r2, dataref) )                 
                continue

            if(line[0] == 'ANIM_rotate_begin'):
                # ANIM_rotate_begin <x> <y> <z> <dataref>
                axis = (float(line[1]), (float(line[3]) * -1), float(line[2]))
                dataref = line[4]
                # create temp keyframe with some of the params
                tempKeyframe = ('rot',axis,0.0,0.0,dataref)
                continue

            if(line[0] == 'ANIM_rotate_key'):
                # ANIM_rotate_key <value> <angle>
                tempKeyframe = ( tempKeyframe[0], tempKeyframe[1], float(line[1]), float(line[2]), tempKeyframe[4])
                keyframes.append( tempKeyframe )            
                continue

            if(line[0] == 'ANIM_keyframe_loop'):
                # TODO: add loop property
                print('loop')

            if(line[0] == 'ANIM_hide'):
                # ANIM_hide <v1> <v2> <dataref>
                v1 = float(line[1])
                v2 = float(line[2])
                dataref = line[3]
                keyframes.append( ('hide', v1, v2, dataref) )
                continue

            if(line[0] == 'ANIM_show'):
                # ANIM_show <v1> <v2> <dataref>
                v1 = float(line[1])
                v2 = float(line[2])
                dataref = line[3]
                keyframes.append( ('show', v1, v2, dataref) )
                continue              
            
            if(line[0] == 'TRIS'):
                obj_origin = Vector( origo )
                tris_offset, tris_count = int(line[1]), int(line[2])
                face_lst = faces[tris_offset:tris_offset+tris_count]
                faceData = tuple( zip(*[iter(face_lst)]*3) )

                if(obLabel == ''):
                    obLabel = 'OBJ%d' % objID

                # make a dict of the mesh object
                meshObject = {'id': objID, 'label': obLabel, 'orig': obj_origin, 'verts': verts, 'faces': faceData, 'mat': material, 'uv': uv, 'nrm': normals, 'attr': attributes, 'kf': keyframes}

                if(len(animStack)):                   
                    # this is in an anim block, so add it to the last block in the stack
                    animStack[-1]['meshes'].append(meshObject)
                else:
                    # this is just a plain mesh, add it to the loose objects list
                    objects.append(meshObject)

                meshObject = {}

                obLabel = ''
                objID += 1
                tempKeyframe= ()
                attributes = []
                continue


            if(line[0] == 'ANIM_end'):
                if(len(animStack)):
                    # pop the last block and assign to an armature
                    anim = animStack.pop()
                    armKeyframes = anim['kf']
                    parent = ''
                    if(len(keyframes)):
                        # add any remaining animations from parent anim blocks
                        armKeyframes = armKeyframes + keyframes
                        if(len(animStack)):
                            # if there is previous anim on the stack, that is the parent
                            parent = animStack[-1]['label']
                            parentLabels.append(parent)

                    if(parent != '' or anim['label'] in parentLabels):
                        # requires an armature to handle nested animation
                        armatures.append({'label': anim['label'], 'kf': armKeyframes, 'parent': parent, 'meshes': anim['meshes']})
                    else:
                        # append to objects since this does not have a parent or child
                        objects = objects + anim['meshes']

                # clear some vars
                keyframes = []
                use_trans = False
                trans1 = Vector( ( 0, 0, 0 ) )
                trans2 = Vector( ( 0, 0, 0 ) )
                continue

            # loop end

        # loop through the armatures and create them in Blender
        # we will add keyframes to all the armatures
        for arm in armatures:
            # need to move the armature to the correct location based on rotations
            keyframes = arm['kf']
            rotOrigin = self.getOrigin(keyframes)
            # create the armature 
            BlenderArm = self.createArmature( arm['label'], rotOrigin)
            # apply the keyframes to the armature
            self.createKeyframes(keyframes, BlenderArm)

            # create meshes associated with this block
            for mesh in arm['meshes']:
                meshObj = self.createBlenderObject(mesh)
                # translate the mesh to match the armature origin
                self.transformMeshOrigin(meshObj, BlenderArm.location)
                # parent it to the armature
                self.addChild(BlenderArm, meshObj) 

        # return to frame 0
        bpy.context.scene.frame_set(0)


        # loop through the loose meshes and create the Blender meshes
        for index, obj in enumerate(objects):
            meshObj = self.createBlenderObject(obj)
            if(len(obj['kf'])):
                print(obj['label'])
                rotOrigin = self.getOrigin(obj['kf'])
                self.transformMeshOrigin(meshObj, rotOrigin)
                self.translateObject(meshObj, rotOrigin)
                # apply object animation keyframes
                self.createKeyframes(obj['kf'], meshObj)


        # create the parent/child relationships
        for arm in armatures:
            if(arm['parent'] != ''):
                try:
                    parentArm = bpy.context.view_layer.objects[arm['parent']]
                    childArm = bpy.context.view_layer.objects[arm['label']]
                    # reset the child position
                    childArm.location = childArm.location - parentArm.location
                    self.addChild(parentArm, childArm)
                except Exception as e:
                    print(e)     

        # end loop

        return len(objects) + len(armatures)
        
def menu_func(self, context):
    self.layout.operator(xplane11import.bl_idname, text="XPlane 11 Object (.obj)")
    
def register():
    bpy.utils.register_class(xplane11import)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(xplane11import)   
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    
if __name__ == "__main__":
    register()
    #bpy.ops.object.xplane11import("INVOKE_DEFAULT")