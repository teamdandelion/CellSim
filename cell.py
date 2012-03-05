#!/usr/bin/env python
import os, sys

from cell_types import COSTS, TYPES_INFO
from cell_programs import grass
from random import randint

import pygame
from pygame import Rect, Color
from pygame.sprite import Sprite
from widgets import Box, MessageBoard

PHOTO_MULT = 1
WATER_MULT = 1 

# This import pattern, and useage of pygame in this program, is based
# on Eli Bendersky's excellent pygame tutorial (eli.thegreenplace.net)

class Cell(Sprite):
    def __init__(self, world, program, initMemory, type, init_sugar, init_water):
        self.type = type
        self.world = world
        self.program = program
        self.memory = initMemory
        self.set_type_characteristics()
        self.alive = True
        self.starving = False
        self.used_photo = False
        
        "Pygame Stuff"
        Sprite.__init__(self)
        #self.screen = world.screen
        #self.image = "... probably handled by set_type_characteristics"
        
        "RESOURECE INITIALIZATION"
        self.sugar_store = init_sugar
            # Baseline sugar use per turn
        self.sugar_used = self.sugar_consumption 
            # Tracks the total sugar use throughout the cycle to ensure that the cell can't 
            # overextend itself and cheat by sending / expending more resources than it has
        self.sugar_incoming = 0
        self.sugar_sent = 0
            # How much it is receiving from other cells or photosynthesis
        self.water_store = init_water
        self.water_used = 0
        self.water_incoming = 0
        self.water_sent = 0
                
        "MESSAGES"
        self.message = {}
            # A dictionary of messages that other cells can access. Contents defined by 
            # the 'DNA' implementation.
    
    def takeAction(self):self.program()
        
    def __repr__(self):
        return "<" + self.type + str(self.world.coordinates[self]) + ">"

    def set_type_characteristics(self):
        info = TYPES_INFO[self.type]
        self.sugar_consumption = info['S_CONSUMPTION']
        self.sugar_max_xfer = info['S_XFER']
        self.sugar_max_store = info['S_MAX']
        self.water_consumption = info['W_CONSUMPTION']
        self.water_max_xfer = info['W_XFER']
        self.water_max_store = info['W_MAX']
        self.photo_factor = info['PHOTO_FACTOR']
        self.water_factor = info['WATER_FACTOR']

    def update_self_state(self):
        '''Updates a cell's internal characteristics, such as sugar and water stores'''
        self.sugar_store -= self.sugar_used
        self.sugar_store += self.sugar_incoming
        self.sugar_used = self.sugar_consumption
        self.sugar_incoming = 0
        self.sugar_sent = 0
        if self.sugar_store > self.sugar_max_store:
            self.sugar_store = self.sugar_max_store    
            
        self.water_store -= self.water_used
        self.water_store += self.water_incoming
        self.water_store += self.water_factor * self.water * self.free_spaces
        self.water_used = self.water_consumption
        self.water_incoming = 0
        self.water_sent = 0
        if self.water_store > self.water_max_store:
            self.water_store = self.water_max_store
            
        if self.sugar_store < 0 or self.water_store < 0:
            if self.starving:
                self.die()
            else:
                self.starving = True
        self.used_photo = False
        
    def update_world_state(self):
        '''Updates a cell's information about the external environment, such as adjacent cells'''
        # We need to seperate this from update_self_state because a cell may die during the 
        # self_state update, and we don't want dead cells to appear in the adjacency lists
        self.light = self.world.get_light(self)
        self.water = self.world.get_water(self)
        # Get light and water values each cycle because they may change (with the weather)
        self.adjacent = self.world.get_adjacent(self)
        self.free_spaces = self.world.get_free_spaces(self)
        self.adjacentMessages = self.world.get_messages
        
                
    def die(self):
        self.alive = False
        self.kill()
        self.world.remove_cell(self)
        
    def photosynthesize(self):
        if not self.used_photo: 
            amount = self.light * self.free_spaces * self.photo_factor
            self.water_used += amount
            self.sugar_incoming += amount
            self.used_photo = True
        # Currently water converted to sugar at 1:1 ratio.
    
    def divide(self, direction, water_transfer, sugar_transfer, newMemory):
        if self.adjacent[direction] == None:
            avail_sugar = self.sugar_store - self.sugar_used
            avail_water = self.water_store - self.water_used
            sugar_cost, water_cost = COSTS['REPR']
            if avail_sugar >= sugar_transfer + sugar_cost and \
                    avail_water >= water_transfer + water_cost:
                  self.sugar_used += sugar_transfer + sugar_cost
                  self.water_used += water_transfer + water_cost
                  self.world.add_daughter(self, direction, sugar_transfer, water_transfer, newMemory)
                  return 0
        return 1
    
    def specialize(self, new_type):
        if self.type == 'GENERIC':
            sugar_cost, water_cost = SPEC_COSTS[new_type]
            if self.water_store - self.water_used - water_cost > 0 and self.sugar_store - \
                                  self.sugar_used - sugar_cost > 0:
                self.sugar_used += sugar_cost
                self.water_used += water_cost
                self.type = new_type
                self.set_type_characteristics()
                
    def transfer(self, direction, sugar, water):
        if self.adjacent[direction] != None:
            sugar = min(sugar, self.sugar_store - self.sugar_used, self.sugar_max_xfer - self.sugar_sent)
            water = min(water, self.water_store - self.water_used, self.water_max_xfer - self.water_sent)
            # Makes sure that the cell can't send more than its xfer limit, and that it can't
            # reduce its store below 0
            self.sugar_used += sugar
            self.sugar_sent += sugar
            self.water_used += water
            self.water_sent += water
            self.world.transfer(self, direction, sugar, water)


