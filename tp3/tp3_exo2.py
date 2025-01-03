import pyray as pr
import numpy as np
from pyray import Vector3
from  exo3 import cross_product , vector_length, vector_normalize, dot_product
from tp3_exo1 import scaling_matrix_homogeneous, orthographic_projection_matrix_homogeneous, perspective_projection_matrix
# Importer les fonctions et utilitaires existants
from tp3_exo1 import (
    initialize_camera,
    update_camera_position,
    load_ply_file,
    initialize_mesh_for_transforming,
    apply_transformations_homogeneous,
    draw_mesh,
    rotation_matrix_homogeneous,
    translation_matrix
)
def draw_plane(axis, size=5, color=pr.GRAY):
    """Dessine un plan basé sur un vecteur normal et une taille."""
    axis = vector_normalize(axis)
    orthogonal_vector = Vector3(1, 0, 0) if abs(axis.x) < abs(axis.y) else Vector3(0, 1, 0)
    v1 = cross_product(axis, orthogonal_vector)
    v2 = cross_product(axis, v1)

    for i in range(-size, size + 1):
        start1 = Vector3(v1.x * -size + v2.x * i, -20+(v1.y * -size + v2.y * i), v1.z * -size + v2.z * i)
        end1 = Vector3(v1.x * size + v2.x * i,  -20+(v1.y * size + v2.y * i), v1.z * size + v2.z * i)
        start2 = Vector3(v2.x * -size + v1.x * i,  -20+(v2.y * -size + v1.y * i), v2.z * -size + v1.z * i)
        end2 = Vector3(v2.x * size + v1.x * i,  -20+(v2.y * size + v1.y * i), v2.z * size + v1.z * i)
        
        pr.draw_line_3d(start1, end1, color)
        pr.draw_line_3d(start2, end2, color)

def scaling_matrix_isotropic(k):
    """
    Génère une matrice homogène de mise à l'échelle isotrope (4x4)
    autour d'un axe arbitraire dans l'espace 3D.
    """
    return np.array([
        [k, 0, 0, 0],
        [0, k, 0, 0],
        [0, 0, k, 0],
        [0, 0, 0, 1]
    ])

