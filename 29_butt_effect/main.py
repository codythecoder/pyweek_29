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
FLASH_FRAMES = 60
FLASH_DISTANCE = 0.5

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

        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.pos = pos
        self.hue = 0

        self.lines = []

        self.last_pos = None

        self.draw_cycle = 0

        self.__draw_blank()

        self.effect = False

    def __draw_blank(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.line(self.image, (255, 255, 255), (self.rect.width/2, 0), (self.rect.width/2, self.rect.height), 2)

    def update(self):
        if not self.lines:
            return

        self.__draw_blank()

        real_cycle = self.draw_cycle / (int(FLASH_SPEED*CLOCK_SPEED) * self.num_groups) * len(self.lines)
        real_lines = self.n_lines*FLASH_DISTANCE

        print(self.num_groups)

        if not self.effect:
            for i, (start, end) in enumerate(self.lines):
                hue = 0.01 * i
                color = colorsys.hsv_to_rgb(hue, 1, 1)
                color = color[0] * 255, color[1] * 255, color[2] * 255

                reflected_start = self.rect.width - start[0], start[1]
                reflected_end = self.rect.width - end[0], end[1]

                pygame.draw.line(self.image, color, start, end, DRAW_WIDTH)
                pygame.draw.line(self.image, color, reflected_start, reflected_end, DRAW_WIDTH)
            return

        for i, (start, end) in enumerate(self.lines):
            hue = 0.01 * i
            # dist_lines = (self.n_lines - i + self.draw_cycle/self.num_groups)%self.n_lines
            dist_lines = ((-i%self.n_lines)+real_cycle)%self.n_lines
            # if not i:
            #     print(f'{dist_lines:6.2f} {real_lines} {1-dist_lines/real_lines:5.2f}')

            if dist_lines < real_lines:
                color = colorsys.hsv_to_rgb(hue, 1, 1)
                color = color[0] * 255, color[1] * 255, color[2] * 255, (1-dist_lines/real_lines)*255

                reflected_start = self.rect.width - start[0], start[1]
                reflected_end = self.rect.width - end[0], end[1]

                pygame.draw.line(self.image, color, start, end, DRAW_WIDTH)
                pygame.draw.line(self.image, color, reflected_start, reflected_end, DRAW_WIDTH)

        self.draw_cycle += 1
        self.draw_cycle %= int(FLASH_SPEED*CLOCK_SPEED)

    def interact(self, mouse_pos, mouse_pressed):
        if not mouse_pressed[0]:
            self.effect = True
            self.last_pos = None
            return

        self.effect = False

        adjusted_pos = mouse_pos[0] - self.pos[0], mouse_pos[1] - self.pos[1]

        if self.last_pos is None:
            self.last_pos = adjusted_pos
            return

        if self.last_pos == adjusted_pos:
            return

        dist = ((self.last_pos[0] - adjusted_pos[0])**2 + (self.last_pos[1] - adjusted_pos[1])**2)**0.5

        if dist < 3:
            return

        draw_color = colorsys.hsv_to_rgb(self.hue, 1, 1)
        draw_color = draw_color[0] * 255, draw_color[1] * 255, draw_color[2] * 255

        reflected_last = self.rect.width - self.last_pos[0], self.last_pos[1]
        reflected_now = self.rect.width -  adjusted_pos[0], adjusted_pos[1]

        pygame.draw.line(self.image, draw_color, self.last_pos, adjusted_pos, DRAW_WIDTH)
        pygame.draw.line(self.image, draw_color, reflected_last, reflected_now, DRAW_WIDTH)

        self.lines.append((self.last_pos, adjusted_pos))

        self.hue += 0.01
        self.hue %= 1
        self.last_pos = adjusted_pos

        self.num_groups = max(1, int(len(self.lines)//FLASH_FRAMES))
        self.n_lines = len(self.lines)/self.num_groups

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