class Environment(object):
    # Game parameters
    SCREEN_WIDTH, SCREEN_HEIGHT = 900, 700
    GRID_SIZE = 20
    FIELD_SIZE = 700, 700
    def __init__(self):
        self.setup_pygame()
        self.cells = {} 
        # A dictionary is used to track cells, in form (coordinate: cell)     
        self.coordinates = {}
        # A dictionary used to track cell coordinates, in form (cell: coordinate)
        # Between the two we have a bijective mapping from cells to coordinates
        self.cycles = 0
        "Initialize a seed cell"
        seedCell = Cell(self, 'SEED', 500, 500)
        self.add_cell(seedCell, (0,-5))
    
    def setup_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (self.SCREEN_WIDTH, 
                      self.SCREEN_HEIGHT), 0, 32)
        self.field_border_width = 4
        field_outer_width  = self.FIELD_SIZE[0] + 2 * self.field_border_width
        field_outer_height = self.FIELD_SIZE[1] + 2 * self.field_border_width
        self.field_rect_outer = Rect(20, 20, field_outer_width, field_outer_height)
        self.field_bgcolor = Color(109, 41, 1, 100)
        self.field_border_color = Color(0, 0, 0)
        self.field_box = Box(self.screen, rect = self.field_rect_outer,
                         bgcolor = self.field_bgcolor,
                         border_width = self.field_border_width,
                         border_color = self.field_border_color)
                         
        self.mboard_text = []
        self.mboard_rect = Rect(500, 60, 120, 60)
        self.mboard_bgcolor = Color(50, 20, 0)
        self.mboard = MessageBoard(self.screen, rect = self.mboard_rect,
                      bgcolor = self.mboard_bgcolor, border_width = 4,
                      border_color = Color('black'),
                      text = self.mboard_text, font = ('verdana', 16),
                      font_color=Color('white'))
        self.clock = pygame.time.Clock()
        self.paused = False
        self.field_rect = self.get_field_rect()
        
        self.grid_nrows = self.FIELD_SIZE[1] / self.GRID_SIZE
        self.grid_ncols = self.FIELD_SIZE[0] / self.GRID_SIZE
        self.options = {'draw_grid': False}
        
    def get_field_rect(self):
        """ Return the internal field rect - the rect of the game
            field exluding its border.
        """
        return self.field_box.get_internal_rect()
    def xy2coord(self, pos):
    
        x, y = (pos[0] - self.field_rect.left, pos[1] - self.field_rect.top)
        return (int(y) / self.GRID_SIZE, int(x) / self.GRID_SIZE)
    
