'''

  V-Ray/Blender 2.5

  http://vray.cgdo.ru

  Time-stamp: " "

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy

''' vb modules '''
from vb25.utils import *
from vb25.ui.ui import *


import properties_data_camera
properties_data_camera.DATA_PT_context_camera.COMPAT_ENGINES.add('VRAY_RENDER')
properties_data_camera.DATA_PT_context_camera.COMPAT_ENGINES.add('VRAY_RENDER_PREVIEW')
properties_data_camera.DATA_PT_camera_display.COMPAT_ENGINES.add('VRAY_RENDER')
properties_data_camera.DATA_PT_camera_display.COMPAT_ENGINES.add('VRAY_RENDER_PREVIEW')
del properties_data_camera


class VRAY_DP_camera(VRayDataPanel, bpy.types.Panel):
	bl_label = "Parameters"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return (context.camera and engine_poll(__class__, context))

	def draw(self, context):
		layout= self.layout

		ca= context.camera

		VRayCamera= ca.vray
		SettingsCamera= VRayCamera.SettingsCamera
		SettingsCameraDof= VRayCamera.SettingsCameraDof
		SettingsMotionBlur= VRayCamera.SettingsMotionBlur

		wide_ui= context.region.width > narrowui

		if wide_ui:
			layout.prop(ca, 'type', expand=True)
		else:
			layout.prop(ca, 'type', text="")
		layout.separator()

		split= layout.split()
		col= split.column()
		if ca.type == 'PERSP':
			col.prop(VRayCamera, 'override_fov')
			if wide_ui:
				col= split.column()
			if VRayCamera.override_fov: col.prop(VRayCamera, 'fov')
				
			split= layout.split()
			split.active= not VRayCamera.override_fov
			col= split.column()
			if ca.lens_unit == 'MILLIMETERS':
				col.prop(ca, 'lens', text="Angle")
			elif ca.lens_unit == 'DEGREES':
				col.prop(ca, 'angle')
			if wide_ui:
				col= split.column()
			col.prop(ca, 'lens_unit', text="")

		layout.separator()

		if ca.type == 'ORTHO':
			col.prop(ca, 'ortho_scale')
		else:
			split= layout.split()
			col= split.column()
			col.label(text="Type:")
			col= split.column()
			col.prop(SettingsCamera, 'type', text="")

			layout.separator()

		'''
			SettingsCamera
		'''
		# SMTH

		'''
			SettingsCameraDof
		'''
		# split= layout.split()
		# col= split.column()
		# col= split.column()

		'''
			SettingsMotionBlur
		'''
		# split= layout.split()
		# col= split.column()
		# col= split.column()

		split= layout.split()
		col = split.column(align=True)
		col.label(text="Clipping:")
		col.prop(ca, 'clip_start', text="Start")
		col.prop(ca, 'clip_end', text="End")
		if wide_ui:
			col= split.column()
		col.label(text="Depth of Field:")
		col.prop(ca, 'dof_object', text="")
		col.prop(ca, 'dof_distance', text="Distance")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'use_camera_loop')


class VRAY_DP_physical_camera(VRayDataPanel, bpy.types.Panel):
	bl_label   = "Physical"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return (context.camera and engine_poll(__class__, context))

	def draw_header(self, context):
		ca= context.camera
		VRayCamera= ca.vray
		CameraPhysical= VRayCamera.CameraPhysical
		self.layout.prop(CameraPhysical, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ca= context.camera
		VRayCamera= ca.vray
		CameraPhysical= VRayCamera.CameraPhysical

		layout= self.layout
		layout.active= CameraPhysical.use

		split= layout.split()
		col= split.column()
		col.prop(CameraPhysical, 'type', text="Type")

		split= layout.split()
		col= split.column()
		col.label(text="Parameters:")

		split= layout.split()
		col= split.column()
		sub= col.column(align=True)
		sub.prop(CameraPhysical, 'specify_fov', text="Use FOV")
		if not CameraPhysical.specify_fov:
			sub.prop(CameraPhysical, 'film_width')
			sub.prop(CameraPhysical, 'focal_length')
			sub.prop(CameraPhysical, 'zoom_factor')

		sub= col.column(align=True)
		sub.prop(CameraPhysical, 'distortion')
		if not CameraPhysical.guess_lens_shift:
			sub.prop(CameraPhysical, 'lens_shift')
			sub.operator('vray.lens_shift')
		sub.prop(CameraPhysical, 'guess_lens_shift')
		
		if wide_ui:
			col= split.column(align=True)

		col.prop(CameraPhysical, 'exposure')
		if CameraPhysical.exposure:
			col.prop(CameraPhysical, 'f_number')
			col.prop(CameraPhysical, 'shutter_speed')
			if CameraPhysical.type == 'CINEMATIC':
				col.prop(CameraPhysical, 'shutter_angle')
				col.prop(CameraPhysical, 'shutter_offset')
			elif CameraPhysical.type == 'VIDEO':
				col.prop(CameraPhysical, 'latency')
			col.prop(CameraPhysical, 'ISO')

		split= layout.split()
		col= split.column()
		col.label(text="White balance:")
		sub= col.row(align= True)
		sub.prop(CameraPhysical, 'white_balance', text="")
		sub.operator('vray.set_kelvin_color', text="", icon= 'COLOR', emboss= False).data_path= "object.data.vray.CameraPhysical.white_balance"

		if wide_ui:
			col= split.column()

		col.prop(CameraPhysical, 'vignetting')

		split= layout.split()
		colL= split.column()
		colL.label(text="Sampling:")

		split= layout.split()
		colL= split.column()
		colR= split.column(align=True)

		colL.prop(CameraPhysical, 'use_dof')
		colL.prop(CameraPhysical, 'use_moblur')

		if CameraPhysical.use_dof:
			colR.prop(CameraPhysical, 'blades_enable')

		if CameraPhysical.use_moblur or CameraPhysical.use_dof:
			colL.prop(CameraPhysical, 'subdivs')

			if CameraPhysical.use_dof and CameraPhysical.blades_enable:
				colR.prop(CameraPhysical, 'blades_num')
				colR.prop(CameraPhysical, 'blades_rotation')
				colR.prop(CameraPhysical, 'center_bias')
				colR.prop(CameraPhysical, 'anisotropy')


class VRAY_DP_hide_from_view(VRayDataPanel, bpy.types.Panel):
	bl_label   = "Hide objects"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return (context.camera and engine_poll(__class__, context))

	def draw_header(self, context):
		ca= context.camera
		VRayCamera= ca.vray
		self.layout.prop(VRayCamera, 'hide_from_view', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ca= context.camera
		VRayCamera= ca.vray

		layout= self.layout
		layout.active= VRayCamera.hide_from_view

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_all', text="Completely")
		if VRayCamera.hf_all:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_all_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_all_auto
			sub.prop_search(VRayCamera, 'hf_all_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_all_groups',   bpy.data,      'groups')

			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_camera', text="From camera")
		if VRayCamera.hf_camera:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_camera_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_camera_auto
			sub.prop_search(VRayCamera, 'hf_camera_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_camera_groups',   bpy.data,      'groups')

			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_gi', text="From GI")
		if VRayCamera.hf_gi:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_gi_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_gi_auto
			sub.prop_search(VRayCamera, 'hf_gi_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_gi_groups',   bpy.data,      'groups')

			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_reflect', text="From reflections")
		if VRayCamera.hf_reflect:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_reflect_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_reflect_auto
			sub.prop_search(VRayCamera, 'hf_reflect_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_reflect_groups',   bpy.data,      'groups')

			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_refract', text="From refractions")
		if VRayCamera.hf_refract:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_refract_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_refract_auto
			sub.prop_search(VRayCamera, 'hf_refract_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_refract_groups',   bpy.data,      'groups')

			layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VRayCamera, 'hf_shadows', text="From shadows")
		if VRayCamera.hf_shadows:
			split= layout.split(percentage=0.2)
			col= split.column()
			col.prop(VRayCamera, 'hf_shadows_auto', text="Auto")
			sub= split.column()
			sub.active= not VRayCamera.hf_shadows_auto
			sub.prop_search(VRayCamera, 'hf_shadows_objects',  context.scene, 'objects')
			sub.prop_search(VRayCamera, 'hf_shadows_groups',   bpy.data,      'groups')
