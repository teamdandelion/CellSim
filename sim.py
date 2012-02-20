PHOTO_FACTOR = 1
WATER_FACTOR = 1 
COST_REPR_SUGAR = 10
COST_REPR_WATER = 10


class Cell:
    def __init__(self, coordinate, init_sugar, init_water):
        self.coordinate = coordinate       
        self.type = 'GENERIC'
        self.alive = True
        self.starving = False
        self.photo_ready = True
        
        self.photo_factor = 0
        self.water_factor = 0

        "SUGAR"
        self.sugar_store = init_sugar
        self.sugar_consumption = 1
        self.sugar_max_xfer = 20
        self.sugar_max_store = 100
        self.sugar_used = 0
        self.sugar_incoming = 0
        "WATER"
        self.water_store = init_water
        self.water_consumption = 0
        self.water_max_xfer = 20
        self.water_max_store = 100
        self.water_used = 0
        self.water_incoming = 0
        
        "LOCATION"
        xC, yC = self.coordinate
        self.adj_cords = {'u': (xC, yC+1), 'r': (xC+1, yC), 
                          'd': (xC, yC-1), 'l': (xC-1, yC)}
        self.light = WORLD.get_light(self.coordinate)
        self.water = WORLD.get_water(self.coordinate)
        self.adjacenct = WORLD.get_adjacent(self.coordinate)
        self.free_spaces = WORLD.get_free_spaces(self.coordinate)
        
        "self.water_delta += self.water * len(self.free_spaces) * WATER_FACTOR"
        
        "MESSAGES"
        self.messages = {}
        

    def update(self):
        self.sugar_store -= self.sugar_used
        self.sugar_store += self.sugar_incoming
        self.sugar_store -= self.sugar_consumption
        self.sugar_used = 0
        self.sugar_incoming = 0
        if self.sugar_store > self.sugar_max_store:
            self.sugar_store = self.sugar_max_store    
            
        self.water_store -= self.water_used
        self.water_store += self.water_incoming
        self.water_store -= self.water_consumption
        self.water_store += self.water_factor * self.water * \
                                            self.free_spaces
        self.water_used = 0
        self.water_incoming = 0
        if self.water_store > self.water_max_store:
            self.water_store = self.water_max_store
            
        if self.sugar_store < 0 or self.water_store < 0:
            if self.starving:
                self.die()
            else:
                self.starving = True
        self.photo_ready = True
        self.light = WORLD.get_light(self.coordinate)
        self.water = WORLD.get_water(self.coordinate)
        self.adjacenct = WORLD.get_adjacent(self.coordinate)
        self.free_spaces = WORLD.get_free_spaces(self.coordinate)
                
    def die(self):
        self.alive = False
        WORLD.remove_cell(self.coordinate)
        
    def photosynthesize(self):
        if self.photo_ready: 
            amount = self.light * len(self.free_spaces) * self.photo_factor
            self.water_used += amount
            self.sugar_incoming += amount
            self.photo_ready = False
        # Currently water converted to sugar at 1:1 ratio.
    
    def divide(self, coordinate, water_transfer, sugar_transfer):
        if coord in self.free_spaces:
            avail_sugar = self.sugar_store - self.sugar_used
            avail_water = self.water_store - self.water_used
            if avail_sugar > sugar_transfer + COST_REPR_SUGAR and \
                    avail_water > water_transfer + COST_REPR_SUGAR:
                  self.sugar_used += sugar_transfer + COST_REPR_SUGAR
                  self.water_used += water_transfer + COST_REPR_WATER
                  WORLD.add_cell(coord, sugar_transfer, water_transfer)
                  return 1
        return 0
    
    def specialize(self, type):
        if self.type = 'GENERIC':
            
class RootCell(Cell):
    def __init__(self, coordinate, 


class Environment:
    def __init__(self):
        self.cells = [] "Initialize a seed cell"
    
    def get_water(self, coordinate):
    def get_light(self, coordinate):
    def get_adjacent(self, coordinate):
    def get_free_space(self, coordinate):
    def add_cell(self, coordinate, init_sugar, init_water)
    def remove_cell(self, coordinate)
        
