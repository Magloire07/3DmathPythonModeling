import pyray as pr
import math
from pyray import Vector3
import random

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

def generate_maze_path(nb_segments, taille_grille=15, longueur_segment=1.0, activer_3d=False):
    """
    Génère un chemin ressemblant à un labyrinthe dans une grille centrée autour de l'origine.
    Le chemin évite les auto-intersections et peut être généré en 2D ou en 3D.

    :param nb_segments: Nombre de segments dans le chemin.
    :param taille_grille: Taille de la grille pour limiter les mouvements du chemin.
    :param longueur_segment: Longueur de chaque segment.
    :param activer_3d: Si True, permet un mouvement sur l'axe y pour un chemin en 3D.
    :return: Liste de points Vector3 représentant le chemin du labyrinthe.
    """
    # Commence à un point aléatoire près de l'origine
    start_x = random.randint(-2, 2)
    start_z = random.randint(-2, 2)
    start_y = 0  # Commence au niveau du sol (y=0)
    
    points = [Vector3(start_x, start_y, start_z)]
    points_visites = {(start_x, start_y, start_z)}
    
    v1=Vector3(0,1,0)
    v2=Vector3(0,0,0)

    
    # Directions : mouvement en 2D (x, z) ou en 3D (x, y, z)
    directions = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
    if activer_3d:
        directions.extend([(0, 1, 0), (0, -1, 0)])  # Ajoute le mouvement sur l'axe y pour la 3D
    
    for _ in range(nb_segments):
        # Choisir une direction aléatoire et calculer la nouvelle position
        dx, dy, dz = random.choice(directions)
        new_x = points[-1].x + dx * longueur_segment
        new_y = points[-1].y + dy * longueur_segment
        new_z = points[-1].z + dz * longueur_segment

        # Vérifier que la nouvelle position est dans les limites et non revisitée
        if (-taille_grille <= new_x <= taille_grille and 
            -taille_grille <= new_y <= taille_grille and 
            -taille_grille <= new_z <= taille_grille and
            (new_x, new_y, new_z) not in points_visites):
            
            points.append(Vector3(new_x, new_y, new_z))
            points_visites.add((new_x, new_y, new_z))
        
    for i in range( len(points)-2):
        
        a= points[i]
        b= points[i+1]
        c= points[i+2]
        
        (v,r)=check_turn_direction(a, b, c)
        print(r)
        

        
    return points

def draw_vector_3(start, end, color, thickness=0.05):
    """Nous dessinons un vecteur en utilisant un cylindre et un cône."""
    direction = Vector3(end.x - start.x, end.y - start.y, end.z - start.z)
    length = vector_length(direction)
    head_size = length * 0.8
    
    n_direction = vector_normalize(direction)
    
    arrow_start = Vector3(start.x + n_direction.x * head_size, 
                          start.y + n_direction.y * head_size, 
                          start.z + n_direction.z * head_size)
    
    pr.draw_cylinder_ex(start, end, thickness / 2, thickness / 2, 8, color)
    pr.draw_cylinder_ex(arrow_start, end, thickness * 2, thickness / 5, 8, color)

def draw_points(points):
    colors = [pr.RED, pr.GREEN, pr.BLUE]
    for i, point in enumerate(points):
        pr.draw_sphere(point, 0.1, colors[i % len(colors)])

def draw_vectors(points):
    for i in range(len(points) - 1):
        draw_vector_3(points[i], points[i + 1], pr.GRAY)


def draw_text_if_visible_3(camera, text, position_3d, font_size=20, color=pr.BLACK):
    """
    Affiche le texte à une position 2D projetée à partir d'une coordonnée 3D si elle est dans les limites de l'écran.
    
    :param camera: La caméra utilisée pour la projection.
    :param text: Texte à afficher.
    :param position_3d: Position 3D du texte.
    :param font_size: Taille de la police du texte.
    :param color: Couleur du texte.
    """
    text_position_2d = pr.get_world_to_screen(position_3d, camera)
    if 0 <= text_position_2d.x <= pr.get_screen_width() and 0 <= text_position_2d.y <= pr.get_screen_height():
        pr.draw_text(text, int(text_position_2d.x), int(text_position_2d.y), font_size, color)
    else:
        print("La position du texte est hors des limites de l'écran :", text_position_2d)


def draw_scene(camera, grid_size, points, direction, turn):
    """
    Affiche les éléments de la scène : axes, points, vecteurs et direction de rotation.
    """
    pr.begin_drawing()
    pr.clear_background(pr.RAYWHITE)
    pr.begin_mode_3d(camera)
    
    pr.draw_grid(grid_size, 1)  # Dessine une grille pour référence
    draw_points(points) # Dessine les points
    draw_vectors(points) # Dessine les vecteurs

    pr.end_mode_3d()
    
    # Affiche le texte de direction de rotation si visible
    text_position_3d = Vector3(-3, 0, 0)
    text = f"Direction de rotation : {turn}"
    draw_text_if_visible_3(camera,text , text_position_3d, font_size=20, color=pr.BLACK)
    
    pr.end_drawing()

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

def check_turn_direction(a, b, c):
    """Calcule le produit vectoriel pour déterminer la direction de rotation."""
    
    # TODO : calculer les vecteurs de A vers B et de B vers C.
    AB = Vector3(b.x-a.x, b.y-a.y, b.z-a.z)
    BC = Vector3(c.x-b.x, c.y-b.y, c.z-b.z)
    
    cross_AB_BC = cross_product(AB, BC)

    # TODO : remplacez le « None » par des informations appropriées sur le virage
    if cross_AB_BC.y > 0:
        return cross_AB_BC, "antihoraire"
    elif cross_AB_BC.y < 0:
        return cross_AB_BC, "horaire"
    else:
        return cross_AB_BC, "Collinéaire"    

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

def main():
    pr.init_window(800, 600, "Produit Vectoriel pour la Direction de Rotation")
    camera = initialize_camera()
    pr.set_target_fps(60)
    grid_size = 15

    # Points de la scène
    a = Vector3(2, 0, 3)    # Premier point
    b = Vector3(-1, 0, 5)   # Point central
    c = Vector3(-4, 0, 1)   # Dernier point
    
    
    points = [a, b, c]

    # Calcule la direction de rotation
    direction, turn = check_turn_direction(a, b, c)

    movement_speed = 0.1
    
    # Génère des points pour la spirale en zigzag
    points = generate_maze_path(50, int(grid_size/2), 1.0, False)

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        draw_scene(camera, grid_size, points, direction, turn)

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