def main():
    pr.init_window(1000, 900, "Cube central tournant avec cubes orbitaux")
    pr.set_target_fps(60)

    # Charger l'objet central
    mesh_file = "cube.ply"  # Remplacez par le chemin réel vers votre fichier PLY
    mesh = load_ply_file(mesh_file)
    initialize_mesh_for_transforming(mesh)

    # Contrôles GUI
    translate_x_ptr = pr.ffi.new('float *', 0.0)
    translate_y_ptr = pr.ffi.new('float *', 0.0)
    translate_z_ptr = pr.ffi.new('float *', 0.0)
    rotation_angle_ptr = pr.ffi.new('float *', 0.0)
    axis_x_ptr = pr.ffi.new('float *', 1.0)
    axis_y_ptr = pr.ffi.new('float *', 0.0)
    axis_z_ptr = pr.ffi.new('float *', 0.0)
    orbit_count_ptr = pr.ffi.new('float *', 5)
    orbit_radius_ptr = pr.ffi.new('float *', 5)
    projection_ptr = pr.ffi.new('bool *', 0)
    pers_ptr = pr.ffi.new('bool *', 0)

    
    
    
    # Créer une liste de cubes orbitaux
    max_orbits = 50
    orbit_cubes = []
    for _ in range(max_orbits):
        orbit_cubes.append({
            "transform": np.eye(4),
            "angle_offset": np.random.uniform(0, 2 * np.pi),
            "inclination": np.random.uniform(-np.pi / 4, np.pi / 4),
            "rotation_axis": Vector3(
                np.random.uniform(-1, 1),
                np.random.uniform(-1, 1),
                np.random.uniform(-1, 1)
            ),
            "clockwise": np.random.choice([True, False]),  # Rotation aléatoire (horaire ou antihoraire)
            "radius": np.random.uniform(1,2),
            "k": np.random.uniform(0.1,3)
            
        })
    
    camera = initialize_camera()

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed = 0.1)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)

        # Transformation du cube central
        tx = translate_x_ptr[0]
        ty = translate_y_ptr[0]
        tz = translate_z_ptr[0]
        central_transform  = translation_matrix(tx, ty, tz)
        
        rotation_axis = Vector3(axis_x_ptr[0], axis_y_ptr[0], axis_z_ptr[0])
        angle= rotation_angle_ptr[0]
        central_rotation = rotation_matrix_homogeneous(rotation_axis, np.radians(angle))
        

        # Dessiner le cube central
        apply_transformations_homogeneous(mesh, central_transform, central_rotation, np.eye(4), np.eye(4))
        draw_mesh(mesh,pr.RED)

        # Dessine le plan 
        draw_plane(Vector3(0,1,0), 50)
        
        #projection 
        projection_mat=np.eye(4)
        if projection_ptr[0]:
            projection_mat = orthographic_projection_matrix_homogeneous(Vector3(0,1,0),-20)
            
            
        # Dessiner les cubes orbitaux
        for i in range(round(orbit_count_ptr[0])):
            orbit = orbit_cubes[i]
            # TODO : expliquer cette ligne en expérimentant et en lisant la documentation
            angle = pr.get_time() * (1 if orbit["clockwise"] else -1) + orbit["angle_offset"]

            # Rotation autour de l'axe du cube
            orbit_rotation = rotation_matrix_homogeneous(orbit["rotation_axis"], angle)

            # Transformation du cube orbital relative au cube central
            """ Le mouvement se déroule principalement dans le plan xz, tandis 
            que la coordonnée y introduit une inclinaison pour donner l'impression 
            que l'orbite est inclinée dans l'espace 3D."""
            # Transformation orbitale
            orbit_x = np.cos(pr.get_time() + orbit["angle_offset"]) * orbit_radius_ptr[0]+orbit["radius"]
            orbit_y = np.sin(orbit["inclination"])                  * orbit_radius_ptr[0]+orbit["radius"]
            orbit_z = np.sin(pr.get_time() + orbit["angle_offset"]) * orbit_radius_ptr[0]+orbit["radius"]
            orbit_translation = translation_matrix(orbit_x, orbit_y, orbit_z)
            
            # Appliquer la rotation du cube central
            combined_transform = central_transform @ central_rotation @ orbit_translation          

            apply_transformations_homogeneous(mesh, combined_transform, orbit_rotation, scaling_matrix_isotropic(orbit["k"]), projection_mat)
                        
            draw_mesh(mesh)
            
        pr.end_mode_3d()

        # Contrôles GUI
        pr.draw_text("Contrôles du Cube Central", 10, 10, 20, pr.BLACK)
        pr.draw_text("Translation X:", 10, 40, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 60, 200, 20), "-5.0", "5.0", translate_x_ptr, -5.0, 5.0)
        pr.draw_text("Translation Y:", 10, 90, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 110, 200, 20), "-5.0", "5.0", translate_y_ptr, -5.0, 5.0)
        pr.draw_text("Translation Z:", 10, 140, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 160, 200, 20), "-5.0", "5.0", translate_z_ptr, -5.0, 5.0)
        pr.draw_text("Axe de Rotation X:", 10, 190, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 210, 200, 20), "-1.0", "1.0", axis_x_ptr, -1.0, 1.0)
        pr.draw_text("Axe de Rotation Y:", 10, 240, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 260, 200, 20), "-1.0", "1.0", axis_y_ptr, -1.0, 1.0)
        pr.draw_text("Axe de Rotation Z:", 10, 290, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 310, 200, 20), "-1.0", "1.0", axis_z_ptr, -1.0, 1.0)
        pr.draw_text("Angle de Rotation:", 10, 340, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 360, 200, 20), "0", "360", rotation_angle_ptr, 0.0, 360.0)
        pr.draw_text("Cubes Orbitaux:", 10, 400, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 420, 200, 20), "0", "50", orbit_count_ptr, 0, max_orbits)
        pr.draw_text("Rayon d'Orbite:", 10, 440, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 460, 200, 20), "0", "10", orbit_radius_ptr, 0, 10)
        pr.draw_text("Projection orthographique:", 10, 480, 20, pr.BLACK)
        pr.gui_check_box(pr.Rectangle(10, 500, 20, 20), "Activer", projection_ptr)
        pr.draw_text("Projection en perspective:", 10, 530, 20, pr.BLACK)
        pr.gui_check_box(pr.Rectangle(10, 550, 20, 20), "Activer", pers_ptr)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()
