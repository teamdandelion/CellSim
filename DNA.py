from pdb import set_trace as debug
from random import random

# Warning: Nothing is done atm to ensure that the children are valid children, i.e. they haven't died...

"""Entry Point"""
def dna_grass(cell):
    """Entry point for the program. Automates cell behavior."""
    if getMem(cell, 'initialized') == 0:
        initialize(cell)
    role = getMem(cell, 'role')
    if role == 0:
        print "Error: Cell has no role!"
        debug()
    elif role == 'stem':
        automate_stem(cell)
    elif role == 'root':
        automate_root(cell)
    elif role == 'leaf':
        automate_leaf(cell)
    elif role == 'store':
        automate_store(cell)
    elif role == 'origin':
        automate_origin(cell)
    elif role == 'bud':
        automate_bud(cell)
    manage_resource_flow(cell)
        
def initialize(cell):
    if cell == 'EMPTY':
        print "ERROR: Failed division"
        debug()
    if 'growth_sugar' not in cell.memory:
        cell.memory['growth_sugar'] = cell.sugar_consumption * 20
    if 'growth_water' not in cell.memory:
        cell.memory['growth_water'] = cell.water_consumption * 20
    if 'sugar_children' not in cell.memory:
        cell.memory['sugar_children'] = []
    if 'water_children' not in cell.memory:
        cell.memory['water_children'] = []
    cell.memory['initialized'] = 1
    if 'demand' not in cell.memory:
        cell.memory['demand'] = ((0, 0), (0, 0))

def automate_origin(cell):
    stem_mem = {'role': 'stem', 'unestablished': 1, 'growth_til_leaf': 2}
    root_mem = {'role': 'root', 'water_children': [(cell, 'N')], 'growth_dir': 'S', 'root_growth_limit': 1}
    cell.memory['root_growth_limit'] = 2
    new_stem = cell.divide('N', 300, 300, stem_mem)
    new_root = cell.divide('S', 250, 60, root_mem)
    cell.memory['growth_sugar'] = 0
    cell.memory['growth_water'] = 0
    add_sugar_child(cell, new_stem, 'N')
    add_water_child(cell, new_stem, 'N')
    add_sugar_child(cell, new_root, 'S')
    cell.memory['role'] = 'store'
    initialize(new_stem)
    initialize(new_root)

def automate_stem(cell):
    if getMem(cell, 'unestablished') == 1:
        establish_stem(cell)
    else:
        if getMem(cell, 'growth_to_bud') == 0 and cell.adjacent['N'] == 'EMPTY':
            if cell.sugar > 40 and cell.water > 40:
                new_cell = cell.divide('N', cell.sugar - 30, cell.water - 30, {'role': 'bud'})
                initialize(new_cell)
                add_water_child(cell, new_cell, 'N')
                add_sugar_child(cell, new_cell, 'N')
                # Get rid of this sugar child once the bud has established itself
            else:
                cell.memory['growth_sugar'] = 40
                cell.memory['growth_water'] = 40
    
def automate_bud(cell):
    if getMem(cell.adjacent['S'], 'role') == 'stem':
        # Bud to the NW, NE, and revert to stem with budcounter
        if cell.adjacent['NW'] == 'EMPTY':   dir = 'NW'
        elif cell.adjacent['NE'] == 'EMPTY': dir = 'NE'
        elif cell.adjacent['N'] == 'EMPTY':  dir = 'N'
        else: 
            dir = 'X'
            debug()
        if dir in ('NW', 'NE'):
            if cell.sugar > 40 and cell.water > 40:
                new_mem = {'role': 'bud', 'growth_dir': dir, 'bud_growth_limit': 5}
                new_cell = cell.divide(dir, 10, 10, new_mem)
                initialize(new_cell)
                add_sugar_child(new_cell, cell, dir)
                add_water_child(cell, new_cell, dir)
            else:
                cell.memory['growth_sugar'] = 40
                cell.memory['growth_water'] = 40
        if dir == 'N':
            cell.memory['role'] = 'stem'
            cell.memory['growth_to_bud'] = 3
    else:
        growth_limit = getMem(cell, 'bud_growth_limit')
        growth_dir = getMem(cell, 'growth_dir')
        leafdir = 'X'
        for dir in outsideDirs(growth_dir):
            if cell.adjacent[dir] == 'EMPTY':
                leafdir = dir
        if leafdir != 'X':
            grow_leaf(cell, leafdir)
        elif cell.adjacent[growth_dir] == 'EMPTY' and growth_limit > 0 and can_grow(cell, 40, 40):
            new_mem = {'role': 'bud', 'growth_dir': growth_dir, 'bud_growth_limit': growth_limit - 1, 'sugar_children': [(cell, oppDir(dir))]}
            new_bud = cell.divide(growth_dir, 10, 10, new_mem)
            initialize(new_bud)
            add_water_child(cell, new_bud, growth_dir)
                
