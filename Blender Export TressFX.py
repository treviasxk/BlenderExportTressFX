# Software Developed by Trevias Xk
# Social Networks:     treviasxk
# Github:              https://github.com/treviasxk
# GithubPage:		   https://github.com/treviasxk/BlenderExportTressFX
# Paypal:              trevias@live.com


bl_info = {
	"name": "Blender Export TressFX",
	"author": "Trevias Xk (@treviasxk)",
	"version": (0, 1, 0),
	"blender": (4, 0, 0),
	"location": "File > Export > TressFX",
	"description": "Blender Export TressFX is an add-ons for blender, with it you can export particles to the TressFX file (.tfx).",
	"warning": "THIS IS AN ALPHA VERSION AND IT DOESN'T WORK PROPERLY!",
	"wiki_url": "https://github.com/treviasxk/BlenderExportTressFX",
	"category": "Export",
}

if "bpy" in locals():
    import imp
    if "export_tfx" in locals():
        imp.reload(export_tfx)


import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from bpy_extras.io_utils import (ExportHelper, path_reference_mode, axis_conversion,)


class ExportTFX(Operator, ExportHelper):
    '''Selection to TFX'''
    bl_idname = "export_scene.tfx"
    bl_label = "Export TFX"
    bl_options = {'PRESET'}

    filename_ext = ".tfx"
    filter_glob = StringProperty(default="*.tfx", options={'HIDDEN'})


    use_export_selected: BoolProperty(
            name="Selected Objects",
            description="Export only selected objects (and visible in active layers if that applies).",
            default=True,
            )
 
    use_bothEndsImmovable: BoolProperty(
            name="Both ends immovable",
            description="",
            default=False,
            )

    use_InvertZ: BoolProperty(
            name="Invert Z",
            description="",
            default=False,
            )	

    use_exportSkinCheckBox: BoolProperty(
            name="Export skin data",
            description="",
            default=False,
            )
			
    use_randomStrandCheckBox: BoolProperty(
            name="Randomize strands for LOD",
            description="",
            default=True,
            )


    @property
    def check_extension(self):
        return True#return self.batch_mode == 'OFF'

    def check(self, context):
        return True


    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")


        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "xna_validate",
                                            ))

        return save(self, context, **keywords)


def menu_func(self, context):
    self.layout.operator(ExportTFX.bl_idname, text="TressFX (.tfx)")


def register():
    bpy.utils.register_class(ExportTFX)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ExportTFX)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()


import ctypes
from mathutils import Vector, Matrix

def RoundF(a): 
    delta = 0.0001  # Round numbers up to 4 digits after decimal point
    d = 1/delta
    a = round(a*d)
    return a/d
	

def Dist_V_to_a_Face(v,f):
    v0 = f.v[0]
    v1 = f.v[1]
    v2 = f.v[2]
    vec1 = Mathutils.Vector(v0.co.x-v1.co.x,v0.co.y-v1.co.y,v0.co.z-v1.co.z)
    vec2 = Mathutils.Vector(v2.co.x-v1.co.x,v2.co.y-v1.co.y,v2.co.z-v1.co.z)
    A = vec1[1]*vec2[2]-vec1[2]*vec2[1]
    B = vec1[0]*vec2[2]-vec1[2]*vec2[0]
    C = vec1[0]*vec2[1]-vec1[1]*vec2[0]
    D = -(A*v0.co.x+B*v0.co.y+C*v0.co.z)
    m = 1/math.sqrt(A*A+B*B+C*C)
    if (D>0):
        m = -m
    cos_Alfa = m*A
    cos_Beta = m*B
    cos_Gamma = m*C
    p = -m*D
    Alfa = math.degrees(math.acos(cos_Alfa))
    Beta = math.degrees(math.acos(cos_Beta))
    Gamma = math.degrees(math.acos(cos_Gamma))
    d = abs(v.co.x*cos_Alfa+v.co.y*cos_Beta+v.co.z*cos_Gamma-p)
    d = RoundF(d)
    return d    
    

