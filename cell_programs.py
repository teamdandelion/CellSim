from cell import *
from cell_types import *

grass_initial_memory = {'INITIALIZE': 1}

def grass(cell):
    if cell.type == 'ROOT':
        if cell.adjacent['RIGHT'] != None:
            cell.transfer('RIGHT', 0, cell.water_store)
        elif cell.adjacent['LEFT'] != None:
            cell.transfer('LEFT', 0, cell.water_store)
            
    if cell.type == 'PHOTO':
        if cell.water_store > 20 and cell.sugar_store + 20 < cell.sugar_max_store:
            cell.photosynthesize()
        if cell.adjacent['RIGHT'] != None:
            cell.transfer('RIGHT', (cell.sugar_store-20), 0)
        elif cell.adjacent['LEFT'] != None:
            cell.transfer('RIGHT', (cell.sugar_store-20), 0)
            
    if cell.type == 'VASCULAR':
        if cell.light > 0:
            if cell.water_store > 25:
                if cell.adjacent['RIGHT'] in ('GENERIC', 'PHOTO')
                    cell.transfer('RIGHT', 0, 10)
                if cell.adjacent['LEFT'] in ('GENERIC', 'PHOTO')
                    cell.transfer('LEFT', 0, 10)
            if cell.water_store - cell.water_used > 10:
                cll.transfer('UP', 0, cell.water_store - cell.water_used - 10)
                
            if cell.sugar_store > 25:
                if cell.adjacent['RIGHT'] in ('GENERIC', 'ROOT'):
                    cell.transfer('RIGHT', 10, 0)
                if cell.adjacent['LEFT'] in ('GENERIC', 'ROOT'):
                    cell.transfer('LEFT', 10, 0)
            if cell.sugar_store - cell.sugar_used > 10:
                cll.transfer('DOWN', cell.sugar_store - cell.sugar_used - 10, 0)
    
    if cell.type == 'STORE':
        if 'INITIALIZE' in cell.memory:
            if cell.memory['INITIALIZE'] == 1:
                cell.memory['INITIALIZE'] = 0
                cell.divide('UP', 240, 350, {'role': 'stem'})
                cell.divide('DOWN', 240, 130, {'role': 'rootstem'})
    
        elif cell.water_store + 10 > cell.water_max_store and cell.sugar_store + 10 > cell.sugar_max_store:
            if 'made seed' not in cell.memory:
            cell.memory['made seed']='left'
            cell.divide('LEFT', 220, 40, {'role': 'SEED'})
            else:
                cell.transfer('LEFT', 300, 20)
            
        else:
            cell.transfer('DOWN', cell.sugar_store - cell.sugar_used - 30, 0)
            cell.transfer('UP'  , 0, cell.water_store - cell.water_used - 30)
        
    if cell.type == 'SEED':
        pass
        
    if cell.type == 'GENERIC':
        if 'role' not in cell.memory:
            pass
        else:
            if self.
            role = cell.memory['role']
            if role == 'SEED':
                cell.specialize('SEED')
            elif role == 'stem':
                if cell.adjacent['LEFT'] == None:
                    
                
            
            
