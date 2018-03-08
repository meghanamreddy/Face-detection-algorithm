'''
Created on 11-Nov-2013

@author: Meghana M Reddy
'''
import math

class Color(object):
    '''
    classdocs
    '''


    def __init__(self, rgb):
        '''
        Precompute and keep the normalized values for r, g and b calculated from the raw rgb values given in the argument rgb.
        Raw rgb - (R, G, B) where all three are integers in the range 0-255
        Also have the total raw RGB in case you want to recover the raw rgb values
        The other attribute (apart from total, and normalized rgb values) you would need is intensity - total/3
        '''
        self.tot_rgb = (float(rgb[0]) + float(rgb[1]) + float(rgb[2]))
        if (float(rgb[0]) + float(rgb[1]) + float(rgb[2])) == 0 :
            self.r = 0
            self.g = 0
            self.b = 0
        else :
            self.r = rgb[0]/self.tot_rgb
            self.g = rgb[1]/self.tot_rgb
            self.b = rgb[2]/self.tot_rgb
        self.intensity = self.tot_rgb/3

    def hue(self):
        '''
        Return the hue in radians - calculated as atan((sqrt(3)*(green-blue))/((red-green) + (red-blue)))
        The color values in the formula are the normalized color values
        You need to check if the denominator is zero and if it is return the appropriate value for the atan.
        '''
        if ((self.r-self.g) + (self.r-self.b) == 0) :
            return (math.pi)/2
        else :
            return math.atan((math.sqrt(3)*(self.g-self.b))/float((self.r-self.g) + (self.r-self.b)))
        


    def hue_degrees(self):
        '''
        Return the hue in degrees
        '''
        hue_radians = self.hue()
        hue_deg = hue_radians * 180/math.pi
        return hue_deg


    def rgb_abs(self):
        '''
        Recover and return the raw RGB values as a triple of integers
        '''
        rgb_r = self.r*self.tot_rgb
        rgb_g = self.g*self.tot_rgb
        rgb_b = self.b*self.tot_rgb
        raw_rgb = (rgb_r, rgb_g, rgb_b)
        return raw_rgb
    
