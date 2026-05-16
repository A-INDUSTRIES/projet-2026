import json, requests
import numpy as np
from .utils import Singleton, getUserDataPath
from .logger import info

WORDS_PATH = getUserDataPath() / "words.csv"
KEYS_PATH = getUserDataPath() / "coords.json"
WORDS_URL = "https://cloud.aindustries.be/public.php/dav/files/2BsGPFqP685CBMC"
KEYS_URL = "https://cloud.aindustries.be/public.php/dav/files/3Ya9mwmEwsLY2Yc"

TO_REPLACE = [("é", "e"),
                ("è", "e"),
                ("ê", "e"),
                ("ë", "e"),
                ("à", "a"),
                ("â", "a"),
                ("ä", "a"),
                ("ì", "i"),
                ("î", "i"),
                ("ï", "i"),
                ("ò", "o"),
                ("ô", "o"),
                ("ö", "o"),
                ("ù", "u"),
                ("û", "u"),
                ("ü", "u"),
                ("ç", "c"),
                ("œ", "oe"),
                ("-", ""),
                ("æ", "ae"),
                ("ñ", "n"),
                ("ã", "a"),
                ("ó", "o"),
                ("/", ""),
                (" ", "")]

# Arbre 'Trie'
class Node:
    def __init__(self, char=None, coords=None):
        self.char = char
        self.coords = coords
        self.children = {}
        self.is_word = False
        self.word = ""

class GazeTyping(metaclass=Singleton):
    def __init__(self):
        self.root = Node()
        self.points = []

        if not KEYS_PATH.exists():
            info("Téléchargement de la base des touches en cours.")
            response = requests.get(KEYS_URL)

            with open(KEYS_PATH, 'wb') as f:
                f.write(response.content)

        with open(KEYS_PATH, 'r') as f:
            self.keys = json.load(f)

        if not WORDS_PATH.exists():
            info("Téléchargement de la base de données des mots en cours.")
            response = requests.get(WORDS_URL)

            with open(WORDS_PATH, 'wb') as f:
                f.write(response.content)

        with open(WORDS_PATH, 'r', encoding="utf-8-sig") as f:
            for word in f.readlines():
                word = word.strip()
                self.insert(word)

    def insert(self, word):
        node = self.root

        chars = word
        for a, b in TO_REPLACE:
            chars = chars.replace(a, b)

        for char in chars:
            if char not in node.children:
                coords = self.keys[char]
                node.children[char] = Node(char, [coords["x"], coords["y"]])
            node = node.children[char]
        node.word = word
        node.is_word = True
    
    def point(self, point):
        self.points.append(point)

    def end(self):
        if len(self.points) < 5:  # Sécurité minimale
            self.points = []
            return []

        results = []
        # On utilise directement self.points (qui peut contenir 1000 points)
        raw_points = np.array(self.points) 
        
        for char, child_node in self.root.children.items():
            if child_node.coords:
                # Étape 1 : Trouver le point le plus proche du départ dans les 10% premiers points
                # (Permet de tolérer un regard qui s'est posé un peu avant de commencer à écrire)
                zone_depart = raw_points[:max(5, len(raw_points) // 10)]
                distances_depart = np.linalg.norm(zone_depart - np.array(child_node.coords), axis=1)
                idx_depart = int(np.argmin(distances_depart))
                initial_distance = distances_depart[idx_depart]

                # Lancer la recherche à partir de cet index optimal
                self.search(results, raw_points, child_node, idx_depart, char, initial_distance)

        self.points = []
        return sorted(results, key=lambda x: x[1])

    def search(self, results, raw_points, node, path_index, current_word, total_error):
        # 1. Seuil d'erreur adapté aux coordonnées normalisées sur un long tracé
        if total_error > 8.0:
            return

        path_len = len(raw_points)

        # 2. Si le nœud actuel est un mot complet, on valide s'il reste assez de points
        if node.is_word:
            # Si on est proche de la fin du tracé (dans les 15% derniers points)
            if path_index >= path_len - max(5, path_len // 7):
                # Score final normalisé par la longueur pour ne pas pénaliser les mots longs
                score_final = total_error / len(current_word)
                results.append((node.word, score_final))

        # 3. ALGORITHME DE BALAYAGE (Look-ahead)
        # On ne passe pas bêtement au point suivant (index + 1). On cherche dans la fenêtre 
        # de points suivants celui qui se rapproche le plus de la PROCHAINE lettre cible.
        fenetre_recherche = max(10, path_len // 10)  # Taille de la zone de scan
        idx_fin_fenetre = min(path_index + fenetre_recherche, path_len)

        if path_index >= path_len or idx_fin_fenetre <= path_index:
            return

        for char, child_node in node.children.items():
            if child_node.coords is None:
                continue

            # Extraire les points futurs du tracé pour cette recherche
            points_futurs = raw_points[path_index:idx_fin_fenetre]
            
            # Calculer la distance de TOUS ces points par rapport à la lettre suivante
            distances = np.linalg.norm(points_futurs - np.array(child_node.coords), axis=1)
            
            # Trouver le point qui fait le "meilleur score" (le creux de la courbe)
            idx_meilleur_local = int(np.argmin(distances))
            meilleure_distance = distances[idx_meilleur_local]
            
            # Le nouvel index dans le tracé global devient la position de cette lettre trouvée
            prochain_index_global = path_index + idx_meilleur_local

            # On descend d'un niveau dans le Trie en sautant directement à ce point du tracé
            self.search(results, raw_points, child_node, prochain_index_global, 
                        current_word + char, total_error + meilleure_distance)