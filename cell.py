#!/usr/bin/env python
import os, sys

from cell_types import COSTS, TYPES_INFO
from cell_programs import grass
from random import randint
from pdb import set_trace as debug

import pygame
from pygame import Rect, Color

PHOTO_MULT = 1
WATER_MULT = 1 

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FIELD_WIDTH, FIELD_HEIGHT = 600, 600
FIELD_RECT = Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
MESSAGE_RECT = Rect(600, 0, 800, 600)
GRID_SIZE = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

class Cell:
    """Represents a single cell, with a type, resources, functions that represent possible actions, a memory, and a program that animates it"""
    def __init__(self, world, program, initMemory, type, init_sugar, init_water):
        self.world = world
        self.program = program
        
        self.type = type
        self.set_type_characteristics()

        self.memory = initMemory
        # The cell's internal memory. Can be accessed by other cells
        self.alive = True
        self.starving = False
        self.used_photo = False
        
        "RESOURECE INITIALIZATION"
        self.sugar = init_sugar
        # Amount of sugar the cell has. A critical resource
        self.sugar_incoming = 0
        # Keeps track of how much sugar the cell will recieve at the start of the next cycle. I recommend not using this variable in DNA programs since it depends on the order in which the environment does cell actions
        self.sugar_sent = 0
        # Keeps track of how much sugar the cell has sent to other cells, so that it does not exceed its max transfer limit.  
        self.water = init_water
        self.water_incoming = 0
        self.water_sent = 0

    def __repr__(self):
        """Just makes it a bit easier to see what's going on..."""
        return "<" + self.type + str(self.world.coordinates[self]) + ">"

    def set_type_characteristics(self):
        """Uses the info from cell_types.py to set the cell characteristics"""
        info = TYPES_INFO[self.type]
        self.sugar_consumption = info['S_CONSUMPTION']
        self.sugar_max_xfer = info['S_XFER']
        self.sugar_max = info['S_MAX']
        self.water_consumption = info['W_CONSUMPTION']
        self.water_max_xfer = info['W_XFER']
        self.water_max = info['W_MAX']
        self.photo_factor = info['PHOTO_FACTOR']
        self.water_factor = info['WATER_FACTOR']
        self.color = info['COLOR']

    def update_self_state(self):
        """Updates internal characteristics, such as sugar and water stores"""
        self.sugar += self.sugar_incoming
        self.sugar_incoming = 0
        self.sugar_sent = 0
        self.sugar -= self.sugar_consumption
        if self.sugar > self.sugar_max:
            self.sugar = self.sugar_max      
        
        self.water += self.water_incoming
        self.water_incoming = 0
        self.water_sent = 0
        self.water -= self.water_consumption
        if self.water > self.water_max:
            self.water = self.water_max  

        if self.sugar < 0 or self.water < 0:
            if self.starving:
                self.die()
            else:
                self.starving = True
        self.used_photo = False
        
    def update_world_state(self):
        """Updates a cell's information about the external environment, such as adjacent cells"""
        # We need to seperate this from update_self_state because a cell may die during the self_state update, and we don't want dead cells to appear in the adjacency lists
        self.light_intensity = self.world.get_light(self)
        self.water_intensity = self.world.get_water(self)
        # Get light and water values each cycle because they may change (with the weather)
        self.adjacent = self.world.get_adjacent(self)
        self.free_spaces = self.world.get_free_spaces(self)
        self.adjacentMessages = self.world.get_messages
                
    def die(self):
        """Kills the cell. Useful to make space"""
        self.alive = False
        self.world.remove_cell(self)
        
    def photosynthesize(self):
        """Converts water into sugar, if the cell is photosynthetic and there's light and free adjacent spaces"""
        if not self.used_photo: 
            amount = self.light_intensity * self.free_spaces * self.photo_factor
            self.water -= amount
            self.sugar += amount
            self.used_photo = True
        # Currently water converted to sugar at 1:1 ratio.
    
    def divide(self, direction, sugar_transfer, water_transfer, newMemory={}):
        """Spawn a daughter cell in the given direction. 
        
        New cell starts with specified sugar and water, and memory initialized to newMemory. Note division has additional costs (specified in cell_types.py as COSTS['REPR']). 
        If the cell doesn't have enough water or sugar for the division, then division will fail but resources will not be lost.
        """
        if self.adjacent[direction] == 'EMPTY':
            sugar_cost, water_cost = COSTS['REPR']
            if self.sugar >= sugar_transfer + sugar_cost and \
                    self.water >= water_transfer + water_cost:
                  self.sugar -= sugar_transfer + sugar_cost
                  self.water -= water_transfer + water_cost
                  self.world.add_daughter(self, direction, sugar_transfer, water_transfer, newMemory)
                  return 0
        return 1
    
    def specialize(self, new_type):
        """Generic cells can specialize into a new type of cell."""
        if self.type == 'GENERIC':
            sugar_cost, water_cost = SPEC_COSTS[new_type]
            if self.water > water_cost and self.sugar > sugar_cost:
                self.sugar -= sugar_cost
                self.water -= water_cost
                self.type = new_type
                self.set_type_characteristics()
                
    def transfer(self, direction, sugar, water):
        """Transfer sugar and/or water in given direction. 
        
        Limited by sugar, water available, the maximum transfer limits. If there is no cell in the given direction or that cell is already overloaded, then resources will be wasted.
        """
        if self.adjacent[direction] != 'EMPTY':
            sugar = min(sugar, self.sugar, self.sugar_max_xfer - self.sugar_sent)
            water = min(water, self.water, self.water_max_xfer - self.water_sent)
            # Makes sure that the cell can't send more than its xfer limit, and that it can't
            # reduce its store below 0
            self.sugar -= sugar
            self.water -= water
            self.sugar_sent += sugar
            self.water_sent += water
            self.world.transfer(self, direction, sugar, water)