def can_grow(cell, sugar_req, water_req):
    if cell.sugar > sugar_req and cell.water>water_req:
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 0
        return True
    else:
        cell.memory['growth_sugar'] = sugar_req
        cell.memory['growth_water'] = water_req
        return False
                
def outsideDirs(dir):
    if dir in ('NW', 'SW'):
        return ['N', 'W', 'S']
    elif dir in ('NE', 'SE'):
        return ['N', 'E', 'S']
                
def grow_leaf(cell, dir):
    if cell.sugar >= 150 and cell.water >= 80:
        new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [(cell, oppDir(dir) )]}
        new_cell = cell.divide(dir, 120, 50, new_mem)
        add_water_child(cell, new_cell, dir)
        initialize(new_cell)
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 0
    else:
        cell.memory['growth_sugar'] = 150
        cell.memory['growth_water'] = 80

def establish_stem(cell):
    if cell.adjacent['N'] != 'EMPTY' and getMem(cell.adjacent['N'], 'unestablished') == 0:
        cell.memory['unestablished'] = 0
        cell.memory['sugar_children'] = [(cell.adjacent['S'], 'S')]
        
    growth_til_leaf = getMem(cell, 'growth_til_leaf')
    if growth_til_leaf != 0:
        if cell.adjacent['N'] == 'EMPTY':
            if cell.sugar > 40 and cell.water > 40:
                new_mem = {'role': 'stem', 'unestablished': 1, 'growth_sugar': 200, 'growth_water': 200, 'growth_til_leaf': growth_til_leaf -1}
                new_cell = cell.divide('N', cell.sugar-30, cell.water-30, new_mem)
                cell.memory['sugar_children'].append((new_cell, 'N'))
                cell.memory['water_children'].append((new_cell, 'N'))
                initialize(new_cell)
                report(cell, 'Growing up!')
            else:
                report(cell, 'Not enough resources to grow up!')
            cell.memory['growth_sugar'] = 200
            cell.memory['growth_water'] = 200
        else:
            report(cell, 'Waiting for establishment.')
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0
    else:
        if cell.adjacent['NE'] == 'EMPTY':
            if cell.sugar > 150 and cell.water > 80:
                new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [(cell, 'SW')]}
                new_cell = cell.divide('NE', 120, 50, new_mem)
                cell.memory['water_children'].append((new_cell, 'NE'))
                initialize(new_cell)
        else:
            if cell.sugar > 150 and cell.water > 80:
                new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [(cell, 'SE')]}
                new_cell = cell.divide('NW', 120, 50, new_mem)
                cell.memory['water_children'].append((new_cell, 'NW'))
                initialize(new_cell)
                cell.memory['unestablished'] = 0
                cell.memory['sugar_children'] = [(cell.adjacent['S'], 'S')]
                cell.memory['growth_to_bud'] = 0

def automate_store(cell):
    if getMem(cell, 'already_established')==0 and cell.adjacent['N'] != 'EMPTY' and getMem(cell.adjacent['N'], 'unestablished') == 0:
        cell.memory['unestablished'] = 0
        cell.memory['sugar_children'] = [(cell.adjacent['S'], 'S')]
        cell.memory['root_growth_limit'] = 3
        cell.memory['already_established'] = 1
    
    if getMem(cell, 'unestablished') == 0:
        if cell.adjacent['SE'] == 'EMPTY': dir = 'SE'
        elif cell.adjacent['SW'] == 'EMPTY': dir = 'SW'
        else: dir = 'X'
        if dir != 'X':
            if cell.sugar > 150 and cell.water > 100:
                root_mem = {'role': 'root', 'water_children': [(cell, oppDir(dir))], 'growth_dir': dir, 'root_growth_limit': 5}
                new_root = cell.divide(dir, 110, 60, root_mem)
                add_sugar_child(cell, new_root, oppDir(dir))
                initialize(new_root)
            else:
                cell.memory['growth_sugar'] = 150
                cell.memory['growth_water'] = 100
        else:
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0
        if random() < .02:
            cell.memory['root_growth_limit'] += 1
        
        
