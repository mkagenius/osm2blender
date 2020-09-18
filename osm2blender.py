import bpy, bmesh

import random

import xml.dom.minidom

# replace filepath with the absolute path of the OSM file you have downloaded
doc = xml.dom.minidom.parse("/Users/manish/Work/osm2maya/indiranagar.osm")


# building:levels


all_ways = doc.getElementsByTagName("way")

buildings = []

for el in all_ways:
    for ch in el.childNodes:
    
        if ch.attributes:

            if 'k' in ch.attributes.keys() and 'building' ==  ch.attributes['k'].value:
                buildings.append(el)
    
                break


nodes = doc.getElementsByTagName("node")
id_to_tuple = {}
for node in nodes:
    id_val = node.attributes['id'].value
    if 'lon' in node.attributes.keys():
        (lon, lat) = (node.attributes['lon'].value, node.attributes['lat'].value)
        id_to_tuple[id_val] = (lon, lat)
        

all_buildings = []

for b in buildings:
    lst = []
    nds = b.getElementsByTagName('nd')
    for ch in nds:
        if ch.tagName == 'nd':
            node_id = ch.attributes['ref'].value
            lst.append(id_to_tuple[node_id])
    
    tags = b.getElementsByTagName('tag')
    level = 1
    for tag in tags:
        if tag.tagName == 'tag':
            if tag.attributes['k'].value == 'building:levels':
                try:
                    level = int(tag.attributes['v'].value)
                except:
                    level = 1
    
     
    
    all_buildings.append((lst, level))


print(all_buildings[0])

all_buildings = sorted(all_buildings)

sz = len(all_buildings)

start_lon = float(all_buildings[sz//2][0][0][0])
start_lat = float(all_buildings[sz//2][0][0][1])


print(all_buildings[0])


def get_xy(lon, lat):
    lon = float(lon)
    lat = float(lat)
    mul = 111.321 * 1000 # meters
    diff_lon = lon - start_lon
    diff_lat = lat - start_lat
    return (diff_lon * mul, diff_lat*mul)
     
buildings_xy = []

for lst in all_buildings:
    tmp = [] 
    for i in lst[0]:
        tmp.append(get_xy(i[0], i[1]))
        
    # height froom levels
    h = lst[1]
    buildings_xy.append((tmp, h))

print(buildings_xy[0])



# Polygons ready, now use it below

#cubeList  = cmds.ls('myCube*')
#if len(cubeList) > 0:
#    cmds.delete(cubeList)
   
   

all_poly = []
cnt = 0

obs_list = []

for lst in buildings_xy:
    cnt += 1
    tmp = []

    for i in lst[0]:
        (x,y) = i
        x/=-100
        z = 0
        y /= 100
        tmp.append((x,y,z))
    h = lst[1]

    verts = tmp
    bm = bmesh.new()
    for v in verts:
        bm.verts.new((v[0], v[1], 1))
    bm.faces.new(bm.verts)
    
    bm.normal_update()
    
    # Flip normal if required
    for f in bm.faces:
        if f.normal[2] < 0:
            f.normal_flip()    
    
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    
    ob = bpy.data.objects.new("Obz"+str(cnt), me)
    ob.modifiers.new("Solidify", type='SOLIDIFY')
    ob.modifiers["Solidify"].thickness = h/10

	# [start] Adding Glow to each object created, comment it out if not needed    
    matName = "Mater"+str(cnt)
    skymaterial = bpy.data.materials.new(matName)
    ob.active_material = skymaterial 
    skymaterial.use_nodes = True
    nodes = skymaterial.node_tree.nodes
    nodes.clear()


    # Create needed Nodes
    nodeOut = nodes.new(type='ShaderNodeOutputMaterial')
    nodeEmission = nodes.new(type='ShaderNodeEmission')
    r = g = b = 0
    if cnt % 3 == 0:
        r = 1.0
        g = 0
        b = 0
    elif cnt % 3 == 1:
        r = 0
        g = 0.5
        b = 1
    elif cnt % 3 == 2:
        r = 0.5
        g = 0
        b = 0.5
        
    nodeEmission.inputs['Color'].default_value = (r,g,b,1)
    nodeEmission.inputs['Strength'].default_value = 4
    
    # Link them together
    links = skymaterial.node_tree.links
    linkOut = links.new(nodeEmission.outputs[0], nodeOut.inputs[0])

    # [end] of Adding Glow to each objct created

    copy = ob.copy()
    obs_list.append(copy)
    print("Done", cnt)
#    if cnt > 7000:
#        break
    
cnt = 1
for ob in obs_list:
    print("Linking ", cnt)
    cnt+=1
    bpy.context.scene.collection.objects.link(ob)

