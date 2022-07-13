import omni.ext
from pxr import Sdf, Gf
import omni.kit.commands
import omni.usd

def create_sphere(path, name, x,y,z, rad):
    omni.kit.commands.execute('CreatePrimWithDefaultXform',
        prim_type='Sphere',
        prim_path= f"/World/{name}",
        attributes={
            'radius': rad, 
            'extent': [(-50, -50, -50), (50, 50, 50)]
            }
        )
    omni.kit.commands.execute('ChangeProperty',
        prop_path=Sdf.Path(F"{path}{name}.xformOp:translate"),
        value=Gf.Vec3d(x,y,z),
        prev=Gf.Vec3d(x,y,z))
            
def create_sphere(path, name, vec3d, rad, ):
    omni.kit.commands.execute('CreatePrimWithDefaultXform',
        prim_type='Sphere',
        prim_path= f"{path}{name}",
        attributes={
            'radius': rad, 
            'extent': [(-50, -50, -50), (50, 50, 50)]
            }
        )
    omni.kit.commands.execute('ChangeProperty',
        prop_path=Sdf.Path(f"{path}{name}.xformOp:translate"),
        value=vec3d,
        prev=vec3d)

def create_scope(path):
    omni.kit.commands.execute('CreatePrimWithDefaultXform',
        prim_type='Scope',
        prim_path= f"{path}"
        )

def create_distant_light(path, name):
    omni.kit.commands.execute('CreatePrim',
                    prim_path=f"{path}{name}",
                    prim_type='DistantLight',
                    select_new_prim=False,
                    attributes={'angle': 1.0, 'intensity': 100},
                    create_default_xform=True)

def orient_distant_light(path, name, vec3dspherical):
    omni.kit.commands.execute('ChangeProperty',
                        prop_path=Sdf.Path(F"{path}{name}.xformOp:rotateXYZ"),
                        value = vec3dspherical,
                        prev = vec3dspherical)

def delete(path):
    omni.kit.commands.execute('DeletePrims',
        paths=[path])

def delete_all(paths):
    omni.kit.commands.execute('DeletePrims',
        paths=paths)