def automate_root(cell):
    if cell.type == 'GENERIC':
        if cell.sugar > 110:
            cell.specialize('ROOT')
        else:
            cell.memory['growth_sugar'] = 110
    else:
        dir = cell.memory['growth_dir']
        growth_remaining = cell.adjacent[oppDir(dir)].memory['root_growth_limit'] -1 
        cell.memory['root_growth_limit'] = growth_remaining
        if cell.adjacent[dir] == 'EMPTY' and growth_remaining > 0:
            if cell.sugar > 140 and cell.water >= 30:
                new_mem = {'role': 'root', 'water_children': [(cell, oppDir(dir))], 'root_growth_limit': growth_remaining - 1, 'growth_dir': dir}
                new_cell = cell.divide(dir, 110, 10, new_mem)
                initialize(new_cell)
                cell.memory['sugar_children'].append((new_cell, dir))
            else:
                cell.memory['growth_sugar'] = 140
                cell.memory['growth_water'] = 30
        else:
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0

    
def automate_leaf(cell):
    if cell.type != 'PHOTO' and cell.sugar > 110 and cell.water > 40:
        cell.specialize('PHOTO')
    
    if cell.type == 'PHOTO':
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 100
        # Good to keep a substantial reserve of water, if you are a leaf.

"""Resource flow functions"""

def manage_resource_flow(cell):
    """Manages resource flow from a cell. If sugar children or water children need resources, they will be sent; high priority first, low priority after. If no resources are needed, but the cell has more than it needs, it evenly distributes its excess resources to neighboring cells.
    
    Presently no adjustment is made for a situation where one cell has multiple parents (i.e. violation of tree structure)
    """

    min_sugar = cell.sugar_consumption * 10
    free_sugar = cell.sugar - min_sugar
    
    min_water = cell.water_consumption * 10
    free_water = cell.water - min_water
    
    if cell.type == 'PHOTO':
        photo_water = cell.light * cell.free_spaces * cell.photo_factor
        if free_water >= photo_water:
            cell.photosynthesize()
        free_water -= 2 * photo_water
    
    children_sugar_demand, children_water_demand = get_children_demand(cell)

    growth_sugar = getMem(cell, 'growth_sugar') + 1 
    growth_water = getMem(cell, 'growth_water') + 1 
    # +1 deals with some issue (related to floats I think) that caused cell.sugar or water to approach growth_sugar but not reach it, preventing conditions from triggering

    if free_sugar < children_sugar_demand[0]:
    # Triggers if free sugar is less than the net high_sugar_demand
        report(cell, 'Insufficient free sugar for high demand')
        if free_sugar > 0:
            distribute(cell, free_sugar, 'sugar', 'high')
        high_sugar_demand = children_sugar_demand[0] - free_sugar
        # Reports a higher demand than sum of adj demands if free sugar is less than zero, a lower one if free sugar is greater than zero
        free_sugar = 0
        
    elif free_sugar >= children_sugar_demand[0]:
    # Triggers if there's enough free sugar to satisfy everyone's pressing needs
        report(cell, 'Sufficient sugar for high demand')
        distribute(cell, children_sugar_demand[0], 'sugar', 'high')
        high_sugar_demand = 0
        free_sugar -= children_sugar_demand[0]
    
    free_sugar -= growth_sugar
    # Now that we are switching to low demand, the cell's free sugar has to take into account its own growth requirements.
    
    low_sugar_demand = max(children_sugar_demand[1] - free_sugar, 0)
    # As before, free sugar might be negative (in which case low_sugar_demand goes higher than children's demand) or positive (vice versa)
    
    if free_sugar > 0:
        amt_to_send = min(children_sugar_demand[1], free_sugar)
        distribute(cell, amt_to_send, 'sugar', 'low')
        free_sugar -= amt_to_send
    
        if free_sugar > 0: #There is free sugar leftover after satisfying low and high demand!
            distribute(cell, free_sugar, 'sugar', 'even')

    if free_water < children_water_demand[0]:
    # Triggers if free water is less than the net high_water_demand
        if free_water > 0:
            distribute(cell, free_water, 'water', 'high')
        high_water_demand = children_water_demand[0] - free_water
        # Reports a higher demand than sum of adj demands if free water is less than zero, a lower one if free water is greater than zero
        free_water = 0
        
    elif free_water >= children_water_demand[0]:
    # Triggers if there's enough free water to satisfy everyone's pressing needs
        distribute(cell, children_water_demand[0], 'water', 'high')
        high_water_demand = 0
        free_water -= children_water_demand[0]
      
    free_water -= growth_water
    
    low_water_demand = max(children_water_demand[1] - free_water, 0)
    
    if free_water > 0:
        amt_to_send = min(children_water_demand[1], free_water)
        distribute(cell, amt_to_send, 'water', 'low')
        free_water -= amt_to_send
    
        if free_water > 0: #There is free water leftover after satisfying low and high demand!
            distribute(cell, free_water, 'water', 'even')
        
    cell.memory['demand'] = ( (high_sugar_demand, low_sugar_demand), (high_water_demand, low_water_demand) )
        

