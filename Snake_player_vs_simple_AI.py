import pygame
from pygame.locals import *
import numpy as np
import time

SIZE = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WIDTH = 600
HEIGHT = 500

class Apple:
    def __init__(self, screen):
        self.screen = screen
        self.move()

    def draw(self):
        pygame.draw.rect(self.screen, RED, [self.x, self.y, SIZE, SIZE])
        pygame.display.flip()

    def move(self):
        self.x = np.random.randint(WIDTH / SIZE) * SIZE
        self.y = np.random.randint(HEIGHT / SIZE) * SIZE

class Snake:
    def __init__(self, surface, length):
        self.length = length
        self.screen = surface
        self.color = GREEN
        self.x = [SIZE] * length
        self.y = [SIZE] * length
        self.size = SIZE
        self.direction = 'down'

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def move_left(self):
        self.direction = 'left'

    def move_right(self):
        self.direction = 'right'

    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'

    def draw(self):
        self.screen.fill(BLACK)
        for i in range(self.length):
            pygame.draw.rect(self.screen, self.color, [self.x[i], self.y[i], self.size, self.size])
        pygame.display.flip()

    def move(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        if self.direction == 'up':
            self.y[0] -= self.size
        if self.direction == 'down':
            self.y[0] += self.size
        if self.direction == 'right':
            self.x[0] += self.size
        if self.direction == 'left':
            self.x[0] -= self.size

        self.draw()



class SnakeAI(Snake):
    def __init__(self, surface, length, apple):
        super().__init__(surface, length)
        self.color = WHITE
        self.apple = apple

    def move_towards_apple(self, apple_x, apple_y):
        if self.x[0] < apple_x:
            self.move_right()
        elif self.x[0] > apple_x:
            self.move_left()
        elif self.y[0] < apple_y:
            self.move_down()
        elif self.y[0] > apple_y:
            self.move_up()

    def draw(self):
        for i in range(self.length):
            pygame.draw.rect(self.screen, self.color, [self.x[i], self.y[i], self.size, self.size])
        pygame.display.flip()
            

    def avoid_player_snake(self, player_snake):
        directions = ['up', 'down', 'left', 'right']
        best_direction = None
        min_distance = float('inf')
        apple_x, apple_y = self.apple.x, self.apple.y

        for direction in directions:
            future_x, future_y = self.x[0], self.y[0]

            if direction == 'up':
                future_y -= SIZE
            elif direction == 'down':
                future_y += SIZE
            elif direction == 'left':
                future_x -= SIZE
            elif direction == 'right':
                future_x += SIZE

            collision = False
            if (future_x < 0 or future_x >= WIDTH or future_y < 0 or future_y >= HEIGHT):
                collision = True
            else:
                for i in range(self.length):
                    if (future_x == self.x[i] and future_y == self.y[i]):
                        collision = True
                        break
                for i in range(player_snake.length):
                    if (future_x == player_snake.x[i] and future_y == player_snake.y[i]):
                        collision = True
                        break

            if not collision:
                distance = abs(future_x - apple_x) + abs(future_y - apple_y)
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction

        if best_direction:
            self.set_direction(best_direction)

    def set_direction(self, direction):
        if direction == 'left':
            self.move_left()
        elif direction == 'right':
            self.move_right()
        elif direction == 'up':
            self.move_up()
        elif direction == 'down':
            self.move_down()        
            
    def move(self):
        self.avoid_player_snake(game.snake)  # Avoid collision with player snake
        super().move()  # Call base class move
        

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.snake = Snake(self.surface, 2)
        self.apple = Apple(self.surface)
        self.snake_ai = SnakeAI(self.surface, 2, self.apple)
        self.snake.draw()
        self.apple.draw()
        self.snake_ai.draw()

    def collision(self, x1, y1, x2, y2):
        return x1 >= x2 and x1 < x2 + SIZE and y1 >= y2 and y1 < y2 + SIZE

    def play(self):
        pygame.display.set_caption('Snake: You vs. AI')
        self.snake.move()
        self.snake_ai.move_towards_apple(self.apple.x, self.apple.y)
        self.snake_ai.move()

        self.apple.draw()

        # Collision with apple for player snake
        if self.collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.snake.increase_length()
            self.apple.move()

        # Collision with apple for AI snake
        if self.collision(self.snake_ai.x[0], self.snake_ai.y[0], self.apple.x, self.apple.y):
            self.snake_ai.increase_length()
            self.apple.move()

        # Collision with itself for player snake
        for i in range(3, self.snake.length):
            if self.collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                print("Game Over")
                self.running = False
                
        # Collision with AI snake for player snake
        for i in range(0, (self.snake_ai.length)):
            if self.collision(self.snake.x[0], self.snake.y[0], self.snake_ai.x[i], self.snake_ai.y[i]):
                print("Game Over")
                self.running = False

        # Collision with borders for player snake
        if (self.snake.x[0] >= WIDTH) or (self.snake.x[0] < 0) or (self.snake.y[0] >= HEIGHT) or (self.snake.y[0] < 0):
            print("Game Over")
            self.running = False


    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    if event.key == K_UP:
                        self.snake.move_up()
                    if event.key == K_DOWN:
                        self.snake.move_down()
                    if event.key == K_LEFT:
                        self.snake.move_left()
                    if event.key == K_RIGHT:
                        self.snake.move_right()
                elif event.type == QUIT:
                    self.running = False

            time.sleep(0.3)
            self.play()

if __name__ == '__main__':
    game = Game()
    game.run()



            