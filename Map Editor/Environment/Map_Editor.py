import os,json,math,copy,random

import pygame
from Environment.Map import *
from Environment.Environment_Data import Data
from Entities.Enemy import Slow_Zombie as Enemy
from Entities.Player import Player
from Camera import Camera
import PyUI as pyui

class Editor_Controller:
    def __init__(self,ui,x,y):
        self.ui = ui
        self.x = x
        self.y = y
        self.keybinds = {'UP':[pygame.K_w,pygame.K_UP],
                         'DOWN':[pygame.K_s,pygame.K_DOWN],
                         'LEFT':[pygame.K_a,pygame.K_LEFT],
                         'RIGHT':[pygame.K_d,pygame.K_RIGHT]}
    def control(self):
        self.speed = 10
        if self.get_pressed('UP'): self.y-=self.speed
        if self.get_pressed('DOWN'): self.y+=self.speed
        if self.get_pressed('LEFT'): self.x-=self.speed
        if self.get_pressed('RIGHT'): self.x+=self.speed
        
    def render_surf(self):
        surf = pygame.Surface((1,1))
        surf.set_alpha(0)
        return surf
    def edit(self,camera,mapp):
        if camera.display_rect.collidepoint(self.ui.mpos):
            pos = camera.screen_pos_to_world_pos(self.ui.mpos,mapp)
            if self.ui.mprs[0]:
                grid_pos = mapp.tilemap.world_pos_to_grid_pos(pos)
                mapp.tilemap.set_tile(grid_pos[0],grid_pos[1],self.ui.IDs['Tile_Picker'].active)
            elif self.ui.mprs[2]:
                grid_pos = mapp.tilemap.world_pos_to_grid_pos(pos)
                mapp.tilemap.set_tile(grid_pos[0],grid_pos[1],"None")

    def get_pressed(self,code):
        if code in self.keybinds:
            for k in self.keybinds[code]:
                if self.ui.kprs[k]:
                    return True
        return False

    def render_hud(self,*_): pass
        
