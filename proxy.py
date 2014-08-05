#
# V-Ray For Blender
#
# http://chaosgroup.com
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

import math
import os
import subprocess
import sys
import tempfile
import time

import bpy
import bmesh

import _vray_for_blender

from vb30.lib import BlenderUtils, PathUtils, LibUtils, SysUtils
from vb30.lib import VRayStream

from vb30.nodes import tools as NodesTools

from vb30.vray_tools import VRayProxy
from vb30 import debug


def LaunchPly2Vrmesh(vrsceneFilepath, vrmeshFilepath, nodeName, frames=None, applyTm=False, useVelocity=False):
    ply2vrmeshBin  = "ply2vrmesh{arch}{ext}"
    ply2vrmeshArch = ""

    if sys.platform == 'win32':
        ply2vrmeshExt = ".exe"
        ply2vrmeshArch = "_%s" % SysUtils.GetArch()
    elif sys.platform == 'linux':
        ply2vrmeshExt = ".bin"
    else:
        ply2vrmeshExt = ".mach"

    ply2vrmeshBin = ply2vrmeshBin.format(arch=ply2vrmeshArch, ext=ply2vrmeshExt)

    exporterPath = SysUtils.GetExporterPath()
    if not exporterPath:
        return "Exporter path is not found!"

    ply2vrmesh = os.path.join(exporterPath, "bin", ply2vrmeshBin)
    if not os.path.exists(ply2vrmesh):
        return "ply2vrmesh binary not found!"

    cmd = [ply2vrmesh]
    cmd.append(vrsceneFilepath)
    cmd.append('-vrsceneNodeName')
    cmd.append(nodeName)
    if useVelocity:
        cmd.append('-vrsceneVelocity')
    if applyTm:
        cmd.append('-vrsceneApplyTm')
    if frames is not None:
        cmd.append('-vrsceneFrames')
        cmd.append('%i-%i' % (frames[0], frames[1]))
    cmd.append(vrmeshFilepath)

    debug.PrintInfo("Calling: %s" % " ".join(cmd))

    err = subprocess.call(cmd)
    if err:
        return "Error generating vrmesh file!"

    return None


def ExportMeshSample(o, ob):
    nodeName = BlenderUtils.GetObjectName(ob)
    geomName = BlenderUtils.GetObjectName(ob, prefix='ME')

    o.set('OBJECT', 'Node', nodeName)
    o.writeHeader()
    o.writeAttibute('geometry', geomName)
    o.writeAttibute('transform', ob.matrix_world)
    o.writeFooter()

    _vray_for_blender.exportMesh(
        bpy.context.as_pointer(),   # Context
        ob.as_pointer(),            # Object
        geomName,                   # Result plugin name
        None,                       # propGroup
        o.output                    # Output file
    )

    return nodeName


def LoadProxyPreviewMesh(ob, filepath, anim_type, anim_offset, anim_speed, anim_frame):
    meshFile = VRayProxy.MeshFile(filepath)

    result = meshFile.readFile()
    if result is not None:
        return "Error parsing VRayProxy file!"

    meshData = meshFile.getPreviewMesh(
        anim_type,
        anim_offset,
        anim_speed,
        anim_frame
    )

    if meshData is None:
        return "Can't find preview voxel!"

    mesh = bpy.data.meshes.new("VRayProxyPreview")
    mesh.from_pydata(meshData['vertices'], [], meshData['faces'])
    mesh.update()

    # Replace object mesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.to_mesh(ob.data)
    ob.data.update()

    if meshData['uv_sets']:
        for uvName in meshData['uv_sets']:
            bpy.ops.mesh.uv_texture_add()

            index = ob.data.uv_layers.active_index
            uvLayer = ob.data.uv_layers[index]
            uvLayer.name = uvName

    # Remove temp
    bm.free()
    bpy.data.meshes.remove(mesh)


def CreateProxyNodetree(ob, proxyFilepath):
    VRayObject = ob.vray
    if VRayObject.ntree:
        return "Node tree already exists!"

    nt = bpy.data.node_groups.new(ob.name, type='VRayNodeTreeObject')
    nt.use_fake_user = True

    outputNode = nt.nodes.new('VRayNodeObjectOutput')

    proxyGeometry   = nt.nodes.new('VRayNodeGeomMeshFile')
    blenderMaterial = nt.nodes.new('VRayNodeBlenderOutputMaterial')

    blenderMaterial.location.x = outputNode.location.x - 200
    blenderMaterial.location.y = outputNode.location.y + 30

    proxyGeometry.location.x = outputNode.location.x - 200
    proxyGeometry.location.y = outputNode.location.y - 150

    nt.links.new(blenderMaterial.outputs['Material'], outputNode.inputs['Material'])
    nt.links.new(proxyGeometry.outputs['Geometry'],   outputNode.inputs['Geometry'])

    NodesTools.deselectNodes(nt)

    proxyGeometry.GeomMeshFile.file = proxyFilepath

    VRayObject.ntree = nt


 #######  ########   ##        ########  ########  ######## ##     ## #### ######## ##      ##
