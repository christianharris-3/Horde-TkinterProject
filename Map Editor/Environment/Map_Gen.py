

tiles = [(47, 220, 39), (84, 110, 8), (83, 223, 243), (137, 115, 36), (40, 204, 114), (113, 45, 95), (222, 138, 190), (115, 178, 112), (174, 242, 241), (216, 189, 233), (186, 185, 11), (171, 96, 108), (98, 188, 102), (146, 251, 20), (183, 83, 68), (118, 124, 243), (118, 121, 132), (243, 166, 224), (192, 95, 111), (16, 168, 143)]
rooms = {'1x1-1':{'tiles':{0,1,2,3},'pattern':[[{'used':True,'doors':[1,0,0,0]}]],'paths':1,'bias':0.5},
         '1x1-2L':{'tiles':{4,5},'pattern':[[{'used':True,'doors':[1,1,0,0]}]],'paths':2,'bias':0.4},
         '1x1-2I':{'tiles':{6,7},'pattern':[[{'used':True,'doors':[1,0,1,0]}]],'paths':2,'bias':0.4},
         '1x1-3':{'tiles':{8},'pattern':[[{'used':True,'doors':[1,1,1,0]}]],'paths':3,'bias':0.2},
         '1x1-4':{'tiles':{9},'pattern':[[{'used':True,'doors':[1,1,1,1]}]],'paths':4,'bias':0.1},
         
         '1x2-1.1':{'tiles':{10},'pattern':[[{'used':True,'doors':[2,0,0,0]},{'used':True,'doors':[1,0,2,0]}]],'paths':1,'bias':0.2},
         '1x2-1.2':{'tiles':{11},'pattern':[[{'used':True,'doors':[2,0,0,0]},{'used':True,'doors':[0,1,2,0]}]],'paths':1,'bias':0.15},
         '1x2-1.3':{'tiles':{12},'pattern':[[{'used':True,'doors':[2,0,0,0]},{'used':True,'doors':[0,0,2,1]}]],'paths':1,'bias':0.15},
         '1x2-2.1':{'tiles':{13},'pattern':[[{'used':True,'doors':[2,0,1,0]},{'used':True,'doors':[1,0,2,0]}]],'paths':2,'bias':0.1},
         '1x2-2.2':{'tiles':{14},'pattern':[[{'used':True,'doors':[2,1,1,0]},{'used':True,'doors':[0,0,2,0]}]],'paths':2,'bias':0.1},
         '1x2-2.3':{'tiles':{15},'pattern':[[{'used':True,'doors':[2,1,0,1]},{'used':True,'doors':[0,0,2,0]}]],'paths':2,'bias':0.1},
         '1x2-2.4':{'tiles':{16},'pattern':[[{'used':True,'doors':[2,1,0,0]},{'used':True,'doors':[1,0,2,0]}]],'paths':2,'bias':0.1},
         '1x2-3.1':{'tiles':{17},'pattern':[[{'used':True,'doors':[2,1,1,1]},{'used':True,'doors':[0,0,2,0]}]],'paths':3,'bias':0.1},
         '1x2-3.2':{'tiles':{18},'pattern':[[{'used':True,'doors':[2,1,0,1]},{'used':True,'doors':[1,0,2,0]}]],'paths':3,'bias':0.1},
         '1x2-3.3':{'tiles':{19},'pattern':[[{'used':True,'doors':[2,1,0,0]},{'used':True,'doors':[1,1,2,0]}]],'paths':3,'bias':0.1},
         
         }

def rotate_list(lis):
    new = copy.deepcopy(lis)
    new.reverse()
    n_lis = [[-1 for a in range(len(new))] for b in range(len(new[0]))]
    for i,a in enumerate(new):
        for j,b in enumerate(a):
            n_lis[j][i] = b
    return n_lis

