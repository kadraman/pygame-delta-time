import sys
import time
from decimal import Decimal

import pygame as pg
from pygame import KEYDOWN, K_ESCAPE, QUIT

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
PLAYER_X_VELOCITY = 80  # pixels / second
FPS_OFFSET_X = 15

dark_area = None
font = None
reached_edge = False


class Player(pg.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pg.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()

    def update(self, dt):
        self.rect.move_ip(PLAYER_X_VELOCITY * dt, 0)

    def reached_edge(self):
        return self.rect.right >= SCREEN_WIDTH


fps_x = 0
fps_text = []
start_time = time.time()
final_time = time.time()
player = Player()


def update(dt):
    global fps_text, final_time, reached_edge
    if player.reached_edge():
        time_now = final_time
    else:
        time_now = time.time()
        final_time = time_now
        player.rect.move_ip(PLAYER_X_VELOCITY * dt, 0)

    fps_text = [
        "FPS: " + str(FPS),
        "dt: " + str(dt),
        "time(s): " + str(Decimal('%2f' % (time_now - start_time)))
    ]


def event_loop():
    pass


def draw(screen):
    global fps_x, dark_area, player
    fps_x = 105
    screen.fill((100, 200, 200))
    screen.blit(dark_area, (0, 100))
    screen.blit(player.surf, player.rect)

    for string in fps_text:
        rect = font.render(string, True, (255, 255, 255))
        screen.blit(rect, (5, fps_x))
        fps_x += FPS_OFFSET_X


def main():
    global dark_area, font
    pg.init()
    pg.display.set_caption("PyGame Delta Time example")
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pg.font.SysFont('Consolas', 12)
    clock = pg.time.Clock()
    done = False

    dark_area = pg.Surface((200, 100)).convert_alpha()
    dark_area.fill((0, 0, 0, 200))

    while not done:
        dt = clock.tick(FPS) / 1000
        for event in pg.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
            elif event.type == QUIT:
                done = True

        event_loop()
        update(dt)
        draw(screen)
        pg.display.update()

    pg.quit()
    sys.exit()


main()
