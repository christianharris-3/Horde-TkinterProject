import sys,os,pygame

def resourcepath(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def distance(point1,point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

def distance_to_rect(point,rect):
    x,y,w,h = rect
    if pygame.Rect(x,y,w,h).collidepoint(point): return 0
    if point[0]<x:
        if point[1]>y:
            if point[1]<y+h: return x-point[0]
            else: return distance(point,(x,y+h))
        else: return distance(point,(x,y))
    elif point[0]>x+w:
        if point[1]>y:
            if point[1]<y+h: return abs(point[0]-(x+w))
            else: return distance(point,(x+w,y+h))
        else: return distance(point,(x+w,y))
    else:
        if point[1]>y: return abs((y+h)-point[1])
        else: return abs(point[1]-y)

def rect_circle_collide(rec,circle):
    return distance_to_rect((circle[0],circle[1]),rec)<circle[2]
def rect_rect_collide(rec1,rec2):
    return pygame.Rect(rec1).colliderect(pygame.Rect(rec2))
def circle_circle_collide(circle1,circle2):
    return distance([circle1[0],circle1[1]],[circle2[0],circle2[1]])<circle1[2]+circle2[2]

def list_list_collide(lis1,lis2):
    for i in lis1:
        if list_obj_collide(lis2,i):
            return True
    return False

def list_obj_collide(lis,obj):
##    print(lis,obj)
    if len(obj) == 3:
        for j in lis:
            if len(j) == 3:
                if circle_circle_collide(obj,j): return True
            else:
                if rect_circle_collide(j,obj): return True
    else:
        for j in lis:
            if len(j) == 3:
                if rect_circle_collide(obj,j): return True
            else:
                if rect_rect_collide(j,obj): return True
    return False

def obj_to_colgrid_IDs(obj):
    if len(obj) == 3:
        top_left = map_pos_to_colgrid_pos(obj[0]-obj[2],obj[1]-obj[2])
        bottom_right = map_pos_to_colgrid_pos(obj[0]+obj[2],obj[1]+obj[2])
    else:
        top_left = map_pos_to_colgrid_pos(obj[0],obj[1])
        bottom_right = map_pos_to_colgrid_pos(obj[0]+obj[2],obj[1]+obj[3])
    IDs = []
    for y in range(top_left[1],bottom_right[1]+1):
        for x in range(top_left[0],bottom_right[0]+1):
            IDs.append(colgrid_pos_to_colgrid_ID(x,y))
    return IDs

def map_pos_to_colgrid_pos(x,y):
    grid_size = 100
    return int(x//grid_size),int(y//grid_size)
def colgrid_pos_to_colgrid_ID(x,y):
    big_num = 100000
    return int(x)*big_num+int(y)

def map_pos_to_colgrid_ID(x,y):
    colgrid_x,colgrid_y = map_pos_to_colgrid_pos(x,y)
    return colgrid_pos_to_colgrid_ID(colgrid_x,colgrid_y)




