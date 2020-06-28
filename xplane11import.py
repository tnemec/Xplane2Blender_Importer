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


# imports X-Plane 11 obj format into Blender 2.8+
# Currently, this can import the model geometry and textures
# TODO: import ANIM and datarefs

# Orginal script: https://github.com/daveprue/XPlane2Blender

# rotations expressed in Y -Z X


import bpy
import math
import mathutils
from mathutils import Vector, Euler
import itertools
import os

bl_info = {
    "name": "Import X-Plane OBJ",
    "author": "Tony Nemec - original script by David C. Prue",
    "version": (0,2,0),
    "blender": (2,80,0),
    "api": 36273,
    "location": "File > Import/Export > XPlane",
    "description": "Import X-Plane obj",
    "category": "Import-Export"
}

class xplane11import(bpy.types.Operator):
    bl_label = "Import X-Plane OBJ"
    bl_idname = "object.xplane11import"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    collection = 0


    def execute(self, context):
        global collection
        print("execute %s" % self.filepath)
        # create new collection to match filename
        collection = bpy.data.collections.new(self.filepath.split('\\')[-1].split('.')[0])
        bpy.context.scene.collection.children.link(collection)
        # do the import      
        self.run((0,0,0))
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def getMessage(self, messageType):
        if(messageType == 'dataref'):
            return 'Failed to create XPlane dataref. Make sure you have the XPlane2Blender plugin enabled.'
        return ''


    def createKeyframes(self, obKeyframes, ob):
        count = -1
        dataref = ''
        dataref_index = 0
        for kf in obKeyframes:           
            count+= 2
            bpy.context.scene.frame_set(count)
            if(kf[0] == 'loc'):
                # kf = ('loc', o_t, param1, dataref)
                # first create the Blender keyframe
                ob.location = kf[1]
                ob.keyframe_insert(data_path='location', frame=count)

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
                    ob.keyframe_insert(data_path='rotation_euler', frame=count)
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

        bpy.context.scene.frame_set(1)
        return 1
    
    def createMeshFromData(self, name, origin, rot_origin, verts, faces, mat, uvs, normals, obKeyframes):
        # Create mesh and object
        me = bpy.data.meshes.new(name+'Mesh')
        ob = bpy.data.objects.new(name, me)
        #ob.location = Vector((0,0,0))
        ob.location = origin
        ob.show_name = False
        # print(name)
        # print(origin)
        # print(rot_origin)
        
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

        if(rot_origin != origin):
            # this moves the mesh to align the rotation axis
            ob.data.transform(mathutils.Matrix.Translation(-rot_origin))
            ob.matrix_world.translation += rot_origin


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

      
        if(len(obKeyframes)):
            #print(obKeyframes)
            self.createKeyframes(obKeyframes, ob)

        # cleanup loose vertexes
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        return ob
        

    def run(self, origo):
        # parse file
        f = open(self.filepath, 'r')
        lines = f.readlines()
        f.close()
        
        verts = []
        faces = []
        normals = []
        uv = []
        material = 0
        removed_faces_regions = []
        origin_temp = Vector( ( 0, 0, 0 ) )
        rot_origin = Vector( ( 0, 0, 0 ) )
        anim_nesting = 0
        a_trans = [origin_temp]
        trans_available = False
        trans1 = Vector( ( 0, 0, 0 ) )
        trans2 = Vector( ( 0, 0, 0 ) )
        obKeyframes = []
        tempKeyframe = ()
        debugLabel = ''
        objects = []
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

            if(line[0] == '#'):
                # if you export with debug mode, labels will be added for each object
                # we can then name the imported objects better
                # save as debug label
                newLabel = '_'.join(line[1:])
                if(debugLabel != newLabel):
                    debugLabel = newLabel


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
            
            if(line[0] == 'IDX10' or line[0] == 'IDX'):
                faces.extend(map(int, line[1:]))
                
            if(line[0] == 'ANIM_begin'):
                anim_nesting += 1
                # if nested more than one deep, we should make an armature instead of an object
                
            if(line[0] == 'ANIM_trans'):
                trans_x = float(line[1])
                trans_y = (float(line[3]) * -1)
                trans_z = float(line[2])
                trans_x2 = float(line[4])
                trans_y2 = (float(line[6]) * -1)
                trans_z2 = float(line[5])
                trans1 = Vector( (trans_x, trans_y, trans_z) )
                trans2 = Vector( (trans_x2, trans_y2, trans_z2) )              
                origin_temp = trans1 + a_trans[-1]
                a_trans.append(trans1) 
                trans_available = True

                if(len(line) == 10):
                    # has a dataref
                    dataref = line[9]
                    if(dataref != 'none'):
                        # ignore 'none'
                        param1 = float(line[7])
                        param2 = float(line[8])
                        # add two keyframes
                        obKeyframes.append( ('loc', trans1, param1, dataref) )
                        obKeyframes.append( ('loc', trans2, param2, dataref) )

            if(line[0] == 'ANIM_trans_begin'):
                dataref = line[1]
                # start a new keyframe tuple, we will read the position and value later
                tempKeyframe = ('loc',0,0,dataref)

            if(line[0] == 'ANIM_trans_key'):
                # ANIM_trans_key <value> <x> <y> <z>
                vec = Vector( (float(line[2]), (float(line[4]) * -1), float(line[3])) )
                tempKeyframe = ( tempKeyframe[0], vec, float(line[1]), tempKeyframe[3])
                obKeyframes.append( tempKeyframe )

            if(line[0] == 'ANIM_rotate'):
                # ANIM_rotate <x> <y> <z> <r1> <r2> <v1> <v2> [dataref]
                # we'll always use XYZ Euler as the rotation mode as this seems to be the Blender default
                if(origin_temp != origo):
                    # for objects with ANIM_trans before rotation, we need to store as the rotation origin
                    rot_origin = origin_temp

                if(len(line) == 9):
                    # has a dataref
                    dataref = line[8]
                    if(dataref != 'none'):
                        # ignore 'none'
                        # axis gets mapped as XZY because that will be Blenders XYZ
                        axis = (float(line[1]), float(line[3]), float(line[2]))
                        r1 = float(line[4])
                        r2 = float(line[5])
                        v1 = float(line[6])
                        v2 = float(line[7])                        
                        # add two keyframes
                        obKeyframes.append( ('rot', axis, v1, r1, dataref) )
                        obKeyframes.append( ('rot', axis, v2, r2, dataref) )

            if(line[0] == 'ANIM_rotate_begin'):
                # ANIM_rotate_begin <x> <y> <z> <dataref>

                if(origin_temp != origo):
                    # for objects with ANIM_trans before rotation, we need to store as the rotation origin
                    rot_origin = origin_temp

                axis = (float(line[1]), (float(line[3]) * -1), float(line[2]))
                dataref = line[4]
                # create temp keyframe with some of the params
                tempKeyframe = ('rot',axis,0.0,0.0,dataref)

            if(line[0] == 'ANIM_rotate_key'):
                # ANIM_rotate_key <value> <angle>
                tempKeyframe = ( tempKeyframe[0], tempKeyframe[1], float(line[1]), float(line[2]), tempKeyframe[4])
                obKeyframes.append( tempKeyframe )

            if(line[0] == 'ANIM_hide'):
                # ANIM_hide <v1> <v2> <dataref>
                v1 = float(line[1])
                v2 = float(line[2])
                dataref = line[3]
                obKeyframes.append( ('hide', v1, v2, dataref) )

            if(line[0] == 'ANIM_show'):
                # ANIM_show <v1> <v2> <dataref>
                v1 = float(line[1])
                v2 = float(line[2])
                dataref = line[3]
                obKeyframes.append( ('show', v1, v2, dataref) )                
            
            if(line[0] == 'ANIM_end'):
                anim_nesting -= 1
                # clear some vars
                use_trans = False
                trans1 = Vector( ( 0, 0, 0 ) )
                trans2 = Vector( ( 0, 0, 0 ) )
                if(anim_nesting == 0):
                    trans_available = False
                    a_trans = [Vector((0,0,0))]
                else:
                    if(len(a_trans)):
                        temp = a_trans.pop()  
                
            if(line[0] == 'TRIS'):
                obj_origin = Vector( origo )
                tris_offset, tris_count = int(line[1]), int(line[2])
                obj_lst = faces[tris_offset:tris_offset+tris_count]
                if(trans_available):
                    obj_origin = origin_temp
                    # TODO: rot_origin still not correct for nested objects
                objects.append( (debugLabel, obj_origin, rot_origin, obj_lst, obKeyframes) )
                debugLabel = ''
                obKeyframes = []
                tempKeyframe= ()
                rot_origin = Vector((0,0,0))
        
        counter = 0
        for label, orig, rot_orig, obj, kf in objects:
            obj_tmp = tuple( zip(*[iter(obj)]*3) )
            obName = label if (label != '') else 'OBJ%d' % counter
            self.createMeshFromData(obName, orig, rot_orig, verts, obj_tmp, material, uv, normals, kf)
            counter+=1
    
        return
        
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