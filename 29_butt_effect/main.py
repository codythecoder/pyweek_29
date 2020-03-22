#!/usr/bin/env python3

import pygame
import sys
import colorsys

pygame.init()

SCREEN_SIZE = (1000, 600)
DRAW_WIDTH = 10
BLACK = (0, 0, 0)
CLOCK_SPEED = 60
DRAW_SCREEN_SIZE = (600, 600)
FLASH_SPEED = 1
FLASH_FRAMES = 30
FLASH_DISTANCE = 0.1

screen = pygame.display.set_mode(SCREEN_SIZE)

def lock_value(x, low=None, high=None):
    if low is not None and x < low:
        return low
    if high is not None and x > high:
        return high
    return x

class Draw_Screen(pygame.sprite.Sprite):
    def __init__(self, size, pos):
        pygame.sprite.Sprite.__init__(self, Draw_Screen.containers)

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.pos = pos
        self.hue = 0

        self.lines = []

        self.last_pos = None

        self.draw_cycle = 0

    def update(self):
        if not self.lines:
            return

        self.image.fill((0, 0, 0, 0))

        real_cycle = self.draw_cycle / int(FLASH_SPEED*CLOCK_SPEED) * len(self.lines)
        real_frames = len(self.lines) / int(FLASH_DISTANCE*CLOCK_SPEED)

        for i, (color, start, end) in enumerate(self.lines):
            hue = 0.01 * i
            if i > real_cycle:
                dist = real_cycle%FLASH_FRAMES - (i - len(self.lines))
            else:
                dist = real_cycle%FLASH_FRAMES - i

            if dist < real_frames:
                draw_color = colorsys.hsv_to_rgb(self.hue, 1, 1-dist/real_frames)
                reflected_start = self.rect.width - start[0], start[1]
                reflected_end = self.rect.width - end[0], end[1]

                pygame.draw.line(self.image, color, start, end, DRAW_WIDTH)
                pygame.draw.line(self.image, color, reflected_start, reflected_end, DRAW_WIDTH)

        self.draw_cycle += 1
        self.draw_cycle %= int(FLASH_SPEED*CLOCK_SPEED)

    def interact(self, mouse_pos, mouse_pressed):
        if not mouse_pressed[0]:
            self.last_pos = None
            return

        adjusted_pos = mouse_pos[0] - self.pos[0], mouse_pos[1] - self.pos[1]

        if self.last_pos is None:
            self.last_pos = adjusted_pos
            return

        if self.last_pos == adjusted_pos:
            return


        draw_color = colorsys.hsv_to_rgb(self.hue, 1, 1)
        draw_color = draw_color[0] * 255, draw_color[1] * 255, draw_color[2] * 255

        reflected_last = self.rect.width - self.last_pos[0], self.last_pos[1]
        reflected_now = self.rect.width -  adjusted_pos[0], adjusted_pos[1]

        pygame.draw.line(self.image, draw_color, self.last_pos, adjusted_pos, DRAW_WIDTH)
        pygame.draw.line(self.image, draw_color, reflected_last, reflected_now, DRAW_WIDTH)

        self.lines.append((draw_color, self.last_pos, adjusted_pos))

        self.hue += 0.01
        self.hue %= 1
        self.last_pos = adjusted_pos

def draw_butt(screen):
    hue = 0
    last_pos = None
    interact_group = pygame.sprite.Group()
    update_group = pygame.sprite.Group()
    draw_group = pygame.sprite.Group()

    Draw_Screen.containers = [interact_group, update_group, draw_group]

    drawer = Draw_Screen(DRAW_SCREEN_SIZE, (200,0))
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)

        for sprite in interact_group:
            sprite.interact(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
        for sprite in update_group:
            sprite.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_group.draw(screen)
        pygame.display.flip()
        clock.tick(CLOCK_SPEED)

draw_butt(screen)
while True:
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    pygame.display.flip()