##     ## ##     ## ####       ##     ## ##     ## ##       ##     ##  ##  ##       ##  ##  ##
##     ## ##     ##  ##        ##     ## ##     ## ##       ##     ##  ##  ##       ##  ##  ##
##     ## ########             ########  ########  ######   ##     ##  ##  ######   ##  ##  ##
##     ## ##         ##        ##        ##   ##   ##        ##   ##   ##  ##       ##  ##  ##
##     ## ##        ####       ##        ##    ##  ##         ## ##    ##  ##       ##  ##  ##
 #######  ##         ##        ##        ##     ## ########    ###    #### ########  ###  ###

class VRAY_OT_proxy_load_preview(bpy.types.Operator):
    bl_idname      = "vray.proxy_load_preview"
    bl_label       = "Load Preview"
    bl_description = "Loads mesh preview from vrmesh file"

    def execute(self, context):
        GeomMeshFile  = context.node.GeomMeshFile
        proxyFilepath = bpy.path.abspath(GeomMeshFile.file)

        if not proxyFilepath:
            self.report({'ERROR'}, "Proxy filepath is not set!")
            return {'FINISHED'}

        if not os.path.exists(proxyFilepath):
            return {'FINISHED'}

        err = LoadProxyPreviewMesh(
            context.object,
            proxyFilepath,
            GeomMeshFile.anim_type,
            GeomMeshFile.anim_offset,
            GeomMeshFile.anim_speed,
            context.scene.frame_current-1
        )

        if err is not None:
            self.report({'ERROR'}, err)
            return {'CANCELLED'}

        return {'FINISHED'}


 #######  ########   ##         ######  ########  ########    ###    ######## ########
##     ## ##     ## ####       ##    ## ##     ## ##         ## ##      ##    ##
##     ## ##     ##  ##        ##       ##     ## ##        ##   ##     ##    ##
##     ## ########             ##       ########  ######   ##     ##    ##    ######
##     ## ##         ##        ##       ##   ##   ##       #########    ##    ##
##     ## ##        ####       ##    ## ##    ##  ##       ##     ##    ##    ##
 #######  ##         ##         ######  ##     ## ######## ##     ##    ##    ########

