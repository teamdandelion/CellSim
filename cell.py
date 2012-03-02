PHOTO_MULT = 1
WATER_MULT = 1 

from cell_types import COSTS, TYPES_INFO
from random import randint

import pygame
from pygame import Rect, Color
from pygame.sprite import Sprite
# This import pattern, and useage of pygame in this program, is based
# on Eli Bendersky's excellent pygame tutorial (eli.thegreenplace.net)

class Cell(object):
    def __init__(self, world, type, init_sugar, init_water):
        self.type = type        
        self.set_type_characteristics()
        self.world = world
        self.alive = True
        self.starving = False
        self.used_photo = False
        
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
        self.world.remove_cell(self)
        
    def photosynthesize(self):
        if not self.used_photo: 
            amount = self.light * self.free_spaces * self.photo_factor
            self.water_used += amount
            self.sugar_incoming += amount
            self.used_photo = True
        # Currently water converted to sugar at 1:1 ratio.
    
    def divide(self, direction, water_transfer, sugar_transfer):
        if self.adjacent[direction] == None:
            avail_sugar = self.sugar_store - self.sugar_used
            avail_water = self.water_store - self.water_used
            sugar_cost, water_cost = COSTS['REPR']
            if avail_sugar >= sugar_transfer + sugar_cost and \
                    avail_water >= water_transfer + water_cost:
                  self.sugar_used += sugar_transfer + sugar_cost
                  self.water_used += water_transfer + water_cost
                  self.world.add_daughter(self, direction, sugar_transfer, water_transfer)
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
    def __init__(self):
        self.cells = {} 
        # A dictionary is used to track cells, in form (coordinate: cell)     
        self.coordinates = {}
        # A dictionary used to track cell coordinates, in form (cell: coordinate)
        # Between the two we have a bijective mapping from cells to coordinates
        self.cycles = 0
        "Initialize a seed cell"
        seedCell = Cell(self, 'SEED', 500, 500)
        self.add_cell(seedCell, (0,-5))
        
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
        x,y = self.coordinates[cell]
        if y<0: return 0
        else: return y**(1.5)
        
    def get_adjacent(self, cell):
        x,y = self.coordinates[cell]
        adjacencies = {}
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.coordinates:
                adjacencies[direction] = self.coordinates[coord].type
            else:
                adjacencies[direction] = None
        return adjacencies
        
    def get_free_spaces(self, cell):
        x,y = self.coordinates[cell]
        spaces = 0
        adjacent_coords = ( (x,y+1), (x+1,y), (x, y-1), (x-1, y) )
        for coord in adjacent_coords:
            if coord not in self.coordinates:
                spaces += 1
        return spaces
        
    def get_messages(self, cell):
        x,y = self.coordinates[cell]
        messages = {}
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        for direction, coord in adjacent_coords.iteritems():
            if coord in self.coordinates:
                messages[direction] = self.coordinates[coord].message
            else:
                adjacencies[direction] = None
        return messages
        
    def add_daughter(self, cell, direction, init_sugar, init_water):
        x,y = self.coordinates[cell]
        adjacent_coords = {'UP': (x, y+1), 'RIGHT': (x+1, y), 'DOWN': (x, y-1), 'LEFT': (x-1, y)}
        coordinate = adjacent_coords[direction]
        if coordinate not in self.coordinates:
            newCell = Cell(self, 'GENERIC', init_sugar, init_water)
            self.add_cell(newCell, coordinate)
    
    def transfer(self, cell, direction, sugar, water):
        x,y = self.coordinates[cell]
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
        
    def update_cells(self):
        self.cycles += 1
        # Once a program is written for managing a cell (e.g. the grass program)
        # Add an action loophere
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
