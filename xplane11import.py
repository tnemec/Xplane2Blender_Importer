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

import bpy
import mathutils
from mathutils import Vector
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

    def execute(self, context):
        print("execute %s" % self.filepath)
        self.run((0,0,0))
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def createMeshFromData(self, name, origin, verts, faces, mat, uvs, normals):
        # Create mesh and object
        me = bpy.data.meshes.new(name+'Mesh')
        ob = bpy.data.objects.new(name, me)
        ob.location = origin
        ob.show_name = False
        
        # Link object to default collection and make active
        bpy.data.collections[0].objects.link(ob)
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        
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
        origin_temp = 0
        anim_nesting = 0 # How many levels of ANIM_begin/ANIM_end pairs there are
        trans_available = False;
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
                anim_nesting+=1
                
            # Now search for ANIM_trans and corresponding TRIS
            if(line[0] == 'ANIM_trans'):
                trans_x = float(line[1])
                trans_y = (float(line[3]) * -1)
                trans_z = float(line[2])
                origin_temp = Vector( (trans_x, trans_y, trans_z) )
                trans_available = True
            
            if(line[0] == 'ANIM_end'):
                anim_nesting-=1
                if(anim_nesting == 0): #lets reset the animation states as we left the anim definition
                    trans_available = False
                
            if(line[0] == 'TRIS'):
                obj_origin = Vector( origo )
                tris_offset, tris_count = int(line[1]), int(line[2])
                obj_lst = faces[tris_offset:tris_offset+tris_count]
                removed_faces_regions.append( (tris_offset, tris_offset+tris_count) )
                if(trans_available):
                    obj_origin = origin_temp
                objects.append( (obj_origin, obj_lst) )
        
        offset = 0
        for start, end in removed_faces_regions:
            faces[start-offset:end-offset] = [] # we moved this part to another place, so remove here
            offset += (end - start)
            
        #now all the objects are on objects array, the leftover is in faces array
        if(len(faces) > 0):
            objects.insert(0, (Vector(origo), faces) )
        
        counter = 0
        for orig, obj in objects:
            obj_tmp = tuple( zip(*[iter(obj)]*3) )
            self.createMeshFromData('OBJ%d' % counter, orig, verts, obj_tmp, material, uv, normals)
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