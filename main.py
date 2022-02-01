#!/usr/bin/env python
"""
This is an example PyGame animation that uses "delta-time" to ensure that
screen updates are unaffected by framerate. There are three sprites which
move at different velocities (in this case pixels per second). It estimates
the expected time for each of the sprites to cross the screen and displays
the actual time. They should be approximately the same and more importantly
the same in any execution environment.
"""

import os
import sys
import time
import pygame as pg

from decimal import Decimal

CAPTION = "Delta Time"
SCREEN_SIZE = (600, 400)  # size of screen we are working with
BACKGROUND_COLOR = (100, 200, 200)
DEBUG_OVERLAY_SIZE = (300, 200)
DEBUG_OVERLAY_BACKGROUND_COLOR = (0, 0, 0, 200)
TRANSPARENT = (0, 0, 0, 0)
FPS = 60  # CHANGE ME - to your preferred frame rate

SPRITE_SIZE = (20, 20)
SPRITE1_VELOCITY = (50, 0)  # This sprite moves at ~ 50 pixels per second
SPRITE2_VELOCITY = (100, 0)  # This sprite moves at ~ 100 pixels per second
SPRITE3_VELOCITY = (200, 0)  # This sprite moves at ~ 200 pixels per second


class DebugOverlay(pg.sprite.Sprite):
    """
    This sprite provides a useful overlay of important information.
    Not really a sprite but we can add it to a SpriteGroup for updates.
    """
    def __init__(self, position, size, color):
        super(DebugOverlay, self).__init__()
        self.size = size
        self.color = color
        self.image = pg.Surface(self.size).convert_alpha()
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=position)
        self.font = pg.font.SysFont('Consolas', 12)
        self.position = position
        self.start_text_y = self.position[1] + 5
        self.start_time = time.time()
        self.time_now = self.start_time
        self.debug_text = []

    def update(self, keys, screen_rect, dt):
        """
        Update the debug string with latest information.
        """
        self.time_now = time.time()
        self.debug_text = [
            "width: " + str(SCREEN_SIZE[0]),
            "height:" + str(SCREEN_SIZE[1]),
            "FPS: " + str(FPS),
            "dt: " + str(dt),
            "time(s): " + str(Decimal('%2f' % (self.time_now - self.start_time)))
        ]

    def draw(self, surface):
        """
        Basic draw function.
        """
        start_y = self.start_text_y
        surface.blit(self.image, self.rect)
        for string in self.debug_text:
            rect = self.font.render(string, True, (255, 255, 255))
            surface.blit(rect, (5, start_y))
            start_y += 15


class Player(pg.sprite.Sprite):
    """
    This sprite is our player that will move across the screen.
    """
    def __init__(self, position, size, color, velocity):
        super(Player, self).__init__()
        self.position = position
        self.size = size
        self.color = color
        self.velocity = velocity
        self.image = pg.Surface(self.size).convert_alpha()
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topright=position)
        self.font = pg.font.SysFont('Consolas', 14)
        self.true_pos = list(self.rect.center)  # exact float position
        self.expected_time = str(Decimal('%2f' % (SCREEN_SIZE[0] / self.velocity[0]))) + "s"
        self.start_time = time.time()
        self.total_time = 0
        self.done = False

    def update(self, keys, screen_rect, dt):
        """
        Update accepts an argument dt (time delta between frames).
        Adjustments to position must be multiplied by this delta.
        Set the rect to true_pos once adjusted (automatically converts to int).
        """
        self.true_pos[0] += self.velocity[0] * dt
        self.true_pos[1] += self.velocity[1] * dt
        self.rect.center = self.true_pos
        # have we reached the edge of the screen yet?
        if self.reached_edge() and not self.done:
            self.total_time = time.time() - self.start_time
            self.done = True
        self.clamp(screen_rect)

    def clamp(self, screen_rect):
        """
        Clamp the rect to the screen if needed and reset true_pos to the
        rect position so they don't lose sync.
        """
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.true_pos = list(self.rect.center)

    def draw(self, surface):
        """
        Basic draw function.
        """
        surface.blit(self.image, self.rect)
        rect = self.font.render(self.expected_time, True, (0, 0, 0))
        surface.blit(rect, (0, self.rect.centery - 5))
        # have we reached the edge of the screen yet, if so display total time to get there
        if self.done:
            total_time_str = str(Decimal('%2f' % self.total_time)) + "s"
            rect = self.font.render(total_time_str, True, (0, 0, 0))
            surface.blit(rect, (self.rect.centerx - rect.get_width() - self.rect.width, self.rect.centery - 5))

    def reached_edge(self):
        """
        Simple check if right edge is touching right of screen
        """
        return self.rect.right >= SCREEN_SIZE[0]


class App(object):
    """
    Class responsible for program control flow.
    """
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('Consolas', 14)
        self.fps = FPS
        self.start_time = time.time()
        self.final_time = 0
        self.time_now = self.start_time
        self.done = False
        self.keys = pg.key.get_pressed()
        self.sprite1 = Player((0, 200), SPRITE_SIZE, (255, 0, 0), SPRITE1_VELOCITY)
        self.sprite2 = Player((0, 250), SPRITE_SIZE, (0, 255, 0), SPRITE2_VELOCITY)
        self.sprite3 = Player((0, 300), SPRITE_SIZE, (0, 0, 255), SPRITE3_VELOCITY)
        self.debug_overlay = DebugOverlay((0, 0), DEBUG_OVERLAY_SIZE, DEBUG_OVERLAY_BACKGROUND_COLOR)
        self.expected_rect = self.font.render("Expected", True, (0, 0, 0))
        self.actual_rect = self.font.render("Actual", True, (0, 0, 0))

    def event_loop(self):
        """
        Basic event loop.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type in (pg.KEYDOWN, pg.KEYUP):
                self.keys = pg.key.get_pressed()

    def update(self, dt):
        """
        Update all the sprites
        """
        self.sprite1.update(self.keys, self.screen_rect, dt)
        self.sprite2.update(self.keys, self.screen_rect, dt)
        self.sprite3.update(self.keys, self.screen_rect, dt)
        self.debug_overlay.update(self.keys, self.screen_rect, dt)

    def draw(self):
        """
        Basic draw function.
        """
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.expected_rect, (0, 150))
        self.screen.blit(self.actual_rect, (SCREEN_SIZE[0] - self.actual_rect.get_width(), 150))
        self.sprite1.draw(self.screen)
        self.sprite2.draw(self.screen)
        self.sprite3.draw(self.screen)
        self.debug_overlay.draw(self.screen)
        pg.display.update()

    def game_loop(self):
        """
        Simple game loop where we use the return value of the call to self.clock.tick
        to get the time delta between frames and pass it to all our sprites.
        """
        dt = 0
        self.clock.tick(self.fps)
        while not self.done:
            self.event_loop()
            self.update(dt)
            self.draw()
            dt = self.clock.tick(self.fps) / 1000.0


def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    App().game_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
