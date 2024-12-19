import pyray as pr
import math
import numpy as np
from pyray import Vector3

def initialize_camera():
    """Initialise la caméra 3D."""
    camera = pr.Camera3D(
        Vector3(0, 10, 10),  # position
        Vector3(0, 0, 0),    # cible
        Vector3(0, 1, 0),    # haut
        45,                  # fovy (champ de vision dans la direction y)
        pr.CAMERA_PERSPECTIVE
    )
    return camera

def update_camera_position(camera, movement_speed):
    """Met à jour la position de la caméra en fonction des touches pressées."""
    if pr.is_key_down(pr.KEY_W):
        camera.position.z -= movement_speed
    if pr.is_key_down(pr.KEY_S):
        camera.position.z += movement_speed
    if pr.is_key_down(pr.KEY_A):
        camera.position.x -= movement_speed
    if pr.is_key_down(pr.KEY_D):
        camera.position.x += movement_speed
    if pr.is_key_down(pr.KEY_Q):
        camera.position.y += movement_speed
    if pr.is_key_down(pr.KEY_E):
        camera.position.y -= movement_speed

def draw_fov_cone(point, direction, distance, angle_phi, color=pr.BLUE, segments=20):
    """
    Dessine un secteur circulaire représentant le champ de vision (FOV) 2D dans la direction d'un vecteur donné.
    
    :param point: Point de départ du cône (Vector3).
    :param direction: Vecteur de direction pour le centre du cône.
    :param distance: Portée maximale du FOV.
    :param angle_phi: Angle du FOV en degrés.
    :param color: Couleur du FOV.
    :param segments: Nombre de segments pour approximer le secteur circulaire.
    """
    
    # Normalise le vecteur de direction
    direction = vector_normalize(direction)
    
    # Convertit l'angle en radians et calcule l'angle demi
    half_angle_rad = math.radians(angle_phi / 2)
    
    # Calcule les points le long de l'arc du FOV
    angle_step = (2 * half_angle_rad) / segments
    points = []
    
    for i in range(segments + 1):
        # Calcule l'angle de rotation pour chaque segment
        rotation_angle = -half_angle_rad + i * angle_step
        rotated_direction = rotate_vector_y(direction, rotation_angle)
        
        # Redimensionne la direction tournée par la distance et traduit par le point de départ
        arc_point = Vector3(
            point.x + rotated_direction.x * distance,
            point.y + rotated_direction.y * distance,
            point.z + rotated_direction.z * distance
        )
        points.append(arc_point)
    
    # Dessine des lignes du point vers chaque segment d'arc et entre les segments consécutifs
    for i in range(len(points) - 1):
        pr.draw_line_3d(point, points[i], color)
        pr.draw_line_3d(points[i], points[i + 1], color)
    
    # Dessine le dernier segment reliant l'extrémité de l'arc au point de départ
    pr.draw_line_3d(point, points[-1], color)

def draw_vector_3(start, end, color, thickness=0.05, head_size_factor=0.8):
    """Dessine un vecteur en utilisant un cylindre et un cône."""
    direction = Vector3(end.x - start.x, end.y - start.y, end.z - start.z)
    length = vector_length(direction)
    head_size = length * head_size_factor
    
    n_direction = vector_normalize(direction)
    
    arrow_start = Vector3(start.x + n_direction.x * head_size, 
                          start.y + n_direction.y * head_size, 
                          start.z + n_direction.z * head_size)
    
    pr.draw_cylinder_ex(start, end, thickness / 2, thickness / 2, 8, color)
    pr.draw_cylinder_ex(arrow_start, end, thickness * 2, thickness / 5, 8, color)

def draw_points(points):
    
    fov_position = Vector3(0, 0, 0)
    fov_direction = Vector3(0, 0, 1)  # Vecteur directeur du cône
    fov_distance = 5
    fov_angle = 90
    
    for point in points:
        if is_point_in_fov(fov_position, fov_direction, fov_distance, fov_angle, point):
            pr.draw_sphere(point, 0.1, pr.GREEN)
        else : 
            pr.draw_sphere(point, 0.1, pr.RED)


def draw_vectors(points):
    for i in range(len(points) - 1):
        draw_vector_3(points[i], points[i + 1], pr.BLUE)

def cross_product(A, B):
    # TODO : mettre en œuvre le calcul du produit croisé
    
    return Vector3(A.y*B.z-A.z*B.y,-(A.x*B.z-A.z*B.x) , A.x*B.y - A.y*B.x)

def dot_product(A, B):
    return A.x*B.x + A.y*B.y +  A.z*B.z

def vector_length(vector):
    # TODO : implémenter le calcul de la longueur d'un vecteur (utiliser le produit scalaire cf. dot_product(A, B))
    return math.sqrt(dot_product(vector, vector))

