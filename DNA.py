
from pdb import set_trace as debug

def get_children_demand(cell):
    high_sugar_demand = 0
    low_sugar_demand  = 0
    high_water_demand = 0
    low_water_demand  = 0
    
    for adjcell in cell.adjacent.itervalues():
        if adjcell != 'EMPTY':
            adj_demand = getMem(adjcell, 'demand')
            if adj_demand != 0:
                if getMem(adjcell, 'sugardaddy') == cell:
                    high_sugar_demand += adj_demand[0][0]
                    low_sugar_demand  += adj_demand[0][1]
                if getMem(adjcell, 'waterdaddy') == cell:
                    high_water_demand += adj_demand[1][0]
                    low_water_demand  += adj_demand[1][1]
    
    return ( (high_sugar_demand, low_sugar_demand), (high_water_demand, low_water_demand))

def manage_resource_flow(cell):
    # Local demand: cell consumption, storage buildup (for seed or growth)
    # Adjacent demand: Carries over, adjust for splits
    # Local supply: cell production
    # Overflow / storage excess adjustment 
    # Reqs following memory attributes:
    #   min_sugar
    #   growth_demand
    min_sugar = cell.sugar_consumption * 10
    free_sugar = cell.sugar - min_sugar
    
    min_water = cell.water_consumption * 10
    free_water = cell.water - min_water
    
    if cell.type == 'PHOTO':
        photo_water = cell.light * cell.free_spaces * cell.photo_factor
        if free_water >= photo_water:
            cell.photosynthesize()
        min_water += 2 * photo_water
    
    adj_sugar_demand, adj_water_demand = get_children_demand(cell)

    growth_sugar = getMem(cell, 'growth_sugar')
    growth_water = getMem(cell, 'growth_water')

    if free_sugar < adj_sugar_demand[0]:
    # Triggers if free sugar is less than the net high_sugar_demand
        if free_sugar > 0:
            distribute(cell, free_sugar, 'sugar', 'high')
        high_sugar_demand = adj_sugar_demand[0] - free_sugar
        # Reports a higher demand than sum of adj demands if free sugar is less than zero, a lower one if free sugar is greater than zero
        free_sugar = 0
        
    elif free_sugar >= adj_sugar_demand[0]:
    # Triggers if there's enough free sugar to satisfy everyone's pressing needs
        distribute(cell, adj_sugar_demand[0], 'sugar', 'high')
        high_sugar_demand = 0
        free_sugar -= adj_sugar_demand[0]
      
    low_sugar_demand = max(adj_sugar_demand[1] + growth_sugar - free_sugar, 0)
    
    if free_sugar > growth_sugar:
        amt_to_send = min(adj_sugar_demand[1], free_sugar - growth_sugar)
        distribute(cell, amt_to_send, 'sugar', 'low')
        free_sugar -= amt_to_send
    
    if free_sugar > 0: #There is free sugar leftover after satisfying low and high demand!
        distribute(cell, free_sugar, 'sugar', 'even')

    if free_water < adj_water_demand[0]:
    # Triggers if free water is less than the net high_water_demand
        if free_water > 0:
            distribute(cell, free_water, 'water', 'high')
        high_water_demand = adj_water_demand[0] - free_water
        # Reports a higher demand than sum of adj demands if free water is less than zero, a lower one if free water is greater than zero
        free_water = 0
        
    elif free_water >= adj_water_demand[0]:
    # Triggers if there's enough free water to satisfy everyone's pressing needs
        distribute(cell, adj_water_demand[0], 'water', 'high')
        high_water_demand = 0
        free_water -= adj_water_demand[0]
      
    low_water_demand = max(adj_water_demand[1] + growth_water - free_water, 0)
    
    if free_water > growth_water:
        amt_to_send = min(adj_water_demand[1], free_water - growth_water)
        distribute(cell, amt_to_send, 'water', 'low')
        free_water -= amt_to_send
    
    if free_water > 0: #There is free water leftover after satisfying low and high demand!
        distribute(cell, free_water, 'water', 'even')
        
    cell.memory['demand'] = ( (high_sugar_demand, low_sugar_demand), (high_water_demand, low_water_demand) )
        
        
