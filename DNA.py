
from pdb import set_trace as debug



def grass(cell):
    cell.debug = []
    def rpt(message):
        """Put a message in the debug message list"""
        cell.debug.append(message)
        
    adj = cell.adjacent
    up = adj['UP']; down = adj['DOWN']; right = adj['RIGHT']; left = adj['LEFT']
    mem = cell.memory
    type = cell.type
    sugar = cell.sugar
    water = cell.water
    
    if 'role' in mem:
        role = mem['role']
    else:
        rpt('No role found!')
        role = None
        
    if type == 'ROOT':
        # Root should transfer sugar down (if something is below) and transfer water up.
        # Later: Deal with capacity issues thru specialization, etc
        # Later: Intelligently don't grow beyond capacity limit
        if down == 'EMPTY':
            if sugar > 30 and water >= 20:
                cell.divide('DOWN', 10, 0, {'role': 'root'})
                rpt('Dividing down')
        else:
            sugar_to_xfer = max(0, sugar-15)
            cell.transfer('DOWN', sugar_to_xfer, 0)
            rpt('xfer {0} sugar down'.format(sugar_to_xfer))
                
        cell.transfer('UP', 0, water)
        rpt('xfer {0} water up'.format(water))
    
    elif type == 'GENERIC':
        if role == 'stem':
            if 'progress' not in mem:
                mem['progress'] = 'none'
                
            if cell.light <= 4 and up == 'EMPTY':
                min_sugar = 15
                min_water = 5
                if cell.sugar > 20 + 2 * min_sugar and cell.water > 30: # Ensures parent and child both have min sugar after division
                    cell.divide('UP', cell.sugar - min_sugar - 20, water - 20, {'role': 'stem'})
                    rpt('Growing up')
                # No point making a leaf here, let's grow higher
            
            if cell.light > 4:
                
                
        if 'established' in mem:
            dir = 'DOWN'
        else:
            dir = 'UP'
        
        if sugar > 15:
            cell.transfer(dir, sugar-15, 0)
                
        if role == 'root':
            if sugar > 100:
                rpt('Spec to root')
                cell.specialize('ROOT')
            else:
                rpt('Need sugar')
            
    elif type == 'STORE':
        if role == 'origin':
            if down == 'EMPTY':
                cell.divide('DOWN', 300, 60, {'role': 'root'})
                rpt('New root below!')
            if up == 'EMPTY':
                cell.divide('UP', 280, 200, {'role': 'stem'})
                rpt('New stem above!')
            if water > 30:
                cell.transfer('UP', 0, water-30)
            
            if 'established' in mem:
                # When cell is well-established, sugar reaching the store is sent down to expand the roots
                dir = 'DOWN'

            else:
                # When cell isn't yet established, sugar in the store is sent up to get photosynthesis going.
                dir = 'UP'
                
            if sugar > 30:
                cell.transfer(dir, min(sugar-30, 200), 0)
                
                

        
                
    
        