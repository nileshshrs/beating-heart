import pygame
import random
import math

# Constants
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 600
CANVAS_CENTER_X = CANVAS_WIDTH // 2
CANVAS_CENTER_Y = CANVAS_HEIGHT // 2
IMAGE_ENLARGEMENT = 11
HEART_COLOR = (255, 33, 33)  # RGB value for red

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
pygame.display.set_caption("Beating Heart")
clock = pygame.time.Clock()

def heart_function(t, shrink_ratio=IMAGE_ENLARGEMENT):
    x = 16 * math.sin(t)**3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    x *= shrink_ratio
    y *= shrink_ratio
    return int(x + CANVAS_CENTER_X), int(-y + CANVAS_CENTER_Y)

def scatter_inside(x, y, beta=0.15):
    ratio_x = beta * math.log(random.random())
    ratio_y = beta * math.log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X)**2 + (y - CANVAS_CENTER_Y)**2)**0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def curve(p):
    return 2 * (2 * math.sin(4 * p)) / (2 * math.pi)

def distance_from_center(x, y):
    return math.sqrt((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2)

class Heart:
    def __init__(self, generate_frame=20):
        self.points = set()
        self.center_diffusion_points = set()
        self.inner_scattered_points = set()
        self.all_points = {}
        self.generate_frame = generate_frame
        self.build(2000)

        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # Outer edge points
        for _ in range(number):
            t = random.uniform(0, 2 * math.pi)
            x, y = heart_function(t)
            self.points.add((x, y))

        # Add scattered edge points
        for _x, _y in list(self.points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self.points.add((x, y))

        # Center diffusion points
        point_list = list(self.points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self.center_diffusion_points.add((x, y))

        # Inner scattered points with distance-based density
        self.inner_scatter_points()

        # Extra scattered inner particles with density based on distance
        for _ in range(3500):
            t = random.uniform(0, 2 * math.pi)
            base_x, base_y = heart_function(t, shrink_ratio=random.uniform(7, 10.5))
            base_x += random.randint(-8, 8)
            base_y += random.randint(-8, 8)

            # Decrease particle density as we move closer to the center
            distance = distance_from_center(base_x, base_y)
            density_factor = 1 / (1 + distance / 100)

            # Randomize density based on distance
            if random.random() < density_factor:
                self.inner_scattered_points.add((base_x, base_y))

    def inner_scatter_points(self):
        """Generate particles to fill the inner space of the heart and ensure it reaches the center."""
        for _ in range(30000):  # Increase the number of particles to cover all space
            t = random.uniform(0, 2 * math.pi)
            base_x, base_y = heart_function(t, shrink_ratio=random.uniform(7, 10.5))

            # Add small random variation to ensure a better distribution of particles
            base_x += random.randint(-8, 8)
            base_y += random.randint(-8, 8)

            # Calculate the distance from the center
            distance = distance_from_center(base_x, base_y)

            # Adjust the density factor to allow more particles to reach the center
            density_factor = 1 / (1 + (distance ** 2) / 40)  # Smooth gradient to allow more particles closer to center

            # Randomize and let particles fill from outer to inner part
            if random.random() < density_factor:
                self.inner_scattered_points.add((base_x, base_y))

    def calc_position(self, x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 20 * math.pi)
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * math.pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * math.pi) ** 2))

        all_points = []
        heart_halo_point = set()

        # Halo glow
        for _ in range(halo_number):
            t = random.uniform(0, 2 * math.pi)
            x, y = heart_function(t, shrink_ratio=11.6)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 3))
                all_points.append((x, y, size))

        # Main edge
        for x, y in self.points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # Center particles
        for x, y in self.center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        # Scattered inner particles with distance-based density
        for x, y in self.inner_scattered_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.choice((1, 2))
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            pygame.draw.rect(render_canvas, HEART_COLOR, pygame.Rect(x, y, size, size))

# Main game loop
def main():
    heart = Heart(generate_frame=20)
    render_frame = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))  # Fill the screen with black
        heart.render(screen, render_frame)
        render_frame += 1

        pygame.display.flip()  # Update the screen
        clock.tick(20)  # 60 FPS

if __name__ == "__main__":
    main()

## not working 3d heart code idk how to get the exact numbers
# import pygame
# import random
# import math

# # Constants
# CANVAS_WIDTH = 640
# CANVAS_HEIGHT = 600
# CANVAS_CENTER_X = CANVAS_WIDTH // 2
# CANVAS_CENTER_Y = CANVAS_HEIGHT // 2
# IMAGE_ENLARGEMENT = 11
# HEART_COLOR = (255, 33, 33)  # RGB value for red

# # Initialize Pygame
# pygame.init()
# screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
# pygame.display.set_caption("Beating Heart 3D")
# clock = pygame.time.Clock()

# def heart_function(t, shrink_ratio=IMAGE_ENLARGEMENT):
#     x = 16 * math.sin(t)**3
#     y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
#     x *= shrink_ratio
#     y *= shrink_ratio
#     return int(x + CANVAS_CENTER_X), int(-y + CANVAS_CENTER_Y)

# def scatter_inside(x, y, beta=0.035):  # Tighter scatter
#     ratio_x = beta * math.log(random.random())
#     ratio_y = beta * math.log(random.random())
#     dx = ratio_x * (x - CANVAS_CENTER_X)
#     dy = ratio_y * (y - CANVAS_CENTER_Y)
#     return x - dx, y - dy