def vector_normalize(vector):
    #TODO : mettre en œuvre la normalisation d'un vecteur
    length = vector_length(vector)
    if length != 0: 
        return Vector3(vector.x/length,vector.y/length,vector.z/length)
    else:
        return Vector3(0,0,0)

def rotate_vector_y(vector, angle):
    """Fait tourner un vecteur autour de l'axe Y selon un angle donné en radians."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vector3(
        vector.x * cos_a - vector.z * sin_a,
        vector.y,
        vector.x * sin_a + vector.z * cos_a
    )

def is_point_in_fov(fov_position, fov_direction, fov_distance, fov_angle, point):
    """
    Vérifie si un point est dans le champ de vision défini par une position, une direction, une distance et un angle.
    
    :param fov_position: Position du point de départ de FOV.
    :param fov_direction: Direction centrale du FOV.
    :param fov_distance: Distance maximale de portée de la FOV.
    :param fov_angle: Angle du FOV en degrés.
    :param point: Point à vérifier.
    :return: True si le point est dans le champ de vision, sinon False.
    """
    # TODO : Vecteur du FOV vers le point
    to_point = Vector3( point.x-fov_position.x, point.y -fov_position.y, point.z-fov_position.z)
    
    # TODO : Calcule la distance au point et vérifie qu'elle est dans la distance FOV

    distance = vector_length(to_point)
    if fov_distance < distance : 
        return False   # on retourne false directement si le distance au point est plus grande que la distance du fov 
    
    # Normalise la direction du FOV et le vecteur vers le point
    
    norm_fov_direction = vector_normalize(fov_direction)
    norm_to_point = vector_normalize(to_point)
    
    # TODO: Calcule le produit scalaire
    scalar= dot_product(norm_fov_direction, norm_to_point)
    
    # TODO Calcule le cosinus de l'angle demi du FOV
    cos_half_fov = math.cos(math.radians(fov_angle) / 2)
    
    
    
    # TODO Vérifie si le produit scalaire satisfait la condition du FOV
    return scalar>=cos_half_fov

def drawPara(vect1,vect2):
    # Dessine les vecteurs
    origin=pr.Vector3(0,0,0)
    vect3 =pr.Vector3(vect1.x+vect2.x,vect1.y+vect2.y,vect1.z+vect2.z)

    draw_vector_3(origin, vect1, pr.RED, thickness=0.05, head_size_factor=0.8)
    draw_vector_3(origin, vect2, pr.BLUE, thickness=0.05, head_size_factor=0.8)
    
    # Dessine les arêtes du parallélogramme
    pr.draw_line_3d(vect1, vect3, pr.GREEN)
    pr.draw_line_3d(vect2, vect3, pr.GREEN)

    # Dessine le parallélogramme
    vect=cross_product(vect1, vect2)
    if vect.y>0:
        pr.draw_triangle_3d(origin, vect1, vect2, pr.fade(pr.VIOLET, 0.5))
        pr.draw_triangle_3d(vect1, vect3, vect2, pr.fade(pr.VIOLET, 0.5))
    else:
        pr.draw_triangle_3d(origin, vect2, vect1, pr.fade(pr.VIOLET, 0.5))
        pr.draw_triangle_3d(vect2, vect3, vect1, pr.fade(pr.VIOLET, 0.5))
    
def main():
    pr.init_window(800, 600, "FOV")
    camera = initialize_camera()
    pr.set_target_fps(60)
    grid_size = 15
    movement_speed = 0.1
    
    fov_position = Vector3(0, 0, 0)
    fov_direction = Vector3(0, 0, 1)  # Vecteur directeur du cône
    point_a = Vector3(1.5, 0, 2)
    point_b = Vector3(2, 0, 4)
    point_c = Vector3(-5, 0, 4)
    point_d = Vector3(4,0,2)
    point_e = Vector3(-4, 0, -3)
    point_f = Vector3(5, 0, -3)
    points = [pr.Vector3(np.random.uniform(-5, 5), 0, np.random.uniform(0, 6)) for _ in range(20)]

    fov_distance = 5
    fov_angle = 90
    vect=cross_product(point_c, point_a)
    print(vect.x," ",vect.y," ",vect.z)
    print(is_point_in_fov(fov_position, fov_direction, fov_distance, fov_angle, point_a))


    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        
        pr.draw_grid(grid_size, 1)  # Dessine une grille pour référence
        draw_points([point_a, point_b, point_c,point_d])
        draw_points(points)
        draw_fov_cone(fov_position, fov_direction, fov_distance, fov_angle)
        
        drawPara(point_e, point_f)

        pr.end_mode_3d()
        pr.end_drawing()

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
