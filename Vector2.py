'''
Created on 15 May 2010

@author: David Schneider
'''

import math

class Vector2():
    '''
    Stores state and behaviour of a two-dimensional vector.
    '''

    def __init__(self, x=0.0, y=0.0):
        '''
        Constructor
        '''
        self.x = x
        self.y = y
        
    def __add__(self, vec2):
        return Vector2(self.x + vec2.x, self.y + vec2.y)
    
    def __sub__(self, vec2):
        return Vector2(self.x - vec2.x, self.y - vec2.y)
    
    def __mul__(self, val):
        return Vector2(self.x * val, self.y * val)
    
    def __div__(self, val):
        return Vector2(self.x / val, self.y / val)
    
    def length(self):        
        return math.sqrt(self.x*self.x + self.y*self.y)

    def normalise(self):
        length = self.length()
        self.x = self.x / length
        self.y = self.y / length