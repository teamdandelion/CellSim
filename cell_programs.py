#from cell import *
#from cell_types import *
from pdb import set_trace as debug

verbose = True

grass_initial_memory = {'INITIALIZE': 1}

def grass(cell):
    if verbose: print "Considering cell: " + str(cell)
    adj = cell.adjacent
    mem = cell.memory
    
    if 'role' in mem:
        my_role = mem['role']
        if verbose: print "Role: " + my_role
    else:
        my_role = 'None'
        if verbose: print "I have no role!"
        
    if cell.type == 'ROOT':
        if adj['RIGHT'] != 'EMPTY':
            cell.transfer('RIGHT', 0, cell.water)
        elif adj['LEFT'] != 'EMPTY':
            cell.transfer('LEFT', 0, cell.water)
            
    if cell.type == 'PHOTO':
        if cell.water > 30 and cell.sugar + 20 < cell.sugar_max:
            # Could be a lot more sophisticated
            cell.photosynthesize()
        if adj['RIGHT'] != 'EMPTY':
            cell.transfer('RIGHT', (cell.sugar - 20), 0)
        elif adj['LEFT'] != 'EMPTY':
            cell.transfer('RIGHT', (cell.sugar - 20), 0)
            
    if cell.type == 'VASCULAR':
        if cell.water > 25:
            if adj['RIGHT'] in ('GENERIC', 'PHOTO'):
                cell.transfer('RIGHT', 0, min((cell.sugar - 10) / 2, 10))
            if adj['LEFT'] in ('GENERIC', 'PHOTO'):
                cell.transfer('LEFT' , 0, min((cell.sugar - 10) / 2, 10))
        if cell.water > 10:
            cell.transfer('UP', 0, cell.water - 10)
            
        if cell.sugar > 25:
            if adj['RIGHT'] in ('GENERIC', 'ROOT'):
                cell.transfer('RIGHT', min((cell.sugar - 10) / 2, 10), 0)
            if adj['LEFT'] in ('GENERIC', 'ROOT'):
                cell.transfer('LEFT',  min((cell.sugar - 10) / 2, 10), 0)
        if cell.sugar > 10:
            cll.transfer('DOWN', cell.sugar - 10, 0)
    
    if cell.type == 'STORE':
        if my_role == 'origin':
            #debug()
            if adj['UP'] == 'EMPTY':
                cell.divide('UP', 200, 300, {'role': 'stem'})
            if adj['DOWN'] == 'EMPTY':
                cell.divide('DOWN', 200, 100, {'role': 'stem'})
                if verbose: print "\tMaking children"
    
        elif cell.water + 10 > cell.water_max_store and cell.sugar + 10 > cell.sugar_max_store:
            if 'made seed' not in mem:
                mem['made seed']='left'
                cell.divide('LEFT', 220, 40, {'role': 'seed'})
                if verbose: print "Making a seed to the left"
            else:
                cell.transfer('LEFT', 300, 20)
            
        else:
            cell.transfer('DOWN', cell.sugar - 30, 0)
            cell.transfer('UP'  , 0, cell.water - 30)
            if verbose: print "Transfering sugar down and water up"
        
    if cell.type == 'SEED':
        pass
        
    if cell.type == 'GENERIC':
        if my_role == 'stem':
            if cell.light_intensity > 0:
                daughter_role = 'leaf'
            else:
                daughter_role = 'root'
            if cell.sugar > 100 and cell.water > 100:
                #debug()
                if adj['RIGHT'] == 'EMPTY':
                    cell.divide('RIGHT', 10, 10, {'role': daughter_role})
                    if verbose: print "Dividing to make " + daughter_role + " to the right"
                if adj['LEFT'] == 'EMPTY':
                    cell.divide('LEFT', 10, 10, {'role': 'leaf'})
                    if verbose: print "Dividing to make " + daughter_role + " to the left"
                if adj['UP'] == 'EMPTY':
                    cell.divide('UP', 10, 10, {'role': 'stem'})
                    if verbose: print "Making a stem above"
                if adj['DOWN'] == 'EMPTY':
                    cell.divide('DOWN', 10, 10, {'role': 'stem'})
                    if verbose: print "Making a stem below"
                    
            if cell.free_spaces == 0 and cell.sugar_avil > 40 and cell.water > 40:
                cell.specialize('VASCULAR')
                if verbose: print "Specializing to vascular"
        
        if my_role == 'root':
            if cell.sugar > 105:
                cell.specialize('ROOT')
                if verbose: print "Specializing to root"
            
        if my_role == 'leaf':
            if cell.sugar > 105 and cell.water > 125:
                cell.specialize('PHOTO')
                if verbose: print "Specializing to photo"
        
        if my_role == 'seed':
            if cell.sugar == 200 and cell.water >=20:
                cell.specialize('SEED')
                if verbose: print "Specializing to seed"
                
            
            