class VRAY_OT_create_proxy(bpy.types.Operator):
    bl_idname      = "vray.create_proxy"
    bl_label       = "Create proxy"
    bl_description = "Creates proxy from selection"

    def execute(self, context):
        sce = context.scene

        # Use current active object UI for initial settings
        ob        = bpy.context.object
        selection = bpy.context.selected_objects
        oneObject = len(selection)

        GeomMeshFile = ob.data.vray.GeomMeshFile

        # Create output path
        outputDirpath = BlenderUtils.GetFullFilepath(GeomMeshFile.dirpath)
        outputDirpath = PathUtils.CreateDirectory(outputDirpath)

        # Create tmp export file
        vrsceneFilepath = os.path.join(tempfile.gettempdir(), "vrmesh.vrscene")
        vrsceneFile = open(vrsceneFilepath, 'w')

        # Settings
        frames = None
        frameStart = 1
        frameStep  = 1
        if GeomMeshFile.animation not in {'NONE'}:
            if GeomMeshFile.animation == 'MANUAL':
                frameStart = GeomMeshFile.frame_start
                frames = (frameStart, GeomMeshFile.frame_end, 1)
            else:
                frameStart = sce.frame_start
                frameStep  = sce.frame_step
                frames = (sce.frame_start, sce.frame_end, sce.frame_step)

        applyTm     = GeomMeshFile.apply_transforms
        useVelocity = GeomMeshFile.add_velocity

        # Export objects meshes and generate nodes name list
        obPluginNames = []
        o = VRayStream.VRaySimplePluginExporter(outputFile=vrsceneFile)

        exporter = _vray_for_blender.init(
            engine  = 0,
            context = bpy.context.as_pointer(),
            scene   = sce.as_pointer(),
            data    = bpy.data.as_pointer(),

            objectFile   = o.output,
            geometryFile = o.output,
            lightsFile   = o.output,
            materialFile = o.output,
            textureFile  = o.output,

            isAnimation = frames is not None,
            frameStart  = frameStart,
            frameStep   = frameStep,

            drSharePath = "",
        )

        _vray_for_blender.setFrame(frameStart)

        for ob in selection:
            if ob.type in BlenderUtils.NonGeometryTypes:
                continue
            nodeName = None
            if not frames:
                nodeName = ExportMeshSample(o, ob)
            else:
                sce = bpy.context.scene
                frame_current = sce.frame_current
                for f in range(frames[0], frames[1]+frames[2], frames[2]):
                    bpy.context.scene.frame_set(f)
                    _vray_for_blender.setFrame(f)
                    nodeName = ExportMeshSample(o, ob)
                    _vray_for_blender.clearCache()
                sce.frame_set(frame_current)
            obPluginNames.append([ob, nodeName])
        o.done()
        vrsceneFile.close()

        _vray_for_blender.clearFrames()
        _vray_for_blender.exit(exporter)

        # Launch the generator tool
        err = None
        for ob, nodeName in obPluginNames:
            vrmeshName = LibUtils.CleanString(ob.name)
            if oneObject and GeomMeshFile.filename:
                vrmeshName = GeomMeshFile.filename
            vrmeshName += ".vrmesh"
            vrmeshFilepath = os.path.join(outputDirpath, vrmeshName)

            err = LaunchPly2Vrmesh(vrsceneFilepath, vrmeshFilepath, nodeName, frames, applyTm, useVelocity)
            if err is not None:
                break

            if GeomMeshFile.proxy_attach_mode != 'NONE':
                attachOb = ob

                if GeomMeshFile.proxy_attach_mode == 'NEW':
                    newName = 'VRayProxy%s' % ob.name
                    newMesh = bpy.data.meshes.new(newName)
                    attachOb = bpy.data.objects.new(newName, newMesh)

                    context.scene.objects.link(attachOb)

                BlenderUtils.SelectObject(attachOb)

                if GeomMeshFile.proxy_attach_mode == 'NEW':
                    for slot in ob.material_slots:
                        if slot and slot.material:
                            attachOb.data.materials.append(slot.material)
                            attachOb.material_slots[-1].link     = 'OBJECT'
                            attachOb.material_slots[-1].material = slot.material

                if GeomMeshFile.apply_transforms:
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                else:
                    attachOb.matrix_world = ob.matrix_world

                CreateProxyNodetree(attachOb, vrmeshFilepath)

                if GeomMeshFile.proxy_attach_mode in {'NEW', 'REPLACE'}:
                    LoadProxyPreviewMesh(
                        attachOb,
                        vrmeshFilepath,
                        GeomMeshFile.anim_type,
                        GeomMeshFile.anim_offset,
                        GeomMeshFile.anim_speed,
                        context.scene.frame_current-1
                    )

        # Remove temp export file
        os.remove(vrsceneFilepath)

        if err:
            self.report({'ERROR'}, "Error generating VRayProxy! Check system console!")
            debug.PrintError(err)
            return {'CANCELLED'}

        self.report({'INFO'}, "Done creating proxy!")

        return {'FINISHED'}


########  ########  ######   ####  ######  ######## ########     ###    ######## ####  #######  ##    ##
##     ## ##       ##    ##   ##  ##    ##    ##    ##     ##   ## ##      ##     ##  ##     ## ###   ##
##     ## ##       ##         ##  ##          ##    ##     ##  ##   ##     ##     ##  ##     ## ####  ##
########  ######   ##   ####  ##   ######     ##    ########  ##     ##    ##     ##  ##     ## ## ## ##
##   ##   ##       ##    ##   ##        ##    ##    ##   ##   #########    ##     ##  ##     ## ##  ####
##    ##  ##       ##    ##   ##  ##    ##    ##    ##    ##  ##     ##    ##     ##  ##     ## ##   ###
##     ## ########  ######   ####  ######     ##    ##     ## ##     ##    ##    ####  #######  ##    ##

def GetRegClasses():
    return (
        VRAY_OT_proxy_load_preview,
        VRAY_OT_create_proxy,
    )


def register():
    for regClass in GetRegClasses():
        bpy.utils.register_class(regClass)


def unregister():
    for regClass in GetRegClasses():
        bpy.utils.unregister_class(regClass)
