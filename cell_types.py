COSTS = {'ROOT': (100, 0), 'PHOTO': (100, 100), 'VASCULAR': (25, 25), 
         'REPR': (20, 20), 'STORE': (150, 150), 'SEED': (200, 20)}

GENERIC_INFO =  {'S_CONSUMPTION': 1, 'S_XFER': 20, 'S_MAX': 200, 
                 'W_CONSUMPTION': 0, 'W_XFER': 20, 'W_MAX': 200,
                  'PHOTO_FACTOR': 0, 'WATER_FACTOR': 0, 'COLOR': (50,205,50)}

ROOT_INFO   =   {'S_CONSUMPTION': 1, 'S_XFER': 40, 'S_MAX': 200, 
                 'W_CONSUMPTION': 0, 'W_XFER': 100,'W_MAX': 600,
                  'PHOTO_FACTOR': 0, 'WATER_FACTOR': 1, 'COLOR': (139,90,43)}
                
PHOTO_INFO  =   {'S_CONSUMPTION': 1, 'S_XFER': 100,'S_MAX': 500, 
                 'W_CONSUMPTION': 5, 'W_XFER': 20, 'W_MAX': 200,
                  'PHOTO_FACTOR': 1, 'WATER_FACTOR': 0, 'COLOR': (0,238,0)}

VASCULAR_INFO = {'S_CONSUMPTION': 1, 'S_XFER': 200,'S_MAX': 400, 
                 'W_CONSUMPTION': 1, 'W_XFER': 200,'W_MAX': 200,
                  'PHOTO_FACTOR': 0, 'WATER_FACTOR': 0, 'COLOR': (189,183,107)}
                
STORE_INFO  =   {'S_CONSUMPTION': 3, 'S_XFER': 400,'S_MAX': 800, 
                 'W_CONSUMPTION': 3, 'W_XFER': 400,'W_MAX': 400,
                  'PHOTO_FACTOR': 0, 'WATER_FACTOR': 0, 'COLOR': (255,165,79)}     
                
SEED_INFO   =   {'S_CONSUMPTION': 0, 'S_XFER': 0,  'S_MAX': 10000, 
                 'W_CONSUMPTION': 0, 'W_XFER': 0,  'W_MAX': 500,
                  'PHOTO_FACTOR': 0, 'WATER_FACTOR': 0, 'COLOR': (255,185,15)}

TYPES_INFO = {'GENERIC': GENERIC_INFO, 'ROOT': ROOT_INFO, 'PHOTO': PHOTO_INFO, 
              'VASCULAR': VASCULAR_INFO, 'STORE': STORE_INFO, 'SEED': SEED_INFO}