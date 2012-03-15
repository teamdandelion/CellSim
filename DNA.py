
from pdb import set_trace as debug

def getMem(cell, arg):
    if arg in cell.memory:
        return cell.memory[arg]
    else:
        return None
def dna_stem(cell):
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

def grass(cell):
    cell.debug = []
    def rpt(message):
        """Put a message in the debug message list"""
        cell.debug.append(message)
        
    adj = cell.adjacent
    up = adj['UP']; down = adj['DOWN']; right = adj['RIGHT']; left = adj['LEFT']
    mem = cell.memory
    type = cell.type

    if 'role' in mem:
        role = mem['role']
    else:
        rpt('No role found!')
        role = None
        
    if type == 'ROOT':
        # Root should transfer sugar down (if something is below) and transfer water up.
        # Later: Deal with capacity issues thru specialization, etc
        # Later: Intelligently don't grow beyond capacity limit
        if adj['DOWN'] == 'EMPTY':
            if cell.sugar > 30 and cell.water >= 20:
                cell.divide('DOWN', 10, 0, {'role': 'root'})
                rpt('Dividing down')
        else:
            sugar_to_xfer = max(0, cell.sugar - 30)
            cell.transfer('DOWN', sugar_to_xfer, 0)
            rpt('xfer {0} sugar down'.format(sugar_to_xfer))
                
        if cell.sugar < 200 or adj['DOWN'] != 'EMPTY':
            amt_to_xfer = cell.water
            cell.transfer('UP', 0, amt_to_xfer)
            rpt('xfer {0} water up'.format(amt_to_xfer))
        
            
    
    elif type == 'GENERIC':
        if role == 'stem':
            if 'num_leaves' not in mem and adj['UP'] != 'EMPTY':
                rpt('Sending {0} water up'.format(cell.water))
                cell.transfer('UP', 0, cell.water)
                
            if cell.light <= 3 and adj['UP'] == 'EMPTY':
                min_sugar = 15
                min_water = 5
                if cell.sugar > 20 + 2 * min_sugar and cell.water > 30: # Ensures parent and child both have min sugar after division
                    cell.divide('UP', cell.sugar - min_sugar - 20, cell.water - 20, {'role': 'stem'})
                    rpt('Growing up')
                # No point making a leaf here, let's grow higher
            if cell.light > 3:
                if 'num_leaves' not in mem:
                    if cell.sugar > 140 and cell.water > 140:
                        cell.divide('RIGHT', 120, 130, {'role': 'leaf'})  
                        mem['num_leaves'] = '1'
                elif mem['num_leaves'] == '1':
                    mem['established'] = 'yes'
                    water_to_leaf = min(cell.water-5, 15)
                    cell.transfer('RIGHT', 0, water_to_leaf)
                    rpt(str(water_to_leaf) + ' water to leaf')
                    if cell.sugar > 140 and cell.water > 140:
                        cell.divide('LEFT', 110, 130, {'role': 'leaf'})
                        mem['num_leaves'] = '2'
                        
            if adj['UP'] != 'EMPTY' and 'established' in adj['UP'].memory:
                cell.memory['established'] = 'yes'
                
                
                
            if 'established' in mem:
                dir = 'DOWN'
            else:
                dir = 'UP'
            
            if 'num_leaves' in mem and mem['num_leaves'] == '1':
                rpt('Xfer ' + str(cell.sugar //2) + ' ' + dir)
                cell.transfer(dir, cell.sugar // 2, 0)
            elif cell.sugar > 15 and adj[dir] != 'EMPTY':
                cell.transfer(dir, cell.sugar-15, 0)   
                
        if role == 'leaf':
            if cell.sugar > 100 and cell.water > 20:
                cell.specialize('PHOTO')

                
        if role == 'root':
            if cell.sugar > 100:
                rpt('Spec to root')
                cell.specialize('ROOT')
            else:
                rpt('Need sugar')
            
    elif type == 'STORE':
        if role == 'origin':
            if adj['DOWN'] == 'EMPTY':
                cell.divide('DOWN', 270, 60, {'role': 'root'})
                rpt('New root below!')
            if adj['UP'] == 'EMPTY':
                cell.divide('UP', 280, 300, {'role': 'stem'})
                rpt('New stem above!')
                
            if adj['UP'] != 'EMPTY' and adj['DOWN'] != 'EMPTY' and cell.sugar < 45:
                mem['role'] = 'stem'
                cell.specialize('GENERIC') # Don't need a store early in the game, and it consumes too much
            if cell.water > 30:
                cell.transfer('UP', 0, cell.water - 30)
            
            if 'established' in mem:
                # When cell is well-established, sugar reaching the store is sent down to expand the roots
                dir = 'DOWN'

            else:
                # When cell isn't yet established, sugar in the store is sent up to get photosynthesis going.
                dir = 'UP'
                
            if cell.sugar > 30:
                cell.transfer(dir, min(cell.sugar - 40, 200), 0)
                
    elif type == 'PHOTO':
        if cell.water > cell.free_spaces * cell.light * cell.photo_factor + 15:
            cell.photosynthesize()
        
        if cell.sugar > 10:
            if adj['RIGHT'] != 'EMPTY': dir = 'RIGHT'
            elif adj['LEFT'] != 'EMPTY': dir = 'LEFT'
            else: dir = 'NONE'
            if dir != 'NONE':
                cell.transfer(dir, cell.sugar - 10, 0)
                rpt('Sent ' + str(cell.sugar - 10) + ' to stem')
                
                

        
                
    
        