class Map_Editor:
    def __init__(self,ui):
        self.ui = ui
        self.make_gui()

        self.pixel_world_ratio = 64
        self.map = Map(ui,self.pixel_world_ratio)
        self.entities = []
        self.entity_data = []
        self.wave_data = []
        self.difficulty = 1
        self.level_title = 'Title'
        self.controller = Editor_Controller(ui,0,0)
        self.camera = Camera(self.controller,pygame.Rect(200,10,990,880),True)

        self.zombies = ['Slow_Zombie','Fast_Zombie','Big_Zombie','Demon_Zombie','Chonk_Zombie']
        self.entity_holding = -1

    def game_tick(self,screen):
        screen.fill(pyui.Style.wallpapercol)
        self.camera.move()
        self.camera.render(screen,self.map,[self.controller]+self.entities,[],[],[])
        if self.edit_swapper.active == 'Tilemap':
            self.controller.edit(self.camera,self.map)
        elif self.edit_swapper.active == 'Entities':
            self.click_drag_entities()
        self.controller.control()
    def resize(self):
        self.camera.set_display_rect(pygame.Rect(200,10,self.ui.screenw-220,self.ui.screenh-20))
        
    def make_gui(self):
        self.edit_swapper = self.ui.makedropdown(10,15,['Tilemap','Entities','Waves'],width=180,dropsdown=False,command=self.swap_menu)

        self.ui.makebutton(15,820,'Save',width=160,command=lambda: self.ui.movemenu('save_map','down')),
        self.ui.makebutton(15,860,'Open',width=160,command=self.open_menu_init),
            
        #### Tile Map
        self.tilemap_editor = self.ui.makewindow(10,50,180,600,autoshutwindows=['tilemap_editor','entity_editor','wave_editor'],ID='tilemap_editor',bounditems=[
            self.ui.makedropdown(10,20,[a for a in Data.data.keys()],width=160,ID='Tile_Picker',layer=5),
            ])
        self.ui.makewindowedmenu(10,10,180,160,'save_map')
        self.ui.maketext(90,4,'{"Save" underlined=True}',menu='save_map',objanchor=('w/2',0)),
        self.ui.maketextbox(90,40,'',width=160,lines=3,objanchor=('w/2',0),menu='save_map',ID='save_textbox',command=self.save_file),
        self.ui.makebutton(90,120,'Save',objanchor=('w/2',0),menu='save_map',command=self.save_file),

        self.ui.makewindowedmenu(10,10,180,160,'open_map',ID='open_map_menu')
        self.ui.maketext(90,4,'{"Open" underlined=True}',menu='open_map',objanchor=('w/2',0)),
        self.ui.maketable(90,35,titles=['File Names'],menu='open_map',objanchor=('w/2',0),ID='files_open_table'),
        
        ### Entities
        self.entity_editor = self.ui.makewindow(10,50,180,700,autoshutwindows=['tilemap_editor','entity_editor','wave_editor'],ID='entity_editor',bounditems=[
            self.ui.makebutton(10,10,'Add Player',width=160,command=self.add_spider),
            self.ui.makescrollertable(10,50,titles=['Spiders'],width=160,ID='spider_table',pageheight=640),

            ])
        self.ui.makewindowedmenu(10,10,180,375,'edit_spider')
        self.ui.maketextbox(10,25,'',160,ID='edit_spider_name',command=self.pull_spider_info,attachscroller=False,menu='edit_spider',bounditems=[
            self.ui.maketext(0,-23,'Name')])

        self.ui.maketextbox(10,245,'0',160,ID='edit_spider_x',command=self.pull_spider_info,attachscroller=False,intscroller=True,numsonly=True,menu='edit_spider',bounditems=[
            self.ui.maketext(0,-23,'X pos')])
        self.ui.maketextbox(10,300,'0',160,ID='edit_spider_y',command=self.pull_spider_info,attachscroller=False,intscroller=True,numsonly=True,menu='edit_spider',bounditems=[
            self.ui.maketext(0,-23,'Y pos')])
        
        self.ui.makebutton(10,335,'Delete',command=self.delete_spider,menu='edit_spider')
        
        
    
        ### Wave Data
        self.wave_editor = self.ui.makewindow(10,50,1000,600,autoshutwindows=['tilemap_editor','entity_editor','wave_editor'],ID='wave_editor',bounditems=[
            self.ui.makescrollertable(10,50,data=[],titles=['Wave Title',"Spawn Rate",'Spawn Slower','Slow Z','Fast Z','Big Z','Demon Z','Chonk Z'],ID='wavetable',pageheight=500),
            self.ui.makebutton(10,10,'add row',command=self.add_wave),

            self.ui.maketext(155,15,'Difficulty:'),
            self.ui.maketextbox(260,10,'1',ID='difficultyinput',numsonly=True,commandifkey=True,command=self.store_difficulty),

            self.ui.maketext(155, 15, 'Level Title:'),
            self.ui.maketextbox(260, 10, '1', ID='titleinput', numsonly=True, commandifkey=True,
                                command=self.store_level_title),
            ])

        self.swap_menu()

    def add_wave(self,info=None):
        if not info:
            data = [f'Wave {len(self.ui.IDs["wavetable"].table)}',1,0.5,0,0,0,0,0]
        else:
            data = [info["Title"],info["Spawn_Rate"],info["Spawn_Slower"]]
            for z in self.zombies:
                for d in info["Zombies"]:
                    if d['Class'] == z:
                        data.append(d["Num"])
                        break
                else:
                    data.append(0)

        row = []
        key = 123#random.randint(10000,100000)
        for a in range(len(data)):
            row.append(self.ui.maketextbox(0,0,text=str(data[a]),command=self.store_wavedata,commandifkey=True,numsonly=a>0,
                                           ID=f'wavetabletextbox{key}/{a},{len(self.ui.IDs["wavetable"].table)}'))
        self.ui.IDs['wavetable'].row_append(row)
        self.store_wavedata()
    def store_wavedata(self):
        table = self.ui.IDs['wavetable'].table[1:]
        self.wave_data = []
        for row in table:
            try:
                self.wave_data.append({'Title':row[0].text,'Spawn_Rate':float(row[1].text),'Spawn_Slower':float(row[2].text),
                                       'Zombies':[]})
                for i,z in enumerate(self.zombies):
                    self.wave_data[-1]["Zombies"].append({'Class':z,'Num':int(row[3+i].text)})
            except:
                pass
    def store_difficulty(self):
        try:
            self.difficulty = float(self.ui.IDs["difficultyinput"].text)
        except:
            pass
    def store_level_title(self):
        self.level_title = self.ui.IDs['titleinput'].text

    def table_move_input(self,move=(0,1)):
        if self.edit_swapper.active == 'Waves':
            tb = self.ui.textboxes[self.ui.selectedtextbox].ID
            new_tb = tb.split('/')[0]+'/' + str(int(tb.replace(',','/').split('/')[1]) + move[0]) + ',' + str(int(tb.split(',')[1]) + move[1])
            if new_tb in self.ui.IDs:
                self.ui.IDs[new_tb].select()

    def open_menu_init(self):
        table = self.ui.IDs['files_open_table']
        files = os.listdir(resourcepath('Data/Maps'))
        data = []
        for f in files:
            if '.json' in f:
                func = pyui.funcer(self.open_file,name=resourcepath('Data\\Maps\\'+f))
                data.append([self.ui.makebutton(0,0,f.removesuffix('.json'),command=func.func)])
        table.data = data
        table.refresh()
        self.ui.IDs['open_map_menu'].setheight(table.height+35+10)
        
        
        self.ui.movemenu('open_map','down')
        
    def save_file(self):
        e_data = copy.deepcopy(self.entity_data)
        # for a in e_data:
        #     a["x_pos"]/=64
        #     a["y_pos"] /= 64
        dat = {'map':self.map.get_storable_map(),
               'entities':e_data,
               'wave_data':self.wave_data,
               'difficulty':self.difficulty,
               'level_title':self.level_title}
        
        with open(resourcepath('Data\\Maps\\'+self.ui.IDs['save_textbox'].text+'.json'),'w') as f:
            json.dump(dat,f)
            
        self.ui.menuback()
        
    def open_file(self,name):
        self.ui.IDs['save_textbox'].settext(name.split('\\')[-1].removesuffix('.json'))
        if name == '':
            dat = {'map':{'tilemap':[['Metal_Floor']],'pos':[0,0]},
                   'entities':{}}
        else:
            if not '.json' in name:
                name  = resourcepath('Maps\\'+name+'.json')
            with open(name,'r') as f:
                dat = json.load(f)
        self.map.load_map(dat['map']['tilemap'],dat['map']['pos'])
        self.entity_data = dat['entities']
        self.wave_data = dat['wave_data']
        self.difficulty = dat['difficulty']
        self.level_title = dat['level_title']
        self.refresh_entities()
        self.ui.menuback()

    def swap_menu(self):
        if self.edit_swapper.active == 'Tilemap':
            self.tilemap_editor.open()
        elif self.edit_swapper.active == 'Entities':
            self.entity_editor.open()
        elif self.edit_swapper.active == 'Waves':
            self.wave_editor.open()
            self.ui.IDs['wavetable'].wipe(False)
            for a in self.wave_data:
                self.add_wave(a)
            self.ui.IDs['difficultyinput'].settext(str(self.difficulty))
            self.ui.IDs['titleinput'].settext(str(self.level_title))

    def refresh_entities(self):
        data = []
        self.entities = []
        for i,info in enumerate(self.entity_data):
            func = pyui.funcer(self.edit_spider,index=i)
            data.append([self.ui.makebutton(0,0,info['ID'],command=func.func)])
            self.entities.append(Map_Editor.make_spider(self.ui,info))
        self.ui.IDs['spider_table'].data = data
        self.ui.IDs['spider_table'].refresh()
    def click_drag_entities(self):
        if self.ui.mprs[0]:
            mpos = self.camera.screen_pos_to_world_pos(self.ui.mpos,self.map)
            if self.entity_holding == -1:
                min_dis = math.inf
                for e in self.entities:
                    dis = ((mpos[0]-e.x*64)**2+(mpos[1]-e.y*64)**2)**0.5
                    if dis<min_dis:
                        min_dis = dis
                        if min_dis<100:
                            self.entity_holding = e
            else:
                self.entity_holding.x = int(mpos[0]/self.pixel_world_ratio)
                self.entity_holding.y = int(mpos[1]/self.pixel_world_ratio)
                self.entity_data[self.entities.index(self.entity_holding)]['x_pos'] = int(mpos[0]/self.pixel_world_ratio)
                self.entity_data[self.entities.index(self.entity_holding)]['y_pos'] = int(mpos[1]/self.pixel_world_ratio)
        else:
            if self.entity_holding!=-1:
                self.refresh_entities()
            self.entity_holding = -1

    def add_spider(self):
        dat = {'ID':'Player','x_pos':0,'y_pos':0}
        if len(self.entity_data)>0:
            dat['ID'] = 'Spider'+str(len(self.entity_data))
        self.entity_data.append(dat)

        self.refresh_entities()

    def make_spider(ui,info):
        try:
            if info['ID'] == 'Player':
                return Player(info['x_pos'],info['y_pos'])
            else:
                return Enemy(info['x_pos'],info['y_pos'])
        except:
            print('Failed to make '+info['ID'])
            return Enemy(0,0)
    def delete_spider(self):
        del self.entity_data[self.spider_edit_index]
        self.refresh_entities()
        self.ui.menuback()
    def edit_spider(self,index):
        self.spider_edit_index = index
        info = self.entity_data[index]
        self.ui.IDs['edit_spider_name'].settext(str(info['ID']))
        self.ui.IDs['edit_spider_x'].settext(str(info['x_pos']))
        self.ui.IDs['edit_spider_y'].settext(str(info['y_pos']))
        self.ui.movemenu('edit_spider','down')
    def pull_spider_info(self):
        index = self.spider_edit_index
        self.entity_data[index]['ID'] = self.ui.IDs['edit_spider_name'].text
        self.entity_data[index]['x_pos'] = int(float(self.ui.IDs['edit_spider_x'].text))
        self.entity_data[index]['y_pos'] = int(float(self.ui.IDs['edit_spider_y'].text))
        self.refresh_entities()



        
        

    
