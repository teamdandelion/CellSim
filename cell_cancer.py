#!/usr/bin/env python
import os, sys

from cell_types import COSTS, TYPES_INFO
from dna_cancer import dna_grass
from random import randint
from pdb import set_trace as debug

import pygame
from pygame import Rect, Color

PHOTO_MULT = 1
WATER_MULT = 1 

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
FIELD_WIDTH, FIELD_HEIGHT = 600, 600
FIELD_RECT = Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
MESSAGE_RECT = Rect(FIELD_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
GRID_SIZE = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

def adjacent_coords(x, y, dir=None):
        adjacent = {'N': (x, y+1), 'NE': (x+1, y+1), 'E': (x+1, y), 'SE': (x+1, y-1), 'S': (x, y-1), 'SW': (x-1, y-1), 'W': (x-1, y), 'NW': (x-1, y+1)}
        if (dir != None):
            return adjacent[dir]
        else:
            return adjacent

class Cell:
    """Represents a single cell, with a type, resources, functions that represent possible actions, a memory, and a program that animates it"""
    def __init__(self, world, program, initMemory, type, init_sugar, init_water):
        self.world = world
        self.program = program
        
        self.type = type
        self.set_type_characteristics()
        self.debug = []
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
        if self.world == None:
            return "<Empty Cell>"
        else: 
            try:
                return "<" + self.type + str(self.world.coordinates[self]) + ">"
            except (AttributeError, KeyError):
                return "<DEAD>"
            

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
        self.water += self.h2o * self.water_factor
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
        self.light = self.world.get_light(self)
        self.h2o = self.world.get_water(self)
        # Get light and water values each cycle because they may change (with the weather)
        self.adjacent = self.world.get_adjacent(self)
        self.free_spaces = self.world.get_free_spaces(self)
                
    def die(self):
        """Kills the cell. Useful to make space"""
        self.alive = False
        self.world.remove_cell(self)
        
    def photosynthesize(self):
        """Converts water into sugar, if the cell is photosynthetic and there's light and free adjacent spaces"""
        if not self.used_photo: 
            amount = self.light * self.free_spaces * self.photo_factor * 3
            self.water -= amount
            self.sugar += amount * 2
            self.used_photo = True
            self.debug.append('Used photo: generated {0} sugar'.format(amount*2))
        # Currently water converted to sugar at 2:1 ratio.
    
    def divide(self, direction, sugar_transfer, water_transfer, newMemory={}):
        """Spawn a daughter cell in the given direction. 
        
        New cell starts with specified sugar and water, and memory initialized to newMemory. Note division has additional costs (specified in cell_types.py as COSTS['GENERIC']). 
        If the cell doesn't have enough water or sugar for the division, then division will fail but resources will not be lost.
        """
        sugar_transfer = max(0, sugar_transfer)
        water_transfer = max(0, water_transfer)
        if self.adjacent[direction] == 'EMPTY':
            sugar_cost, water_cost = COSTS['GENERIC']
            if self.sugar >= sugar_transfer + sugar_cost and \
                    self.water >= water_transfer + water_cost:
                  self.sugar -= sugar_transfer + sugar_cost
                  self.water -= water_transfer + water_cost
                  return self.world.add_daughter(self, direction, sugar_transfer, water_transfer, newMemory)
                  
        else:  
            print "Warning: Bad division!!!"
            debug()
            return 'EMPTY'
    
    def specialize(self, new_type):
        """Cells can specialize into a new type of cell."""
        sugar_cost, water_cost = COSTS[new_type]
        if self.water >= water_cost and self.sugar >= sugar_cost:
            self.sugar -= sugar_cost
            self.water -= water_cost
            self.type = new_type
            self.set_type_characteristics()
            self.world.update_cell(self)
                
    def transfer(self, direction, sugar, water):
        """Transfer sugar and/or water in given direction. 
        
        Limited by sugar, water available, the maximum transfer limits. If there is no cell in the given direction or that cell is already overloaded, then resources will be wasted.
        
        NOTE: Transfer limits currently disabled.
        """
        sugar = max(sugar, 0)
        water = max(water, 0)
        if self.adjacent[direction] != 'EMPTY':
            sugar = min(sugar, self.sugar)
            water = min(water, self.water)
            # Makes sure that the cell can't send more than its xfer limit, and that it can't
            # reduce its store below 0
            self.sugar -= sugar
            self.water -= water
            self.sugar_sent += sugar
            self.water_sent += water
            self.world.transfer(self, direction, sugar, water)
        else:
            print "Tried to transfer to empty coordinate."

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
        self.initiate_graphics(screen)

        
    def add_cell(self, cell, coordinate):
        """Adds given cell to the world at given coordinate. 
        
        Includes cell in list of cells that need to be drawn. Prints a warning and fails if a cell already exists at that coordinate, or if the given cell already exists on the map.
        """
        if coordinate in self.cells:
            print "Warning: A cell already exists at coordinate {0}".format(coordinate)
            
        elif cell in self.coordinates:
            print "Warning: Cell already exists in coordinate map."
            
        else:
            self.cells[coordinate] = cell
            self.coordinates[cell] = coordinate
            cell.update_world_state() # Gives the cell adjacency list, etc
            self.toDraw.append((coordinate, cell.color))
        
    def get_water(self, cell):
        """Returns the water density at a cell's location"""
        x,y = self.coordinates[cell]
        if y > 0: return 0
        else: return -y + 5
        
    def get_light(self, cell):
        """Returns the light intensity at a cell's location"""
        x,y = self.coordinates[cell]
        if y < 0: return 0
        else: return 1
        
    def get_adjacent(self, cell):
        """Returns a dictionary of cells adjacent to the given cell."""
        x,y = self.coordinates[cell]
        adjacencies = {}
        for direction, coord in adjacent_coords(x,y).iteritems():
            if coord in self.cells: # self.cells is indexed by coordinates
                adjacencies[direction] = self.cells[coord]
            else:
                adjacencies[direction] = 'EMPTY'
        return adjacencies
        
    def get_free_spaces(self, cell):
        x,y = self.coordinates[cell]
        spaces = 0
        for coord in adjacent_coords(x,y).itervalues():
            if coord not in self.cells:
                spaces += 1
        return spaces

    def add_daughter(self, cell, direction, init_sugar, init_water, newMemory={}):
        x, y = self.coordinates[cell]
        coordinate = adjacent_coords(x, y, direction)
        program = cell.program
        
        if coordinate not in self.coordinates:
            newCell = Cell(self, program, newMemory, 'GENERIC', init_sugar, init_water)
            self.add_cell(newCell, coordinate)
            for adjcell in self.get_adjacent(newCell).itervalues():
                if adjcell != 'EMPTY':
                    adjcell.update_world_state()
            return newCell
        else:
            return 'EMPTY'
            
    def transfer(self, cell, direction, sugar, water):
        if sugar > 0 or water > 0:
            x, y = self.coordinates[cell]
            coordinate = adjacent_coords(x, y, direction)
            if coordinate in self.cells:
                target = self.cells[coordinate]
                target.sugar_incoming += sugar
                target.water_incoming += water
                target.debug.append('Recieved {0}, {1} from {2}'.format(sugar, water, cell))
                cell.debug.append('Sent {0}, {1}, to {2}'.format(sugar, water, target))
            else: print "Warning: Bad transfer to coordinate " + str(coordinate)
        
    def remove_cell(self, cell):
        coordinate = self.coordinates[cell]
        if self.selected_cell == cell:
            self.selected_cell = None
        if cell.h2o > 0: color = self.ground_color
        else: color = self.sky_color
        self.toDraw.append((coordinate, color))
            
        del self.coordinates[cell]
        del self.cells[coordinate]
        for adjcell in cell.adjacent.itervalues():
            if adjcell != 'EMPTY':
                adjcell.update_world_state()
        
    def update_cells(self):
        self.cycles += 1
        for cell in self.coordinates.copy():
            cell.debug = []
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
    def initiate_graphics(self, screen):
        self.screen = screen
        self.selected_cell = None
        self.sky_color = (0, 191, 255)
        self.ground_color = (139, 69, 19)
        self.u_offset = 0
        self.v_offset = 0
        self.x_axis = 380 # AKA ground level
        self.y_axis = 300
        self.toDraw = []
        self.drawBackground()

    def c2p(self, coordinate):
        """Converts a cell coordinate into a pixel coordinate
        
        Specifically, returns the pixel coordinate designating the upper left-hand coordinate of the given cell.
        """
        x, y = coordinate
        minU = self.y_axis + (x * GRID_SIZE)
        minV = self.x_axis - ((y+1) * GRID_SIZE)
        return (minU, minV)
        
    def p2c(self, pixel):
        """Translate a pixel coordinate to a cell coordinate. Reverse of c2p"""
        u,v = pixel
        x = (u - self.y_axis) // GRID_SIZE
        y = -(v - self.x_axis) // GRID_SIZE
        return (x,y)
     
    def color_grid(self, coordinate, color):
        """Colors a given coordinate (GRID_SIZE x GRID_SIZE square)"""
        u,v = self.c2p(coordinate)
        rect = (u, v, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect)
    
    def updateDisplay(self):
        for (coordinate, color) in self.toDraw:
            self.color_grid(coordinate, color)
        self.toDraw = []

    def update_cell(self, cell):
        self.toDraw.append((self.coordinates[cell], cell.color))
    
    def drawBackground(self):
        """Draws background over coordinate space designated"""
        
        sky_rect = (0, 0, SCREEN_WIDTH, self.x_axis)
        ground_rect = (0, self.x_axis, SCREEN_WIDTH, SCREEN_HEIGHT - self.x_axis)
        pygame.draw.rect(screen, self.sky_color, sky_rect)
        pygame.draw.rect(screen, self.ground_color, ground_rect)
        
    def drawCell(self, cell, corner):
        minU, minV = corner
        if minU + GRID_SIZE < SCREEN_WIDTH and minV + GRID_SIZE < SCREEN_HEIGHT:
            for u in xrange(GRID_SIZE):
                for v in xrange(GRID_SIZE):
                    self.screen.set_at((u+minU, minV-v), cell.color)
                
    def draw_messageboard(self, screen, rect):
        box_color = (50, 20, 0)
        pygame.draw.rect(screen, box_color, rect)
        my_font = pygame.font.SysFont('arial', 15)
        big_font = pygame.font.SysFont('arial', 25)
        cell = self.selected_cell
        
        messages = []
        cyclecount = "Cycles: " + str(self.cycles)
        cyclecount_sf = big_font.render(cyclecount, True, Color('white'))
        
        if cell == None:
            messages.append("No cell selected.")
        else:
            messages.append(repr(cell))
            messages.append("Sugar: " + str(cell.sugar))
            messages.append("Water: " + str(cell.water))
            messages.append("Light: " + str(cell.light))
            messages.append("H20 Density: " + str(cell.h2o))
            for key, val in cell.memory.iteritems():
                messages.append(key + " : " + str(val))
            
            messages.append("-----------")
            for message in cell.debug:
                messages.append(message)
                
        messages_sf = []
        for message in messages:
            messages_sf.append(my_font.render(message, True, Color('white')))
        
        offset = 0
        for message in messages_sf:
            screen.blit(message, rect.move(15, offset))
            offset += message.get_height()

        screen.blit(cyclecount_sf, rect.move(15, 500))
        
    def change_selected_cell(self, pixel):
        """Takes the pixel coordinate of a mouse click, and changes selected cell to match the object at that location."""
        x,y = self.p2c(pixel)
        print str((x,y)), str(pixel)
        if (x,y) in self.cells:
            self.selected_cell = self.cells[(x,y)]
        else:
            self.selected_cell = None

#For testing purposes...
world = Environment(screen)
pygame.init()
seed_cell = Cell(world, dna_grass, {'role':'origin'}, 'STORE', 1000, 500)
world.add_cell(seed_cell, (0, -2))
world.draw_messageboard(screen, MESSAGE_RECT)
world.updateDisplay()
pygame.display.flip()
autoRunning = False
tick_amount = 500
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                world.update_cells()
                world.draw_messageboard(screen, MESSAGE_RECT)
                pygame.display.flip()
            if event.key == pygame.K_x:
                debug()
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_g:
                if autoRunning:
                    tick_amount = 500
                else:
                    tick_amount = 6
                autoRunning = not(autoRunning)
        elif (  event.type == pygame.MOUSEBUTTONDOWN and
                pygame.mouse.get_pressed()[0]):
            world.change_selected_cell(pygame.mouse.get_pos())
            world.draw_messageboard(screen, MESSAGE_RECT)
            pygame.display.flip()
            
    if autoRunning:
        world.update_cells()
        world.draw_messageboard(screen, MESSAGE_RECT)
        pygame.display.flip()
        
    clock.tick(tick_amount)
    