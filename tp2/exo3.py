import pyray as pr
import math
from pyray import Vector3
import trimesh

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

def load_ply_file(file_path):
    """Charge un fichier PLY et retourne le mesh en tant que structure de données trimesh."""
    mesh = trimesh.load(file_path)
    return mesh

def cross_product(A, B):
    return Vector3(A.y*B.z-A.z*B.y,-(A.x*B.z-A.z*B.x) , A.x*B.y - A.y*B.x)

def vector_length(vector):
    return math.sqrt(dot_product(vector, vector))

def vector_normalize(vector):
    length = vector_length(vector)
    if length != 0: 
        return Vector3(vector.x/length,vector.y/length,vector.z/length)
    else:
        return Vector3(0,0,0)

def dot_product(A, B):
    """Calcule le produit scalaire entre deux vecteurs A et B."""
    return A.x*B.x + A.y*B.y +  A.z*B.z

def compute_face_center(v0, v1, v2):
    """Calcule le centre d'une face triangulaire."""
    return Vector3(
        (v0.x + v1.x + v2.x) / 3,
        (v0.y + v1.y + v2.y) / 3,
        (v0.z + v1.z + v2.z) / 3
    )

def compute_vertex_normals(mesh, face_normals):
    """
    Calcule les normales pour chaque sommet en moyennant les normales des faces adjacentes.
    Retourne un dictionnaire avec chaque sommet et son vecteur normal associé.
    """
    
    # TODO : mettre en œuvre le calcul des normales pour chaque sommet en moyennant les normales des faces adjacentes
    vertex_normals = {i: Vector3(0, 0, 0) for i in range(len(mesh.vertices))}
    vertex_count = {i: 0 for i in range(len(mesh.vertices))}

    for face, (_, normal) in zip(mesh.faces, face_normals):
        for vertex_index in face:
            vertex_normals[vertex_index].x += normal.x
            vertex_normals[vertex_index].y += normal.y
            vertex_normals[vertex_index].z += normal.z
            vertex_count[vertex_index] += 1

    # TODO : Moyenne les normales (n'oubliez pas de normaliser)
    for i in vertex_normals:
        if vertex_count[i] > 0:
            vertex_normals[i].x /= vertex_count[i]
            vertex_normals[i].y /= vertex_count[i]
            vertex_normals[i].z /= vertex_count[i]
            
            # TODO: Normalisation
            vertex_normals[i]=vector_normalize(vertex_normals[i])

    return vertex_normals

def compute_face_normals(mesh):
    """Calcule les normales pour chaque face du mesh et retourne une liste de tuples (centre, normale)."""
    normals = []
    for face in mesh.faces:
        v0 = Vector3(*mesh.vertices[face[0]])
        v1 = Vector3(*mesh.vertices[face[1]])
        v2 = Vector3(*mesh.vertices[face[2]])

        # TODO : Calculer le vecteur normal de la face
        edge1 = Vector3(v1.x-v0.x,v1.y-v0.y,v1.z-v0.z) 
        edge2 = Vector3(v2.x-v0.x,v2.y-v0.y,v2.z-v0.z)
        normal = cross_product(edge1, edge2)
        normal = vector_normalize(normal)

        # Calculer le centre de la face
        center = compute_face_center(v0, v1, v2)
        
        normals.append((center, normal))
    return normals

def draw_vertex_normals(mesh, vertex_normals):
    """
    Dessine les normales des sommets comme des vecteurs à partir de chaque sommet.
    """
    for vertex_index, normal in vertex_normals.items():
        start_point = Vector3(*mesh.vertices[vertex_index])
        end_point = Vector3(
            start_point.x + normal.x * 0.5,
            start_point.y + normal.y * 0.5,
            start_point.z + normal.z * 0.5
        )
        draw_vector_3(start_point, end_point, pr.GREEN)  # Dessine le vecteur normal en vert

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

def draw_edge(start, end, color, thickness=0.05):
    """Dessine une arête comme un cylindre."""
    pr.draw_cylinder_ex(start, end, thickness / 2, thickness / 2, 8, color)

def draw_mesh(mesh):
    """Dessine le mesh complet avec sommets, arêtes et faces."""
    # Dessine les faces sous forme de triangles
    for face in mesh.faces:
        v0 = Vector3(*mesh.vertices[face[0]])
        v1 = Vector3(*mesh.vertices[face[1]])
        v2 = Vector3(*mesh.vertices[face[2]])
        pr.draw_triangle_3d(v0, v1, v2, pr.LIGHTGRAY)  # Dessine la face comme un triangle rempli
    
    # Dessine les arêtes
    for edge in mesh.edges:
        v_start = Vector3(*mesh.vertices[edge[0]])
        v_end = Vector3(*mesh.vertices[edge[1]])
        draw_edge(v_start, v_end, pr.BLACK)  # Dessine l'arête
    
    # Dessine les sommets
    for vertex in mesh.vertices:
        pr.draw_sphere(Vector3(*vertex), 0.05, pr.RED)  # Dessine les sommets comme de petites sphères

def draw_face_normals(face_normals):
    """Dessine les normales des faces comme des vecteurs à partir du centre de chaque face."""
    for center, normal in face_normals:
        end_point = Vector3(
            center.x + normal.x * 0.5,  # Échelle de la normale pour la visualisation
            center.y + normal.y * 0.5,
            center.z + normal.z * 0.5
        )
        draw_vector_3(center, end_point, pr.BLUE)  # Dessine le vecteur normal

def main():
    pr.init_window(1000, 800, "PLY Viewer with Normals")
    camera = initialize_camera()
    pr.set_target_fps(60)
    movement_speed = 0.1

    # Charge et affiche le fichier PLY
    ply_file_path = "dolphin.ply"  # Remplacez par le chemin de votre fichier PLY
    mesh = load_ply_file(ply_file_path)
    face_normals = compute_face_normals(mesh)
    vertex_normals = compute_vertex_normals(mesh, face_normals)

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        
        draw_mesh(mesh)              # Affiche les sommets, arêtes et faces du fichier PLY
        draw_face_normals(face_normals)  # Affiche les normales des faces
        draw_vertex_normals(mesh, vertex_normals)  # Affiche les normales des sommets

        pr.end_mode_3d()
        pr.end_drawing()

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