def distribute(cell, amount, resource, pattern):
    """Automates distribution of resource (given amount) to adjacent cells according to pattern
    
    cell: A cell
    amount: A float
    resource: 'sugar' or 'water'
    pattern: 'high' distributes according to high demand profile for given resource, 'low' according to the low demand profile, 'even' gives equally to each adjacent cell
    """
    #if cell.world.coordinates[cell] == (0, 2):
    #    debug()
    report(cell, 'Distributing {0} {1} in pattern {2}'.format(amount, resource, pattern))
    
    #if pattern == 'low' and resource == 'sugar' and amount == 27:
        #debug()
    
    if pattern in ('high', 'low'):
        adj_demand = get_children_demand(cell)
        if resource == 'sugar':
            adj_demand = adj_demand[0]
        elif resource == 'water':
            adj_demand = adj_demand[1]
        else:
            debug()
        if pattern == 'high':
            adj_demand = adj_demand[0]
        else:
            adj_demand = adj_demand[1]
        
        if adj_demand == 0:
            distribution_factor = 1
        else:
            distribution_factor = float(amount) / adj_demand
        # The proportion of amount demanded to give to each adjacent cell
        
        for dir, adjcell in cell.adjacent.iteritems():
            if adjcell != 'EMPTY':
                amt_to_send = distribution_factor * getCellDemand(cell, adjcell, resource, pattern)
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
                
            

def getMem(cell, arg):
    if arg in cell.memory:
        return cell.memory[arg]
    else:
        print "Cell " + str(cell) + " attempted to access non-existant memory " + arg
        return 0
        
def adjAttr(cell, dir, attr):
    if cell.adjacent[dir] != 'EMPTY':
        return cell.adjacent[dir].__dict__(attr)
    else:
        return 'EMPTY'

#def dna_stem(cell):
    # Automate the behavior of a stem cell.
    # Send water up
    # Send sugar in following directions:
    #   Down: To support roots
    #   Down: To grow roots
    #   Sides: To support leaves
    #   Up: To grow taller
    # Affected by the following memory parameters:
    # Idea: use 
    # 
def getCellDemand(cell, adjcell, resource, priority):
    if resource == 'sugar':
        daddytype = 'sugardaddy'
    elif resource == 'water':
        daddytype = 'waterdaddy'
    else:
        debug()
        
    if getMem(adjcell, daddytype) == cell:
        demand = getMem(adjcell, 'demand')
        if demand == 0:
            return 0
        else:
            if resource == 'sugar':
                demand = demand[0]
            elif resource == 'water':
                demand = demand[1]
            else:
                debug()
            
            if priority == 'high':
                demand = demand[0]
            elif priority == 'low':
                demand = demand[1]
            else:
                debug()
            
            return demand
    else:
        return 0
        
def xferResource(cell, dir, amount, resource):
    if resource == 'sugar':
        cell.transfer(dir, amount, 0)
    else:
        cell.transfer(dir, 0, amount)

def report(cell, message):
    """Put a message in the debug message list"""
    cell.debug.append(message)

