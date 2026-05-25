#!/usr/bin/env python


"""
MODIFIED BY: H. Lazo 2012

Copyright (C) 2007-2012 Rob Antonishen; rob.antonishen@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import inkex, os, csv, math

"""
PATHS2GROUPS : To use when you vectorize a raster image with the multiple pass option. You get a group
with multiple paths with different fill attributes. Then you can convert the groups to layers with the extension
group2layer
"""

class paths2groups(inkex.Effect):
   def __init__(self):
      inkex.Effect.__init__(self)

   def effect(self):
      # THE SELECTED GROUP
      # sltd=self.selected
      
      for elem in self.selected.itervalues():
         # Only to check that there is only 1 group
         inkex.errormsg(str(self.selected))
         father=self.getParentNode(elem)
         children=elem.getchildren()
         if  children != None:
            for node in children:
               if node.tag == inkex.addNS('path','svg'):
                  
                  #print(node.get("id"))
                  #group =inkex.etree.SubElement(root, inkex.addNS('g','svg'))
                  group =inkex.etree.SubElement(elem, inkex.addNS('g','svg') )
                  group.set("id", "lyr_"+node.get("id")[4:])
                  group.append(node)
                  
                  if group.tag == inkex.addNS('g','svg'):
                     group.set(inkex.addNS("label","inkscape"), group.get(inkex.addNS("id")))
                     group.set(inkex.addNS("groupmode","inkscape"), "layer")
                     father.append(group)
         father.remove(elem)

if __name__ == '__main__':
    e = paths2groups()
    e.affect()


# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