#     def coord2xy_mid(self, coord):
#         nrow, ncol = coord
#         return (
#             self.field_rect.left + ncol * self.GRID_SIZE 

    def draw_grid(self):
        for y in range(self.grid_nrows +1):
            pygame.draw.line(
                self.screen,
                Color(50, 50, 50),
                (self.field_rect.left, self.field_rect.top + y * self.GRID_SIZE - 1),
                (self.field_rect.right - 1, self.field_rect.top + y * self.GRID_SIZE -1))
        
        for x in range(self.grid_ncols + 1):
            pygame.draw.line(
                self.screen,
                Color(50, 50, 50),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.top),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.bottom - 1))
                
    def draw(self):
        self.field_box.draw()
        self.draw_grid()
        self.mboard.text = "h"
        self.mboard.draw()
                        
        
    def add_cell(self, cell, coordinate):
        if coordinate in self.cells:
            print "Warning: A cell already exists at coordinate {0}".format(coordinate)
            # Raise an error later
        elif cell in self.coordinates:
            print "Warning: Cell already exists in coordinate map."
            # Raise an error later
        else:
            self.cells[coordinate] = cell
            self.coordinates[cell] = coordinate
            cell.update_world_state()
        
    def get_water(self, cell):
        x,y = self.coordinates[cell]
        if y>0: return 0
        else: return y**2
        
    def get_light(self, cell):
        c, r = self.coordinates[cell]
        if r<0: return 0
        else: return r**(1.5)
        
    def get_adjacent(self, cell):
        c, r = self.coordinates[cell]
        adjacencies = {}
        adjacent_coords = {'UP': (c, r+1), 'RIGHT': (c+1, r), 'DOWN': (c, r-1), 'LEFT': (c-1, r)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.coordinates:
                adjacencies[direction] = self.coordinates[coord].type
            else:
                adjacencies[direction] = None
        return adjacencies
        
    def get_free_spaces(self, cell):
        c,r = self.coordinates[cell]
        spaces = 0
        adjacent_coords = ( (c, r+1), (c+1, r), (c, r-1), (c-1, r) )
        for coord in adjacent_coords:
            if coord not in self.coordinates:
                spaces += 1
        return spaces
        
    def get_messages(self, cell):
        c, r = self.coordinates[cell]
        messages = {}
        adjacent_coords = {'UP': (c, r+1), 'RIGHT': (c+1, r), 'DOWN': (c, r-1), 'LEFT': (c-1, r)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.coordinates:
                messages[direction] = self.coordinates[coord].message
            else:
                adjacencies[direction] = None
        return messages
        
    def add_daughter(self, cell, direction, init_sugar, init_water, newMemory={}):
        c, r = self.coordinates[cell]
        adjacent_coords = {'UP': (c, r+1), 'RIGHT': (c+1, r), 'DOWN': (c, r-1), 'LEFT': (c-1, r)}
        coordinate = adjacent_coords[direction]
        program = cell.program
        if coordinate not in self.coordinates:
            newCell = Cell(self, program, 'GENERIC', init_sugar, init_water, newMemory)
            self.add_cell(newCell, coordinate)
    
    def transfer(self, cell, direction, sugar, water):
        c, r = self.coordinates[cell]
        adjacent_coords = {'UP': (c, r+1), 'RIGHT': (c+1, r), 'DOWN': (c, r-1), 'LEFT': (c-1, r)}
        coordinate = adjacent_coords[direction]
        if coordinate in self.cells:
            target = self.cells[coordinate]
            target.sugar_incoming += sugar
            target.water_incoming += water
        else: print "Warning: Bad transfer to coordinate " + str(coordinate)
        
    def remove_cell(self, cell):
        coordinate = self.coordinates[cell]
        del self.coordinates[cell]
        del self.cells[coordinate]
        
    def update_cells(self):
        self.cycles += 1
        for cell in self.coordinates.copy():
            cell.takeAction()
        # The coordinates dict is index by cells, so if we ignore the values, it's a bit like
        # accessing a list
        for cell in self.coordinates.copy(): 
            cell.update_self_state()
            # This might remove cells due to death, so we iterate over a copy
        
        for cell in self.coordinates:
            cell.update_world_state()
            # No risk of cell removal at this point, they are just updating their global info    


        
#For testing purposes...

world = Environment()
c1 = world.cells[(0,-5)]
c1.divide('DOWN', 200, 200)