def Index_Vert_to_Faces(v,faces):
	fl = False
	d_min = 0
	fi_min = 0  
	for f in faces:
		d = Dist_V_to_a_Face(v,f)
		if fl:
			if (d_min > d):
				d_min = d
				fi_min = f.index
		else:
			d_min = d
			fl = True  
	return fi_min

class TressFXTFXFileHeader(ctypes.Structure):
    _fields_ = [('version', ctypes.c_float),
                ('numHairStrands', ctypes.c_uint),
                ('numVerticesPerStrand', ctypes.c_uint),
                ('offsetVertexPosition', ctypes.c_uint),
                ('offsetStrandUV', ctypes.c_uint),
                ('offsetVertexUV', ctypes.c_uint),
                ('offsetStrandThickness', ctypes.c_uint),
                ('offsetVertexColor', ctypes.c_uint),
                ('reserved', ctypes.c_uint * 32)]

class Point(ctypes.Structure):
	_fields_ = [('x', ctypes.c_float),
				('y', ctypes.c_float),
				('z', ctypes.c_float)]	

class TressFXSkinFileObject(ctypes.Structure):
	_fields_ = [('version', ctypes.c_uint),
				('numHairs', ctypes.c_uint),
				('numTriangles', ctypes.c_uint),
				('reserved1', ctypes.c_uint * 31), 
				('hairToMeshMap_Offset', ctypes.c_uint),
				('perStrandUVCoordniate_Offset', ctypes.c_uint),
				('reserved1', ctypes.c_uint * 31)]      
	
class HairToTriangleMapping(ctypes.Structure):
	_fields_ = [('mesh', ctypes.c_uint),
				('triangle', ctypes.c_uint),
				('barycentricCoord_x', ctypes.c_float),
				('barycentricCoord_y', ctypes.c_float),
				('barycentricCoord_z', ctypes.c_float),
				('reserved', ctypes.c_uint)]  
					
