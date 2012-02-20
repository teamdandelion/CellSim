PHOTO_FACTOR = 1
WATER_FACTOR = 1 
COST_REPR_SUGAR = 10
COST_REPR_WATER = 10


class Cell:
    def __init__(self, coordinate):
        self.coordinate = coordinate       
        self.type = 'generic'
        self.alive = True
        self.starving = False
        self.photosynthesizer = False 
        self.photo_available = False
        #self.photo_available is used to restrict photosynthesizers
        #to one photosynthesis per cycle
        "SUGAR"
        self.sugar_store = 10
        self.sugar_consumption = 1
        self.sugar_max_xfer = 0
        self.sugar_max_store = 100
        self.sugar_delta = 0
        "WATER"
        self.water_store = 0
        self.water_consumption = 0
        self.water_max_xfer = 0
        self.water_max_store = 100
        self.water_delta = 0
        
        "LOCATION"
        xC, yC = self.coordinate
        self.adj_cords = {'u': (xC, yC+1), 'r': (xC+1, yC), 
                          'd': (xC, yC-1), 'l': (xC-1, yC)}
        self.light = world.get_light(self.coordinate)
        self.water = world.get_water(self.coordinate)
        self.adjacenct = world.get_adjacent(self.coordinate)
        self.free_spaces = world.get_free_spaces(self.coordinate)
        
        self.water_delta += self.water * len(self.free_spaces) * WATER_FACTOR
        
        "MESSAGES"
        self.messages = {}
        

    def update(self):
        self.sugar_store += self.sugar_delta
        self.sugar_store -= self.sugar_consumption
        if self.sugar_store > self.sugar_max_store:
            self.sugar_store = self.sugar_max_store    
        self.water_store += self.water_delta
        self.water_store -= self.water_consumption
        if self.water_store > self.water_max_store:
            self.water_store = self.water_max_store
        if self.sugar_store < 0 or self.water_store < 0:
            if self.starving:
                self.die()
            else:
                self.starving = True
        if self.photosynthesizer:
            self.photo_available = True
                
    def die(self):
        self.alive = False
        
    def photosynthesize(self):
        if self.photo_available: 
        amount = self.light * len(self.free_spaces) * PHOTO_FACTOR
        self.water_delta -= amount
        self.sugar_delta += amount
    
    def divide(self, coordinate, water_transfer, sugar_transfer):
        if coord in self.free_spaces:
            self.available_water = self.water_store
            "How to make sure the cell can't cheat by transfering" +
                "more than it has?"
        
        
class Environment:
    def __init__(self):
        self.cells = [] "Initialize a seed cell"
    
    def get_water(self, coordinate):
    def get_light(self, coordinate):
    def get_adjacent(self, coordinate):
    def get_free_space(self, coordinate):
        
