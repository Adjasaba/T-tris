import tkinter as tk
import random 

# Dimensions de la grille
GRID_WIDTH = 9  # Nombre de colonnes
GRID_HEIGHT = 18  # Nombre de lignes
GRID_SIZE = 28  # Taille d'une case
CANVAS_WIDTH = GRID_WIDTH * GRID_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Différentes formes de tetris
SHAPES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "S": [(0, 1), (1, 1), (1, 0),(2, 1)],
    "J": [(0, 0), (0, 1), (0, 2), (1, 0)],
}

# Couleurs des blocs
SHAPE_COLORS = ["#f87041", "#3ba8c4", "#aeac2a", "#ffd400", "#e42b1f","#9917ce"]  # Orange, Bleu, Vert, Jaune, Rose,violet

class TetrisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris Game")
        

        # Interface principale
        self.main_frame = tk.Frame(root, bg="#c3c7b7")
        self.main_frame.pack(fill="both", expand=True)

        # En-tête pour le choix du pseudo
        self.name_frame = tk.Frame(self.main_frame, bg="#c3c7b7")
        self.name_frame.grid(row=0, column=0, pady=10)

        self.name_label = tk.Label(self.name_frame, text="Pseudo:", bg="#c3c7b7", font=("Retropix", 14))
        self.name_label.pack(side="left", padx=5)

        self.name_entry = tk.Entry(self.name_frame, font=("Retropix", 14))
        self.name_entry.pack(side="left", padx=5)

        self.start_button = tk.Button(self.name_frame, text="Start", command=self.start_game, font=("Retropix", 12))
        self.start_button.pack(side="left", padx=5)

        # Score, niveau et pseudo affichés
        self.header_frame = tk.Frame(self.main_frame, bg="#c3c7b7")
        self.header_frame.grid(row=1, column=0, pady=10)

        self.pseudo_label = tk.Label(self.header_frame, text="Pseudo: ---", bg="#c3c7b7", font=("Retropix", 14))
        self.pseudo_label.pack(side="left", padx=10)

        self.score_label = tk.Label(self.header_frame, text="Score: 0", bg="#c3c7b7", font=("Retropix", 14))
        self.score_label.pack(side="left", padx=10)

        self.level_label = tk.Label(self.header_frame, text="Niveau: 1", bg="#c3c7b7", font=("Retropix", 14))
        self.level_label.pack(side="left", padx=10)

        # Canvas pour le jeu
        self.canvas = tk.Canvas(self.main_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#484944")
        self.canvas.grid(row=2, column=0, padx=20, pady=20)

        # Variables utiles 
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.pseudo = None
        self.level = 1
        self.speed = 250  # Vitesse initiale (en millisecondes)
        self.paused = False  # Statut de pause
        self.high_score = 0  # Initialiser le meilleur score
        self.high_score_pseudo = ""  # Initialiser le pseudo du meilleur score

        # Ajouter un Label pour afficher le meilleur score
        self.high_score_label = tk.Label(
            root, text=f"Record: {self.high_score} par {self.high_score_pseudo}",
            font=("Arial", 12), fg="white", bg="black"
        )
        self.high_score_label.pack(side="bottom", pady=10)

    def start_game(self):
        """
        Initialise le jeu après que le joueur ait saisi son pseudo.
        """
        self.pseudo = self.name_entry.get().strip() or "Player"
        self.pseudo_label.config(text=f"Pseudo: {self.pseudo}")

        # Désactiver l'entrée du nom après le démarrage
        self.name_entry.config(state="disabled")
        self.start_button.config(state="disabled")

        # Réinitialiser les variables
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.level = 1
        # Définir la vitesse initiale
        self.speed = max(200, self.speed - 25)  # Réduit la vitesse de 25 ms à chaque niveau
        self.update_score(0)

        # Démarrer le jeu
        self.spawn_piece()
        self.update()
        self.root.bind("<Left>", lambda event: self.move_piece(-1))
        self.root.bind("<Right>", lambda event: self.move_piece(1))
        self.root.bind("<Down>", lambda event: self.move_piece(0, 1))
        self.root.bind("<Up>", lambda event: self.rotate_piece())
        self.root.bind("<p>", lambda event: self.toggle_pause()) 
        self.root.bind("<n>", lambda event: self.start_game())
        
      

    def spawn_piece(self):
        """
        Fait apparaître une nouvelle pièce.
        """
        shape_name = random.choice(list(SHAPES.keys()))
        color = random.choice(SHAPE_COLORS)
        self.current_piece = {
            "name": shape_name,
            "blocks": SHAPES[shape_name],
            "x": GRID_WIDTH // 2 - 1,
            "y": 0,
            "color": color,
        }
        if not self.can_place_piece():
            self.game_over = True

    def can_place_piece(self, x_offset=0, y_offset=0, blocks=None):
        """
        Vérifie si une pièce peut être placée à une position donnée.
        """
        if blocks is None:
            blocks = self.current_piece["blocks"]
        for x, y in blocks:
            new_x = self.current_piece["x"] + x + x_offset
            new_y = self.current_piece["y"] + y + y_offset
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                return False
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                return False
        return True

    def move_piece(self, x_offset, y_offset=0):
        """
        Déplace une pièce si possible.
        """
        if not self.paused and self.can_place_piece(x_offset, y_offset):
            self.current_piece["x"] += x_offset
            self.current_piece["y"] += y_offset
            self.draw()

    def rotate_piece(self):
        """
        Fait pivoter une pièce.
        """
        rotated = [(-y, x) for x, y in self.current_piece["blocks"]]
        if self.can_place_piece(blocks=rotated):
            self.current_piece["blocks"] = rotated
            self.draw()

    def lock_piece(self):
        """
        Fixe une pièce dans la grille.
        """
        for x, y in self.current_piece["blocks"]:
            grid_x = self.current_piece["x"] + x
            grid_y = self.current_piece["y"] + y
            if 0 <= grid_y < GRID_HEIGHT:
                self.grid[grid_y][grid_x] = self.current_piece["color"]
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """
        Efface les lignes complètes et met à jour le score.
        """
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        self.update_score(lines_cleared)

    def update_score(self, lines):
        """
        Met à jour le score et le niveau.
        """
        self.score += lines * 100
        self.score_label.config(text=f"Score: {self.score}")

        # Vérifie si le joueur a atteint un nouveau niveau
        if self.score >= self.level * 500:
            self.level += 1
            # Réduit la vitesse (augmente la difficulté)
            self.speed = max(50, self.speed - 50)  # Réduit la vitesse de 50 ms à chaque niveau
            self.level_label.config(text=f"Niveau: {self.level}")
            # Jouer le son de changement de niveau
             # playsound("level_up.mp3")  # Jouer le son

            # Mettre à jour le meilleur score si nécessaire
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_score_pseudo = self.pseudo
                self.display_high_score()

    def display_high_score(self):
        """
        Met à jour le Label du meilleur score.
        """
        self.high_score_label.config
        text=f"Record: {self.high_score} par {self.high_score_pseudo}"
 
    def update(self):
        """
        Met à jour l'état du jeu.
        """
        if not self.game_over and not self.paused:
            if self.can_place_piece(0, 1):
                self.move_piece(0, 1)
            else:
                self.lock_piece()
            self.draw()
            self.root.after(self.speed, self.update)
        elif self.game_over:
            self.display_game_over()

    def display_game_over(self):
        """
        Affiche l'écran Game Over.
        """
        self.canvas.delete("all")
        self.root.bind("<c>", lambda event: self.restart_game())
        self.root.bind("<n>", lambda event: self.start_game())
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT // 3,
            text=f"GAME OVER\n{self.pseudo}\nScore: {self.score}",
            fill="black", font=("Retropix", 20)
             
        )
        
        self.root.bind("<r>", lambda event: self.restart_game())
        self.root.bind("<n>", lambda event: self.start_game())

    def draw(self):
        """
        Dessine la grille et la pièce actuelle.
        """
        self.canvas.delete("all")

        # Dessiner la grille
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x]
                if color:
                    self.draw_block(x, y, color)
                else:
                    self.canvas.create_rectangle(
                        x * GRID_SIZE, y * GRID_SIZE, (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                        outline="gray", width=1
                    )

        if self.current_piece:
            for x, y in self.current_piece["blocks"]:
                self.draw_block(self.current_piece["x"] + x, self.current_piece["y"] + y, self.current_piece["color"])

    def draw_block(self, x, y, color):
        """
        Dessine un bloc.
        """
        x1 = x * GRID_SIZE
        y1 = y * GRID_SIZE
        x2 = x1 + GRID_SIZE
        y2 = y1 + GRID_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def restart_game(self):
        """
        Redémarre le jeu.
        """
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.update()

    def toggle_pause(self):
        """
        Met le jeu en pause ou reprend le jeu.
        """
        if self.paused:
            self.paused = False
            self.update()
        else:
            self.paused = True
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="PAUSE", fill="black", font=("Retropix", 20))


if __name__ == "__main__":
    root = tk.Tk()
    app = TetrisApp(root)
    root.mainloop()