def get_children_demand(cell):
    """Returns how much resources are demanded by the cell's children"""
    high_sugar_demand = 0
    low_sugar_demand  = 0
    high_water_demand = 0
    low_water_demand  = 0
    
    if getMem(cell, 'sugar_children') != 0:
        for (sugar_child, __) in getMem(cell, 'sugar_children'):
            child_demand = getMem(sugar_child, 'demand')
            high_sugar_demand += child_demand[0][0]
            low_sugar_demand  += child_demand[0][1]
            
    if getMem(cell, 'water_children') != 0:
        for (water_child, __) in getMem(cell, 'water_children'):
            child_demand = getMem(water_child, 'demand')
            high_water_demand += child_demand[1][0]
            low_water_demand  += child_demand[1][1]             
    
    return ((high_sugar_demand, low_sugar_demand), 
            (high_water_demand, low_water_demand))

def distribute(cell, amount, resource, pattern):
    """Automates distribution of resource (given amount) to adjacent cells according to pattern
    
    cell: A cell
    amount: A float
    resource: 'sugar' or 'water'
    pattern: 'high' distributes according to high demand profile for given resource, 'low' according to the low demand profile, 'even' gives equally to each adjacent cell
    """

    report(cell, 'Distributing {0} {1} in pattern {2}'.format(amount, resource, pattern))
    
    index1 = int(resource == 'water')
    if pattern in ('high', 'low'):
        index2 = int(pattern == 'low')
        demand = get_children_demand(cell)[index1][index2]
        if demand == 0:
            distribution_factor = 1
        else:
            distribution_factor = float(amount) / demand
        # The proportion of amount demanded to give to each adjacent cell
        
        if resource == 'sugar' and getMem(cell, 'sugar_children') != 0:
            for (sugar_child, dir) in getMem(cell, 'sugar_children'):
                amt_to_send = getMem(sugar_child, 'demand')[index1][index2] * distribution_factor
                xferResource(cell, dir, amt_to_send, resource)
        elif resource == 'water' and getMem(cell, 'water_children') != 0:
                for (water_child, dir) in getMem(cell, 'water_children'):
                    amt_to_send = getMem(water_child, 'demand')[index1][index2] * distribution_factor
                    xferResource(cell, dir, amt_to_send, resource)
    else:
        if pattern != 'even':
            debug()
        num_adjacent_cells = 9 - cell.free_spaces
        # Used 9 as starting number so that the cell will always keep a portion for itself!
        amt_to_send = float(amount) / num_adjacent_cells
        
        for dir, adjcell in cell.adjacent.iteritems():
            if adjcell != 'EMPTY':
                xferResource(cell, dir, amt_to_send, resource)
                
        
def xferResource(cell, dir, amount, resource):
    if resource == 'sugar':
        cell.transfer(dir, amount, 0)
    else:
        cell.transfer(dir, 0, amount)
        
def add_sugar_child(cell, child, child_dir):
    """Note: Takes the direction the child is in, not the direction the parent is in"""
    if 'sugar_children' not in cell.memory:
        cell.memory['sugar_children'] = []
    cell.memory['sugar_children'].append((child, oppDir(child_dir)))
    
def add_water_child(cell, child, child_dir):
    """Note: Takes the direction the child is in, not the direction the parent is in"""
    if 'water_children' not in cell.memory:
        cell.memory['water_children'] = []  
    cell.memory['water_children'].append((child, child_dir))


"""General functions"""

def getMem(cell, arg):
    if cell == 'EMPTY':
        return 'EMPTY'
    elif arg in cell.memory:
        return cell.memory[arg]
    else:
        print "Cell " + str(cell) + " attempted to access non-existant memory " + arg
        return 0
        
def adjAttr(cell, dir, attr):
    if cell.adjacent[dir] != 'EMPTY':
        return cell.adjacent[dir].__dict__(attr)
    else:
        return 'EMPTY'


def oppDir(dir):
    directions     = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    opp_directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    return opp_directions[directions.index(dir)]


def report(cell, message):
    """Put a message in the debug message list"""
    cell.debug.append(message)