# def shrink(x, y, ratio):
#     force = -1 / (((x - CANVAS_CENTER_X)**2 + (y - CANVAS_CENTER_Y)**2)**0.6)
#     dx = ratio * force * (x - CANVAS_CENTER_X)
#     dy = ratio * force * (y - CANVAS_CENTER_Y)
#     return x - dx, y - dy

# def curve(p):
#     return 2 * (2 * math.sin(4 * p)) / (2 * math.pi)

# def distance_from_center(x, y):
#     return math.sqrt((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2)

# class Heart:
#     def __init__(self, generate_frame=20):
#         self.points = set()
#         self.center_diffusion_points = set()
#         self.inner_scattered_points = set()
#         self.all_points = {}
#         self.generate_frame = generate_frame
#         self.build(2000)

#         for frame in range(generate_frame):
#             self.calc(frame)

#     def build(self, number):
#         # Outer edge points
#         for _ in range(number):
#             t = random.uniform(0, 2 * math.pi)
#             x, y = heart_function(t)
#             self.points.add((x, y))

#         # Add scattered edge points
#         for _x, _y in list(self.points):
#             for _ in range(3):
#                 x, y = scatter_inside(_x, _y, 0.035)  # Sharper edge scatter
#                 self.points.add((x, y))

#         # Center diffusion points
#         point_list = list(self.points)
#         for _ in range(4000):
#             x, y = random.choice(point_list)
#             x, y = scatter_inside(x, y, 0.17)
#             self.center_diffusion_points.add((x, y))

#         # Inner scattered points with distance-based density
#         self.inner_scatter_points()

#         # Extra scattered inner particles with distance based on distance
#         for _ in range(3500):
#             t = random.uniform(0, 2 * math.pi)
#             base_x, base_y = heart_function(t, shrink_ratio=random.uniform(7, 10.5))
#             base_x += random.randint(-5, 5)  # Tighter scatter
#             base_y += random.randint(-5, 5)

#             distance = distance_from_center(base_x, base_y)
#             density_factor = 1 / (1 + distance / 100)

#             if random.random() < density_factor:
#                 self.inner_scattered_points.add((base_x, base_y))

#     def inner_scatter_points(self):
#         """Generate particles to fill the inner space of the heart and ensure it reaches the center."""
#         for _ in range(30000):
#             t = random.uniform(0, 2 * math.pi)
#             base_x, base_y = heart_function(t, shrink_ratio=random.uniform(7, 10.5))
#             base_x += random.randint(-5, 5)  # Tighter scatter
#             base_y += random.randint(-5, 5)

#             distance = distance_from_center(base_x, base_y)
#             density_factor = 1 / (1 + (distance ** 2) / 40)

#             if random.random() < density_factor:
#                 self.inner_scattered_points.add((base_x, base_y))

#     def calc_position(self, x, y, ratio):
#         force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.49)  # Stronger center pull
#         dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
#         dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
#         return x - dx, y - dy

#     def calc(self, generate_frame):
#         ratio = 10 * curve(generate_frame / 20 * math.pi)
#         halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * math.pi)))
#         halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * math.pi) ** 2))

#         all_points = []
#         heart_halo_point = set()

#         # Halo glow
#         for _ in range(halo_number):
#             t = random.uniform(0, 2 * math.pi)
#             x, y = heart_function(t, shrink_ratio=11.6)
#             x, y = shrink(x, y, halo_radius)
#             if (x, y) not in heart_halo_point:
#                 heart_halo_point.add((x, y))
#                 x += random.randint(-18, 18)  # Softer outer glow
#                 y += random.randint(-18, 18)
#                 size = random.choice((1, 2, 3))
#                 all_points.append((x, y, size))

#         # Main edge
#         for x, y in self.points:
#             x, y = self.calc_position(x, y, ratio)
#             dist = distance_from_center(x, y)
#             if dist < 50:
#                 size = random.choice((2, 3))  # Bigger particles near center
#             elif dist < 100:
#                 size = random.choice((1, 2))
#             else:
#                 size = 1
#             all_points.append((x, y, size))

#         # Center particles
#         for x, y in self.center_diffusion_points:
#             x, y = self.calc_position(x, y, ratio)
#             dist = distance_from_center(x, y)
#             if dist < 50:
#                 size = random.choice((2, 3))
#             elif dist < 100:
#                 size = random.choice((1, 2))
#             else:
#                 size = 1
#             all_points.append((x, y, size))

#         # Scattered inner particles
#         for x, y in self.inner_scattered_points:
#             x, y = self.calc_position(x, y, ratio)
#             dist = distance_from_center(x, y)
#             if dist < 50:
#                 size = random.choice((2, 3))
#             elif dist < 100:
#                 size = random.choice((1, 2))
#             else:
#                 size = 1
#             all_points.append((x, y, size))

#         self.all_points[generate_frame] = all_points

#     def render(self, render_canvas, render_frame):
#         for x, y, size in self.all_points[render_frame % self.generate_frame]:
#             pygame.draw.rect(render_canvas, HEART_COLOR, pygame.Rect(x, y, size, size))

# # Main game loop
# def main():
#     heart = Heart(generate_frame=20)
#     render_frame = 1

#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 return

#         screen.fill((0, 0, 0))  # Black background
#         heart.render(screen, render_frame)
#         render_frame += 1

#         pygame.display.flip()
#         clock.tick(20)

# if __name__ == "__main__":
#     main()
# # This code creates a 3D beating heart animation using Pygame.
# # The heart is generated using a mathematical function and is animated to give a beating effect.