def grass(cell):
    if cell.world.cycles == 10:
        if cell.adjacent['N'] == 'EMPTY':
            if cell.adjacent['E'] != 'EMPTY':
                cell.memory['sugardaddy'] = cell.adjacent['E']
            else:
                cell.memory['sugardaddy'] = None
        else:
            cell.memory['sugardaddy'] = cell.adjacent['N']
        
        if cell.adjacent['S'] == 'EMPTY':
            if cell.adjacent['W'] != 'EMPTY':
                cell.memory['waterdaddy'] = cell.adjacent['W']
            else:
                cell.memory['waterdaddy'] = None
        else:
            cell.memory['waterdaddy'] = cell.adjacent['S']
        
        cell.memory['demand'] = ( (0,0), (0,0))
        cell.memory['growth_sugar'] = cell.sugar_consumption * 30
        cell.memory['growth_water'] = cell.water_consumption * 30
        
    
    elif cell.world.cycles > 10:
        cell.debug = ['Managing resource flows.']
        manage_resource_flow(cell)
    else:
            
        adj = cell.adjacent
        mem = cell.memory
        type = cell.type
    
        if 'role' in mem:
            role = mem['role']
        else:
            report(cell, 'No role found!')
            role = None
            
        if type == 'ROOT':
            # Root should transfer sugar down (if something is below) and transfer water up.
            # Later: Deal with capacity issues thru specialization, etc
            # Later: Intelligently don't grow beyond capacity limit
            if adj['S'] == 'EMPTY':
                if cell.sugar > 30 and cell.water >= 20:
                    cell.divide('S', 10, 0, {'role': 'root'})
                    report(cell, 'Dividing down')
            else:
                sugar_to_xfer = max(0, cell.sugar - 30)
                cell.transfer('S', sugar_to_xfer, 0)
                report(cell, 'xfer {0} sugar down'.format(sugar_to_xfer))
                    
            if cell.sugar < 200 or adj['S'] != 'EMPTY':
                amt_to_xfer = cell.water
                cell.transfer('N', 0, amt_to_xfer)
                report(cell, 'xfer {0} water up'.format(amt_to_xfer))
            
                
        
        elif type == 'GENERIC':
            if role == 'stem':
                if 'num_leaves' not in mem and adj['N'] != 'EMPTY':
                    report(cell, 'Sending {0} water up'.format(cell.water))
                    cell.transfer('N', 0, cell.water)
                    
                if cell.light <= 3 and adj['N'] == 'EMPTY':
                    min_sugar = 15
                    min_water = 5
                    if cell.sugar > 20 + 2 * min_sugar and cell.water > 30: # Ensures parent and child both have min sugar after division
                        cell.divide('N', cell.sugar - min_sugar - 20, cell.water - 20, {'role': 'stem'})
                        report(cell, 'Growing up')
                    # No point making a leaf here, let's grow higher
                if cell.light > 3:
                    if 'num_leaves' not in mem:
                        if cell.sugar > 140 and cell.water > 140:
                            cell.divide('E', 120, 130, {'role': 'leaf'})  
                            mem['num_leaves'] = '1'
                    elif mem['num_leaves'] == '1':
                        mem['established'] = 'yes'
                        water_to_leaf = min(cell.water-5, 15)
                        cell.transfer('E', 0, water_to_leaf)
                        report(cell, str(water_to_leaf) + ' water to leaf')
                        if cell.sugar > 140 and cell.water > 140:
                            cell.divide('W', 110, 130, {'role': 'leaf'})
                            mem['num_leaves'] = '2'
                            
                if adj['N'] != 'EMPTY' and 'established' in adj['N'].memory:
                    cell.memory['established'] = 'yes'
                    
                    
                    
                if 'established' in mem:
                    dir = 'S'
                else:
                    dir = 'N'
                
                if 'num_leaves' in mem and mem['num_leaves'] == '1':
                    report(cell, 'Xfer ' + str(cell.sugar //2) + ' ' + dir)
                    cell.transfer(dir, cell.sugar // 2, 0)
                    cell.memory['growth_sugar'] = 180
                elif cell.sugar > 15 and adj[dir] != 'EMPTY':
                    cell.transfer(dir, cell.sugar-15, 0)   
                    
            if role == 'leaf':
                if cell.sugar > 100 and cell.water > 20:
                    cell.specialize('PHOTO')
    
                    
            if role == 'root':
                if cell.sugar > 100:
                    report(cell, 'Spec to root')
                    cell.specialize('ROOT')
                else:
                    report(cell, 'Need sugar')
                
        elif type == 'STORE':
            if role == 'origin':
                if adj['S'] == 'EMPTY':
                    cell.divide('S', 270, 60, {'role': 'root'})
                    report(cell, 'New root below!')
                if adj['N'] == 'EMPTY':
                    cell.divide('N', 280, 300, {'role': 'stem'})
                    report(cell, 'New stem above!')
                    
                if adj['N'] != 'EMPTY' and adj['S'] != 'EMPTY' and cell.sugar < 45:
                    mem['role'] = 'stem'
                    cell.specialize('GENERIC') # Don't need a store early in the game, and it consumes too much
                if cell.water > 30:
                    cell.transfer('N', 0, cell.water - 30)
                
                if 'established' in mem:
                    # When cell is well-established, sugar reaching the store is sent down to expand the roots
                    dir = 'S'
    
                else:
                    # When cell isn't yet established, sugar in the store is sent up to get photosynthesis going.
                    dir = 'N'
                    
                if cell.sugar > 30:
                    cell.transfer(dir, min(cell.sugar - 40, 200), 0)
                    
        elif type == 'PHOTO':
            if cell.water > cell.free_spaces * cell.light * cell.photo_factor + 15:
                cell.photosynthesize()
            
            if cell.sugar > 10:
                if adj['E'] != 'EMPTY': dir = 'E'
                elif adj['W'] != 'EMPTY': dir = 'W'
                else: dir = 'NONE'
                if dir != 'NONE':
                    cell.transfer(dir, cell.sugar - 10, 0)
                    report(cell, 'Sent ' + str(cell.sugar - 10) + ' to stem')
                
                

        
                
    
        