"""===================================================================="""

class Environment:
    def __init__(self, screen):
        self.cells = {} 
        # A dictionary is used to track cells, in form (coordinate: cell)     
        self.coordinates = {}
        # A dictionary used to track cell coordinates, in form (cell: coordinate)
        # Between the two we have a bijective mapping from cells to coordinates
        self.cycles = 0
        # Keep track of the number of cycles that have passed
        self.toDraw = [] # A list of cells that need to be drawn or updated on the screen
        self.screen = screen
        self.selected_cell = None
        
    def add_cell(self, cell, coordinate):
        """Adds given cell to the world at given coordinate. 
        
        Includes cell in list of cells that need to be drawn. Prints a warning and fails if a cell already exists at that coordinate, or if the given cell already exists on the map.
        """
        if coordinate in self.cells:
            print "Warning: A cell already exists at coordinate {0}".format(coordinate)
            #debug()
        elif cell in self.coordinates:
            print "Warning: Cell already exists in coordinate map."
            #debug()
        else:
            self.cells[coordinate] = cell
            self.coordinates[cell] = coordinate
            cell.update_world_state() # Gives the cell adjacency list, etc
            self.toDraw.append((cell, coordinate))
        
    def get_water(self, cell):
        """Returns the water density at a cell's location"""
        x,y = self.coordinates[cell]
        if y > 0: return 0
        else: return -y
        
    def get_light(self, cell):
        """Returns the light intensity at a cell's location"""
        x,y = self.coordinates[cell]
        if y < 0: return 0
        else: return y 
        
    def get_adjacent(self, cell):
        """Returns a dictionary of cells adjacent to the given cell."""
        x,y = self.coordinates[cell]
        adjacencies = {}
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.cells: # self.cells is indexed by coordinates
                adjacencies[direction] = self.cells[coord].type
            else:
                adjacencies[direction] = 'EMPTY'
        return adjacencies
        
    def get_free_spaces(self, cell):
        x,y = self.coordinates[cell]
        spaces = 0
        adjacent_coords = ((x, y+1), (x+1, y), (x, y-1), (x-1, y))
        for coord in adjacent_coords:
            if coord not in self.coordinates:
                spaces += 1
        return spaces
        
    def get_messages(self, cell):
        x, y = self.coordinates[cell]
        messages = {}
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.coordinates:
                messages[direction] = self.coordinates[coord].message
            else:
                adjacencies[direction] = None
        return messages
        
    def add_daughter(self, cell, direction, init_sugar, init_water, newMemory={}):
        x, y = self.coordinates[cell]
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        coordinate = adjacent_coords[direction]
        program = cell.program
        
        if coordinate not in self.coordinates:
            newCell = Cell(self, program, newMemory, 'GENERIC', init_sugar, init_water)
            self.add_cell(newCell, coordinate)
            
    def transfer(self, cell, direction, sugar, water):
        x, y = self.coordinates[cell]
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
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
        "Include something to remove dead cells from display."
        
    def update_cells(self):
        self.cycles += 1
        for cell in self.coordinates.copy():
            cell.program(cell)
        # The coordinates dict is index by cells, so if we ignore the values, it's a bit like accessing a list
        # Iterate over a copy because a cell could die
        for cell in self.coordinates.copy(): 
            cell.update_self_state()
            # This might remove cells due to death, so we iterate over a copy
        for cell in self.coordinates:
            cell.update_world_state()
            # No risk of cell removal at this point, they are just updating their global info    
        self.updateDisplay()
        
    """Graphics functionality"""
    def drawAllCells(self):
        for coordinate, cell in self.coordinates.iteritems():
            self.drawCell(cell, self.c2b(coordinate))
    
    def updateDisplay(self):
        for cell, coordinate in self.toDraw:
            self.drawCell(cell, self.c2b(coordinate))
        self.toDraw = []
    
    def drawBackground(self):
        """Draws background over coordinate space designated"""
        pass
    
    def c2b(self, coordinate):
        """Converts a coordinate within self.XBounds, self.YBounds into 
            bounds for drawing on the screen"""
        x, y = coordinate
        minU = FIELD_WIDTH  / 2 + (x * GRID_SIZE)
        minV = FIELD_HEIGHT / 2 + (y * GRID_SIZE)
        return (minU, minV)
        
    def drawCell(self, cell, corner):
        minU, minV = corner
        for u in xrange(GRID_SIZE):
            for v in xrange(GRID_SIZE):
                self.screen.set_at((u+minU, v+minV), cell.color)
                
    def draw_messageboard(self, screen, rect):
        box_color = (50, 20, 0)
        pygame.draw.rect(screen, box_color, rect)
        my_font = pygame.font.SysFont('arial', 10)
        cell = self.selected_cell
        
        messages = []
        message0 = "Cycles: " + str(self.cycles)
        message1 = "(Select a cell)"
        message2 = "Sugar: "
        message3 = "Water: "
        message4 = "Memory: \n"

        if cell != None:
            message1 = repr(cell)
            message2 += str(cell.sugar)
            message3 += str(cell.water)
            for key, val in cell.memory.iteritems():
                message4 += key + " : " + val + "\n"
                
        messages = [message0, message1, message2, message3, message4]

        message0_sf = my_font.render(message0, True, Color('white'))
        message1_sf = my_font.render(message1, True, Color('white'))
        message2_sf = my_font.render(message2, True, Color('white'))
        message3_sf = my_font.render(message3, True, Color('white'))
        message4_sf = my_font.render(message4, True, Color('white'))
        
        messages_sf = []
        for message in messages:
            messages_sf.append(my_font.render(message, True, Color('white')))
        
        offset = 0
        for message in messages_sf:
            screen.blit(message, rect.move(0, offset))
            offset += message.get_height()
        
#         screen.blit(message0_sf, rect)
#         screen.blit(message1_sf, rect.move(0, message0_sf.get_height()))
#         screen.blit(message2_sf, rect.move(0, message1_sf.get_height()))
#         screen.blit(message3_sf, rect.move(0, message2_sf.get_height()))
#         screen.blit(message4_sf, rect.move(0, message3_sf.get_height()))

#For testing purposes...
world = Environment(screen)
pygame.init()
seed_cell = Cell(world, grass, {'role':'origin'}, 'STORE', 500, 500)
world.add_cell(seed_cell, (0, -5))
world.selected_cell = seed_cell
world.draw_messageboard(screen, MESSAGE_RECT)

world.updateDisplay()

#debug()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                world.update_cells()
                world.draw_messageboard(screen, MESSAGE_RECT)
                pygame.display.flip()

    clock.tick(240)
    #debug()