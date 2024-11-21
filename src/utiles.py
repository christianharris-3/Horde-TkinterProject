import math, datetime

class Vec:
    """
    Custom 2D vector class, used through-out project for 2d vector calculations e.g. velocity

    object stores only x and y component of Vector
    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __truediv__(self, other):
        """
        Divides both components of the vector by the input value
        :param other: float | int
        :return: Vec
        """
        return Vec(self.x / other, self.y / other)

    def __floordiv__(self, other):
        """
        Does Floor division to both components of the Vector
        :param other: float | int
        :return: Vec
        """
        return Vec(self.x // other, self.y // other)

    def __mul__(self, other):
        """
        Does multiplication to both components of the Vector
        :param other: float | int
        :return: Vec
        """
        return Vec(self.x * other, self.y * other)

    def __sub__(self, other):
        """
        Subtracts another vector off itself and returns the new vector
        :param other: Vec
        :return: Vec
        """
        return Vec(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """
        Adds another vector to itself and returns the new vector
        :param other: Vec
        :return: Vec
        """
        return Vec(self.x + other.x, self.y + other.y)
    def __neg__(self):
        """
        Returns a negated version of itself
        :return: Vec
        """
        return Vec(-self.x,-self.y)

    def __getitem__(self,item):
        """
        Allows the vector to be treated like a list of 2 values [x,y]
        :param item:  int
        :return: float | int
        """
        if item == 0: return self.x
        elif item == 1: return self.y
    def __setitem__(self,key,value):
        """
        Allows the vector to be treated like a list of 2 values [x,y]
        :param key: int
        :param value: float | int
        :return: None
        """
        if key%2 == 0: self.x = value
        else: self.y = value

    def __str__(self):
        """
        function that allows the object to be turned into a string and output
        :return: str
        """
        return f'<Vector2: ({self.x}, {self.y})>'
    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        """
        Allows the object to be iterated through and unpacked same as a tuple
        :return: tuple
        """
        return iter((self.x, self.y))

    @staticmethod
    def make_from_angle(angle,magnitude=1):
        """

        :param angle: float (radians)
        :param magnitude: float | int
        :return: Vec
        """
        return Vec(math.cos(angle),math.sin(angle))*magnitude

    def tuple(self,force_int=False):
        """
        returns itself as a tuple
        :param force_int: bool
        :return: tuple
        """
        if force_int: return (int(self.x),int(self.y))
        else: return (self.x,self.y)

    def length(self):
        """
        returns the length of the vector
        :return: float
        """
        return ((self.x)**2+(self.y)**2)**0.5
    def angle(self):
        """
        returns the angle of the vector
        :return: float (radians)
        """
        return math.atan2(self.y,self.x)

    def normalize(self):
        """
        sets the length of the vector to 1, if length is 0 then vector does not change
        :return: None
        """
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length
    def normalized(self):
        """
        returns a vector of length 1 and angle of current vector, if length is 0 then returns self
        :return: Vec
        """
        self.normalize()
        return self


class Rect:
    """
    Rect object used as a replacement for pygame.Rect object to handle collisions with other rects and points
    """
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    def colliderect(self,rect):
        return self.x<rect.x+rect.w and self.x+self.w>rect.x and self.y<rect.y+rect.h and self.y+self.h>rect.y
    def collidepoint(self,point):
        return point[0]>self.x and point[0]<self.x+self.w and point[1]>self.y and point[1]<self.y+self.h
    def __str__(self):
        return f'<Rect: (x:{self.x}, y:{self.y}, w:{self.w}, h:{self.h})>'
    def __repr__(self):
        return self.__str__()

class Hitbox:
    box_types = {1: 'Rect',
                 2: 'Circle',
                 3: 'Point',
                 4: 'List'}
    units_per_colgrid = 8
    big_num = 10000

    def set_x(self, x):
        self.x = x
        self.update()

    def set_y(self, y):
        self.y = y
        self.update()

    def set_ints(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.update()

    def update(self):
        self.calc_colcodes()

    def __eq__(self, other):
        return self.Get_Collide(other)

    def Get_Collide(self, hitbox):
        return self.function_map[hitbox.box_type](self, hitbox)

    def calc_colcodes(self):
        self.colcodes = []
        top_left = self.get_top_left() // Hitbox.units_per_colgrid
        bottom_right = self.get_bottom_right() // Hitbox.units_per_colgrid

        for y in range(int(top_left[1]), int(bottom_right[1]) + 1):
            for x in range(int(top_left[0]), int(bottom_right[0]) + 1):
                self.colcodes.append(self.colgrid_position_to_colcode((x, y)))

    def colgrid_position_to_colcode(self, pos):
        return pos[0] * self.big_num + pos[1]

    @staticmethod
    def _collide_rect_rect(rect1, rect2):
        return rect1.rect.colliderect(rect2.rect)

    @staticmethod
    def _collide_rect_circle(rect, circle):
        return rect.corners.Get_Collide(circle) or circle.corners.Get_Collide(rect)

    @staticmethod
    def _collide_rect_point(rect, point):
        return rect.rect.collidepoint((point.x, point.y))

    @staticmethod
    def _collide_circle_circle(circle1, circle2):
        return (circle1.x - circle2.x) ** 2 + (circle1.y - circle2.y) ** 2 < (circle1.radius + circle2.radius) ** 2

    @staticmethod
    def _collide_circle_point(circle, point):
        return (circle.x - point.x) ** 2 + (circle.y - point.y) ** 2 < circle.radius** 2

    @staticmethod
    def _collide_hitbox_list(hitbox, list_):
        for h in list_:
            if hitbox.Get_Collide(h):
                return True
        return False


class RectHitbox(Hitbox):
    box_type = 1
    function_map = {1: Hitbox._collide_rect_rect,
                    2: Hitbox._collide_rect_circle,
                    3: Hitbox._collide_rect_point,
                    4: Hitbox._collide_hitbox_list}

    def __init__(self, x, y, width, height):
        self.set_info(x, y, width, height)

    def __str__(self):
        return f'<RectHitbox x:{self.x},y:{self.y},w:{self.width},h:{self.height}>'

    def set_info(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.update()

    def set_ints(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.width = int(self.width)
        self.height = int(self.height)
        self.update()

    def set_width(self, width):
        self.width = width
        self.update()

    def set_height(self, height):
        self.height = height
        self.update()

    def update(self):
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.corners = ListHitbox((self.x, self.y), (self.x + self.width, self.y),
                                  (self.x + self.width, self.y + self.height), (self.x, self.y + self.height))
        self.calc_colcodes()

    def get_top_left(self):
        return Vec(self.x, self.y)

    def get_bottom_right(self):
        return Vec(self.x + self.width, self.y + self.height)


class CircleHitbox(Hitbox):
    box_type = 2
    function_map = {1: lambda circle, rect: Hitbox._collide_rect_circle(rect, circle),
                    2: Hitbox._collide_circle_circle,
                    3: Hitbox._collide_circle_point,
                    4: Hitbox._collide_hitbox_list}

    def __init__(self, x, y, radius):
        self.set_info(x, y, radius)

    def __str__(self):
        return f'<CircleHitbox x:{self.x},y:{self.y},r:{self.radius}>'

    def set_info(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.update()

    def set_ints(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.radius = int(self.radius)
        self.update()

    def set_radius(self, radius):
        self.radius = radius
        self.update()

    def update(self):
        self.corners = ListHitbox((self.x, self.y - self.radius), (self.x + self.radius, self.y),
                                  (self.x, self.y + self.radius), (self.x - self.radius, self.y))
        self.calc_colcodes()

    def get_top_left(self):
        return Vec(self.x - self.radius, self.y - self.radius)

    def get_bottom_right(self):
        return Vec(self.x + self.radius, self.y + self.radius)


class PointHitbox(Hitbox):
    box_type = 3
    function_map = {1: lambda point, rect: Hitbox._collide_rect_point(rect, point),
                    2: lambda point, circle: Hitbox._collide_circle_point(circle, point),
                    3: lambda *x: False,
                    4: Hitbox._collide_hitbox_list}

    def __init__(self, x, y):
        self.set_info(x, y)

    def set_info(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def calc_colcodes(self):
        self.colcodes = [self.colgrid_position_to_colcode((self.x // Hitbox.units_per_colgrid,
                                                           self.y // Hitbox.units_per_colgrid))]


class ListHitbox:
    box_type = 4
    function_map = {1: lambda list_, rect: Hitbox._collide_hitbox_list(rect, list_),
                    2: lambda list_, circle: Hitbox._collide_hitbox_list(circle, list_),
                    3: lambda list_, point: Hitbox._collide_hitbox_list(point, list_),
                    4: Hitbox._collide_hitbox_list}

    def __init__(self, *hitboxes):
        self.hitboxes = []
        self.unpack(hitboxes)

    def __getitem__(self, item):
        return self.hitboxes[item]

    def unpack(self, hitboxes):
        for h in hitboxes:
            if type(h) in [RectHitbox, CircleHitbox, PointHitbox]:
                self.hitboxes.append(h)
            elif type(h) in [list, tuple]:
                if not type(h[0]) in [list, tuple]:
                    if len(h) == 4:
                        self.hitboxes.append(RectHitbox(h[0], h[1], h[2], h[3]))
                    elif len(h) == 3:
                        self.hitboxes.append(CircleHitbox(h[0], h[1], h[2]))
                    elif len(h) == 2:
                        self.hitboxes.append(PointHitbox(h[0], h[1]))
                else:
                    self.unpack(h)

    def Get_Collide(self, hitbox):
        return self.function_map[hitbox.box_type](self, hitbox)

    def calc_colcodes(self):
        self.colcodes = []
        for h in self.hitboxes:
            h.calc_colcodes()
            self.colcodes += h.colcodes

    def set_ints(self):
        for h in self.hitboxes:
            h.set_ints()

# Class used to convert between Pixel positions/sizes to a custom scaled Coordinate system
class Coords:
    scale_factor = 80
    @staticmethod
    def pixel_to_world(pixels):
        return pixels/Coords.scale_factor

    @staticmethod
    def world_to_pixel(world):
        return world * Coords.scale_factor

    @staticmethod
    def pixel_to_world_coords(pixel_pos):
        return Vec(pixel_pos[0],pixel_pos[1])/Coords.scale_factor

    @staticmethod
    def world_to_pixel_coords(world_pos):
        return Vec(world_pos[0], world_pos[1])*Coords.scale_factor

def get_now():
    timestamp = datetime.datetime.now()
    datelist = str(timestamp.date()).split('-')
    datelist.reverse()
    datestr = '/'.join(datelist)
    timelist = str(timestamp.time()).split('.')[0].split(':')[:2]
    timestr = str(int(timelist[0])%12)+':'+timelist[1]+['am','pm'][int(timelist[0])//12]
    return datestr, timestr

def get_difficulty_data(difficulty=1):
    return {'Zombie_Damage': 1 * difficulty,
            'Zombie_Health': 1 * difficulty,
            'Zombie_Speed': 1 * difficulty,
            'Coin_Multiplier': round(1/max([difficulty,0.01])),
            'Natural Healing': False}