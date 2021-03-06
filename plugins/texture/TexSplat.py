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

import bpy

import TexCommonParams


TYPE = 'TEXTURE'
ID   = 'TexSplat'
NAME = 'Splat'
DESC = ""

PluginParams = list(TexCommonParams.PluginParams)

PluginParams.extend([
    {
        'attr' : 'use_3d_mapping',
        'desc' : "",
        'type' : 'BOOL',
        'default' : False,
    },

    {
        'attr' : 'color1',
        'desc' : "First color",
        'type' : 'TEXTURE',
        'default' : (1, 1, 1),
    },
    {
        'attr' : 'color2',
        'desc' : "Second color",
        'type' : 'TEXTURE',
        'default' : (0, 0, 0),
    },
    {
        'attr' : 'size',
        'desc' : "Size",
        'type' : 'FLOAT',
        'default' : 1,
    },
    {
        'attr' : 'iterations',
        'desc' : "Number of iterations for the fractal generator",
        'type' : 'INT',
        'default' : 4,
    },
    {
        'attr' : 'threshold',
        'desc' : "Threshold",
        'type' : 'FLOAT',
        'default' : 0.2,
    },
    {
        'attr' : 'smoothing',
        'desc' : "Transition smoothing",
        'type' : 'FLOAT',
        'default' : 0.02,
    },
])

PluginWidget = """
{ "widgets": [
    {   "layout" : "SPLIT",
        "splits" : [
            {   "layout" : "COLUMN",
                "align" : false,
                "attrs" : [
                    { "name" : "size" }
                ]
            },
            {   "layout" : "COLUMN",
                "align" : false,
                "attrs" : [
                    { "name" : "iterations" },
                    { "name" : "threshold" },
                    { "name" : "smoothing" }
                ]
            }
        ]
    },

    {   "layout" : "COLUMN",
        "attrs" : [
            { "name" : "use_3d_mapping" }
        ]
    },

    {TEX_COMMON}
]}
"""
PluginWidget = PluginWidget.replace('{TEX_COMMON}', TexCommonParams.PluginWidget)