class TfxExporter:

	def SaveTFXBinaryFile(self, filepath, pss, locs):
		numCurves = len(pss)
		numVerticesPerStrand = 9999
		
		npss = len(pss)
		for i in range(npss):
			ps = pss[i]
			pnum = len(ps.particles)
			curves = ps.particles
			numCurves = numCurves + pnum
			if(len(ps.particles) == 0):
				continue
			curveFn = curves[0]
			dz = len(curveFn.hair_keys)
			if(dz<numVerticesPerStrand):
				numVerticesPerStrand = dz
		
		#print (self.config["use_bothEndsImmovable"])
		print("total particles num:"+str(numCurves))
		

		rootPositions = []

		tfxHeader = TressFXTFXFileHeader()
		tfxHeader.version = 4.0
		tfxHeader.numHairStrands = numCurves
		tfxHeader.numVerticesPerStrand = numVerticesPerStrand
		tfxHeader.offsetVertexPosition = ctypes.sizeof(TressFXTFXFileHeader)
		tfxHeader.offsetStrandUV = 0
		tfxHeader.offsetVertexUV = 0
		tfxHeader.offsetStrandThickness = 0
		tfxHeader.offsetVertexColor = 0

		f = open(filepath, "wb")
		f.write(tfxHeader)

		for i in range(npss):
			print("exporting particle system {}".format(i))
			ps = pss[i]
			loc = locs[i]
			pnum = len(ps.particles)
			curves = ps.particles
			print(loc)
			for j in range(pnum):
				curveFn = curves[j]
				#dz = len(curveFn.hair_keys)
				
				for k in range(0, numVerticesPerStrand):
					pos = loc+ curveFn.hair_keys[k].co
					#print(particle.hair_keys[k].co_local )
					#print(particle.hair_keys[k].co)
					p = Point()
					p.x = pos.x
					p.y = pos.y
					
					if(self.config["use_InvertZ"]):
						p.z = -pos.z # flip in z-axis
					else:
						p.z = pos.z

					f.write(p)
					
					# # root pos used to find face index
					if(k==0):
						rootPositions.append(pos)
						#print(pos)
						#print(curveFn.hair_keys[k].co_local )
						#print(curveFn.hair_keys[k].co)
						#print(loc + curveFn.hair_keys[k].co)
		
		f.close()
		
		return rootPositions	
	
  
			
	def SaveTFXSkinBinaryFile(filepath, faceIdList, baryCoordList, uvCoordList): 
		tfxSkinObj = TressFXSkinFileObject()
		tfxSkinObj.version = 1
		tfxSkinObj.numHairs = len(faceIdList)
		tfxSkinObj.numTriangles = 0
		tfxSkinObj.hairToMeshMap_Offset = ctypes.sizeof(TressFXSkinFileObject)
		tfxSkinObj.perStrandUVCoordniate_Offset = tfxSkinObj.hairToMeshMap_Offset + len(faceIdList) * ctypes.sizeof(HairToTriangleMapping)
		
		f = open(filepath, "wb")
		f.write(tfxSkinObj)
		
		for i in range(len(faceIdList)):
			mapping = HairToTriangleMapping()
			mapping.mesh = 0
			mapping.triangle = faceIdList[i]
			
			uvw = baryCoordList[i]
			mapping.barycentricCoord_x = uvw.x
			mapping.barycentricCoord_y = uvw.y
			mapping.barycentricCoord_z = uvw.z
			
			f.write(mapping)
			
		# per strand uv coordinate
		for i in range(len(uvCoordList)):
			uv_coord = uvCoordList[i]
			p = Point()
			p.x = uv_coord.x
			p.y = 1.0 - uv_coord.y # DirectX has it inverted
			p.z = uv_coord.z 
			
			f.write(p)    
		
		f.close()
		 
		return
	
	def get_particle_systems(self):
		for obj in self.scene.objects:
			if (obj.type=="MESH" ):  #selected objects system
				if( self.config["use_export_selected"] and not obj.select_get):
					continue
					
				nps = len(obj.particle_systems)
				print("mesh " + obj.name +" has particle system:" + str(nps))
				#print(obj.location)
				if(nps>0):
					for i in range(nps):
						ps = obj.particle_systems[i]
						if(ps!=None):
							if (not ps in self.valid_pss):
								self.valid_pss.append(ps)	
								self.co_pss.append(obj.location)
		return
		
	def export(self):
		#print("in TfxExporter.export 2")
		self.get_particle_systems()

		npss = len(self.valid_pss)
		print("particle sys num:"+ str(npss))
		
		ps = self.valid_pss[0]
		pnum = len(ps.particles)
		#print("particle num of 1st sys:"+str(pnum))
		
		self.SaveTFXBinaryFile(self.path , self.valid_pss, self.co_pss)

		#need to export skin?
		if(self.config["use_exportSkinCheckBox"] == False):
			return True
		
		#get the mesh used as base to grow hair or fur
		mesh = ps.parent
		if(mesh!=None):
			for i in range(len(rootPositions)):
				rootPoint = rootPositions[i]
				triangleId = Index_Vert_to_Faces(rootPoint,mesh.faces) # find the id of the nearest face 
				faceIdList.append(triangleId)
				
				#barycentric list
			
				#UV list
			
			#SaveTFXSkinBinaryFile
			
		return True

	def __init__(self,path,keys,operator):
		self.valid_pss=[]	#valid particle systems
		self.co_pss=[]	#location of particle systems
		self.path=path
		self.scene=bpy.context.scene
		self.config=keys



def save(operator, context, **keys):
	#print("in export_tfx.save")
	exp = TfxExporter(operator.filepath, keys, operator)
	exp.export()
	return {'FINISHED'}  


