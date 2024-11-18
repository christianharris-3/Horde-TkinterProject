import pygame

class Camera:
    def __init__(self,target,display_rect,lock_on=False):
        self.display_rect = display_rect
        self.target = target
        self.x = self.target.x
        self.y = self.target.y
        self.zoom = 1

        self.lock_on = lock_on
        self.velocity = [0,0]
        self.acceleration_constant = 0.03
        
    def render(self,screen,mapp,entities,objects,projectiles,particles):
        Surf = pygame.Surface((self.display_rect.w,self.display_rect.h))
        Surf.fill((0,128,0))

        transformed = self.transform(mapp.tilemap.x,mapp.tilemap.y)
        subsurf_rect = pygame.Rect(-transformed[0],-transformed[1],self.display_rect.w,self.display_rect.h)
        map_surf = mapp.render_surf(subsurf_rect,objects)
        Surf.blit(map_surf,(0,0))

        
        for p in entities+particles+projectiles:
            p_surf = p.render_surf()
            Surf.blit(p_surf,self.transform(p.x*64-p_surf.get_width()/2,
                                               p.y*64-p_surf.get_height()/2))

            
        for p in entities:
            p.render_hud(Surf)
            p.mpos = self.screen_pos_to_world_pos(self.target.ui.mpos,mapp)
        
            
        screen.blit(Surf,self.display_rect.topleft)
        
    def set_display_rect(self,display_rect):
        self.display_rect = display_rect
    def transform(self,x=0,y=0,return_tuple=True):
        if not type(x) in [list,tuple]: pos = [x,y]
        else: pos = x
        ret = (pos[0]-self.x+self.display_rect.w/2,pos[1]-self.y+self.display_rect.h/2)
        
        if return_tuple:
            return ret
        else:
            return ret[0],ret[1]
    def screen_pos_to_world_pos(self,pos,mapp):
        return [pos[0]-self.display_rect.x+self.x-self.display_rect.w/2,
                pos[1]-self.display_rect.y+self.y-self.display_rect.h/2]

    def move(self):
        if self.lock_on:
            self.x = self.target.x
            self.y = self.target.y
        else:
            self.velocity[0]+=self.acceleration_constant*(self.target.x-self.x)
            self.velocity[1]+=self.acceleration_constant*(self.target.y-self.y)

            self.x+=self.velocity[0]
            self.y+=self.velocity[1]

            damping = 0.84-4*self.acceleration_constant
            
            self.velocity[0]*=damping
            self.velocity[1]*=damping





        