class Map_maker():
    def __init__(self,rooms):
        self.rooms = rooms
        self.reset()
    def reset(self):
        self.used = []
        
    def get_random_room(self,used,paths):
        accepted = False
        while not accepted:
            total = sum([self.rooms[a]['bias'] for a in self.rooms])
            ran = random.random()*total
            for a in self.rooms:
                ran-=self.rooms[a]['bias']
                if ran<0:
                    if self.rooms[a]['paths'] in paths: accepted = True
                    break
            room = self.rooms[a]

        room['rotations'] = 0
        for a in range(random.randint(0,3)):
            room['rotations']+=1
            room['pattern'] = rotate_list(room['pattern'])
            for y in room['pattern']:
                for x in y:
                    x['doors'].insert(0,x['doors'].pop(-1))
        
        return room

    def draw_map(self,screen,start_x,start_y,scale=50,gap=10):
        pathw = scale/5
        extentions = [(scale,0,gap,scale),(0,scale,scale,gap),(-gap,0,gap,scale),(0,-gap,scale,gap)]
        paths = [(scale,scale/2-pathw/2,gap,pathw),(scale/2-pathw/2,scale,pathw,gap),(-gap,scale/2-pathw/2,gap,pathw),(scale/2-pathw/2,-gap,pathw,gap)]

        path_col = (40,40,40)
        
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != -1:
                    col = tiles[self.grid[y][x]['tile']]
                    pygame.draw.rect(screen,col,pygame.Rect(start_x+x*(scale+gap),start_y+y*(scale+gap),scale,scale))
                    for i,a in enumerate(self.grid[y][x]['doors']):
                        if a == 1: pygame.draw.rect(screen,path_col,pygame.Rect(start_x+x*(scale+gap)+paths[i][0],start_y+y*(scale+gap)+paths[i][1],paths[i][2],paths[i][3]))
                        elif a == 2: pygame.draw.rect(screen,col,pygame.Rect(start_x+x*(scale+gap)+extentions[i][0],start_y+y*(scale+gap)+extentions[i][1],extentions[i][2],extentions[i][3]))

    def attach_room(self,room,attach_point):
        possible_bindings = []
        for y in range(len(room['pattern'])):
            for x in range(len(room['pattern'][y])):
                if room['pattern'][y][x]['doors'][(attach_point[2]+2)%4] == 1:
                    possible_bindings.append([x,y])
        if len(possible_bindings)>0:
            worked = False
            for a in possible_bindings:
                inserted,path = self.insert_room(room,[attach_point[0]-a[0],attach_point[1]-a[1]])
                if inserted:
                    worked = True
                    break
            if worked:
                return True,path
        return False,[]

    def check_on_grid(self,x,y):
        return (x>-1 and y>-1 and x<len(self.grid[0]) and y<len(self.grid))
            
    def insert_room(self,room,pos,tile_index='r'):
        stored = copy.deepcopy(self.grid)
        if tile_index == 'r': tile = random.choice(tuple(room['tiles']))
        else: tile = room['tiles'].pop()
        dirr = [(1,0),(1,0),(-1,0),(0,-1)]
        new_paths = []
        source = True
        for y in range(len(room['pattern'])):
            for x in range(len(room['pattern'][y])):
                if (not self.check_on_grid(pos[0]+x,pos[1]+y)) or self.grid[pos[1]+y][pos[0]+x] != -1:
                    self.grid = stored
                    return False,[]
                r = room['pattern'][y][x]
                if r['used']:
                    print('PLATING ROOM',pos[0],pos[1],x,y)
                    self.grid[pos[1]+y][pos[0]+x] = {'doors':r['doors'],'tile':tile,'source':source}
                    source = False
                    for i,d in enumerate(dirr):
                        if r['doors'][i] == 1:
                            if self.check_on_grid(pos[0]+x+d[0],pos[1]+y+d[1]):
                                if self.grid[pos[1]+y+d[1]][pos[0]+x+d[0]] == -1:
                                    # add new path where door connects to empty tile
                                    print('new path',pos[0],x,d[0],pos[1],y,d[1])
                                    new_paths.append([pos[0]+x+d[0],pos[1]+y+d[1],i])
                                else:
                                    # stop if an adjacent tile has no door where current tile does
                                    if self.grid[pos[1]+y+d[1]][pos[0]+x+d[0]]['doors'][(i+2)%4] == 0:
                                        self.grid = stored
                                        return False,[]
                            else:
                                # stop if door connects to outside grid
                                self.grid = stored
                                return False,[]
        return True,new_paths
                        

    def make_map(self,max_rooms):
        self.grid = [[-1 for b in range(max_rooms)] for a in range(max_rooms)]
        start = [0,0]#int(max_rooms/3)]

        worked,paths = self.insert_room(self.rooms['1x1-1'],start,0)
        
        while len(paths)>0:
            print('paths:',paths)
            path = paths.pop(0)
            print('adding to:',path)
            game_loop()
            
            added = False
            attempts = 0
            while not added:
                attempts+=1
                if attempts>100:
                    break
                room = self.get_random_room([],[2,3,4])
                print('trying room:',room)
                worked,new_path = self.attach_room(room,path)
                if worked:
                    print('added',room,new_path)
                    paths+=new_path
                    added = True
                

