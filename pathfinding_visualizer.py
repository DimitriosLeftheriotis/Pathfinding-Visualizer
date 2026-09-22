import pygame
from queue import PriorityQueue, Queue, LifoQueue

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Visualizer")

ROWS = 40
GAP = WIDTH // ROWS

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
GREEN = (0, 255, 0)   # Start
RED = (255, 0, 0)     # End
BLUE = (0, 0, 255)    # Visited
YELLOW = (255, 255, 0)  # Path
PURPLE = (128, 0, 128)  # Frontier


# ---------------- NODE CLASS ----------------
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * GAP
        self.y = col * GAP
        self.color = WHITE
        self.neighbors = []
        self.previous = None

    def get_pos(self):
        return self.row, self.col

    def is_wall(self):
        return self.color == BLACK

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = GREEN

    def make_end(self):
        self.color = RED

    def make_wall(self):
        self.color = BLACK

    def make_visited(self):
        if self.color not in (GREEN, RED):
            self.color = BLUE

    def make_frontier(self):
        if self.color not in (GREEN, RED):
            self.color = PURPLE

    def make_path(self):
        if self.color not in (GREEN, RED):
            self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color,
                         (self.x, self.y, GAP, GAP))

    def update_neighbors(self, grid):
        self.neighbors = []

        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        for dr, dc in directions:
            r = self.row + dr
            c = self.col + dc
            if 0 <= r < ROWS and 0 <= c < ROWS:
                if not grid[r][c].is_wall():
                    self.neighbors.append(grid[r][c])


# ---------------- GRID ----------------
def make_grid():
    return [[Node(i, j) for j in range(ROWS)] for i in range(ROWS)]             


def draw_grid(win):
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i*GAP), (WIDTH, i*GAP))
        pygame.draw.line(win, GREY, (i*GAP, 0), (i*GAP, WIDTH))


def draw(win, grid):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win)
    pygame.display.update()


def get_clicked_pos(pos):
    x, y = pos
    return x // GAP, y // GAP


# ---------------- PATH RECONSTRUCTION ----------------
def reconstruct_path(end, draw):
    while end.previous:
        end = end.previous
        end.make_path()
        draw()


# ---------------- BFS ----------------
def bfs(draw, start, end):
    queue = Queue()
    queue.put(start)
    visited = {start}

    while not queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.get()

        if current == end:
            reconstruct_path(end, draw)
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                neighbor.previous = current
                neighbor.make_frontier()
                queue.put(neighbor)

        draw()
        current.make_visited()

    return False


# ---------------- DFS ----------------
def dfs(draw, start, end):
    stack = LifoQueue()
    stack.put(start)
    visited = {start}

    while not stack.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = stack.get()

        if current == end:
            reconstruct_path(end, draw)
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                neighbor.previous = current
                neighbor.make_frontier()
                stack.put(neighbor)

        draw()
        current.make_visited()

    return False


# ---------------- DIJKSTRA ----------------
def dijkstra(draw, start, end):
    count = 0
    pq = PriorityQueue()
    pq.put((0, count, start))

    dist = {start: 0}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = pq.get()[2]

        if current == end:
            reconstruct_path(end, draw)
            return True

        for neighbor in current.neighbors:
            temp = dist[current] + 1

            if neighbor not in dist or temp < dist[neighbor]:
                dist[neighbor] = temp
                count += 1
                pq.put((temp, count, neighbor))
                neighbor.previous = current
                neighbor.make_frontier()

        draw()
        current.make_visited()

    return False


# ---------------- A* ----------------
def heuristic(a, b):
    x1, y1 = a.get_pos()
    x2, y2 = b.get_pos()
    return abs(x1-x2) + abs(y1-y2)


def astar(draw, start, end):
    count = 0
    pq = PriorityQueue()
    pq.put((0, count, start))

    g_score = {start: 0}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = pq.get()[2]

        if current == end:
            reconstruct_path(end, draw)
            return True

        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1

            if neighbor not in g_score or temp_g < g_score[neighbor]:
                g_score[neighbor] = temp_g
                f = temp_g + heuristic(neighbor, end)
                count += 1
                pq.put((f, count, neighbor))
                neighbor.previous = current
                neighbor.make_frontier()

        draw()
        current.make_visited()

    return False


# ---------------- MAIN LOOP ----------------
def main():
    grid = make_grid()
    start = None
    end = None
    run = True

    while run:
        draw(WIN, grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # LEFT CLICK
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_wall()

            # RIGHT CLICK
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            # KEY CONTROLS
            if event.type == pygame.KEYDOWN and start and end:

                for row in grid:
                    for node in row:
                        node.update_neighbors(grid)

                if event.key == pygame.K_b:
                    bfs(lambda: draw(WIN, grid), start, end)

                if event.key == pygame.K_d:
                    dfs(lambda: draw(WIN, grid), start, end)

                if event.key == pygame.K_j:
                    dijkstra(lambda: draw(WIN, grid), start, end)

                if event.key == pygame.K_a:
                    astar(lambda: draw(WIN, grid), start, end)

                if event.key == pygame.K_c:
                    grid = make_grid()
                    start = None
                    end = None

    pygame.quit()


main()