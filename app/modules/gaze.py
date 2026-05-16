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
        if len(self.points) < 5:
            self.points = []
            return []

        results = []
        raw_points = np.array(self.points)
        
        # Rayon de recherche de départ (15% du tracé)
        zone_depart = raw_points[:max(5, len(raw_points) // 6)]
        
        for char, child_node in self.root.children.items():
            if child_node.coords:
                # Trouver le point de départ idéal pour ce mot précis
                distances_depart = np.linalg.norm(zone_depart - np.array(child_node.coords), axis=1)
                idx_depart = int(np.argmin(distances_depart))
                initial_distance = distances_depart[idx_depart]

                self.search(results, raw_points, child_node, idx_depart, char, initial_distance)

        self.points = []
        return sorted(results, key=lambda x: x[1])

    def search(self, results, raw_points, node, path_index, current_word, total_error):
        path_len = len(raw_points)
        word_len = len(current_word)

        if word_len > 0 and (total_error / word_len) > 0.40:
            return

        if node.is_word:
            if path_index >= int(path_len * 0.85):
                score_final = total_error / word_len
                results.append((node.word, score_final))

        if path_index >= path_len - 1:
            return

        pas_estime = max(50, (path_len - path_index) // 2)
        idx_fin_fenetre = min(path_index + pas_estime, path_len)
        
        points_futurs = raw_points[path_index:idx_fin_fenetre]

        for char, child_node in node.children.items():
            if child_node.coords is None:
                continue

            distances = np.linalg.norm(points_futurs - np.array(child_node.coords), axis=1)
            
            if len(distances) == 0:
                continue
                
            idx_meilleur_local = int(np.argmin(distances))
            meilleure_distance = distances[idx_meilleur_local]

            if meilleure_distance > 0.35:
                continue

            prochain_index_global = path_index + idx_meilleur_local
            
            while prochain_index_global < path_len - 1:
                dist_suivante = np.linalg.norm(raw_points[prochain_index_global + 1] - np.array(child_node.coords))
                if dist_suivante <= meilleure_distance * 1.25:
                    prochain_index_global += 1
                else:
                    break

            if prochain_index_global <= path_index:
                prochain_index_global = path_index + 1

            self.search(results, raw_points, child_node, prochain_index_global, 
                        current_word + char, total_error + meilleure_distance)