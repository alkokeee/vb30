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


TYPE = 'TEXTURE'
ID   = 'TexRemapFloat'
NAME = 'Remap Float'
DESC = "Remap float value"

PluginParams = (
    {
        'attr' : 'value',
        'desc' : "Value to remap",
        'type' : 'FLOAT_TEXTURE',
        'default' : 0,
    },
    {
        'attr' : 'low',
        'desc' : "Low boundary",
        'type' : 'FLOAT',
        'default' : 0,
    },
    {
        'attr' : 'high',
        'desc' : "High boundary",
        'type' : 'FLOAT',
        'default' : 1,
    },
)

PluginWidget = """
{ "widgets": [
    {   "layout" : "ROW",
        "align" : true,
        "attrs" : [
            { "name" : "low" },
            { "name" : "high" }
        ]
    }
]}
"""

def nodeDraw(context, layout, TexRemapFloat):
    split = layout.split()
    col = split.column(align=True)
    col.prop(TexRemapFloat, 'low')
    col.prop(TexRemapFloat, 'high')
