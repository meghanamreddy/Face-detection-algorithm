'''
Created on 10-Nov-2013

@author: Meghana M Reddy
'''
import os

from color import Color
from pyimage import PyImage
from graph import Graph

class FaceDetector(object):
    '''
    classdocs
    '''
    def __init__(self, filename, block_size = 11, min_component_size = 11, majority = 0.56):
        '''
        Constructor - keeps input image filename, image read from the file as a PyImage object, block size (in pixels),
        threshold to decide how many skin color pixels are required to declare a block as a skin-block
        and min number of blocks required for a component. The majority argument says what fraction of
        the block pixels must be skin/hair colored for the block to be a skin/hair block - the default value is
        0.5 (half).
        '''
        self.image = PyImage(filename)
        self.block_sz = block_size
        self.min_blocks = min_component_size
        self.fraction_pixel = majority

   
    def skin_green_limits(self, red):
        '''
        Return the limits of normalized green given the normalized red component as a tuple (min, max)
        '''
        return ((-0.776*red*red + 0.5601*red + 0.18), (-1.376*red*red + 1.0743*red + 0.2))


    def is_skin(self, pixel_color):
        '''
        Given the pixel color (as a Color object) return True if it represents the skin color
        Color is skin if hue in degrees is (> 240 or less than or equal to 20) and 
        green is in the green limits and it is not white
        '''
        hue = pixel_color.hue_degrees()
        abs_rgb = pixel_color.rgb_abs()
        green = pixel_color.g
        green_limits = self.skin_green_limits(pixel_color.r)
        if ((hue > 240 or hue<= 20) and (green > green_limits[0] and green < green_limits[1]) and abs_rgb != (255, 255, 255)): 
            return True
        


    def is_hair(self, pixel_color):
        '''
        Return True if the pixel color represents hair - it is if intensity < 80 and ((B-G)<15 or (B-R)<15 or
        hue is between 20 and 40)
        '''
        hue = pixel_color.hue_degrees()
        intensity = pixel_color.intensity
        abs_rgb = pixel_color.rgb_abs()
        if (intensity < 80 and (abs_rgb[2] - abs_rgb[1] < 15) or (abs_rgb[2] - abs_rgb[0] < 15) or (hue > 20 and hue <40)) :
            return True


    def is_skin_hair_block(self, block, block_type):
        '''
        Return true if the block (given by the argument 'block' which is the coordinate-tuple for the top-left corner)
        is a skin/hair-block - it is if a majority (as per the threshold attribute) of the pixels in the block are
        skin/hair colored. 'block_type' says whether we are testing for a skin block ('s') or a hair block ('h).
        '''
        total_pixels = 0
        if block_type == 's' :
            num_pixels = 0
            for width in range(block[0], block[0] + self.block_sz) :
                for height in range(block[1], block[1] + self.block_sz) :
                    if 0<=width < self.image.size()[0] and 0<= height < self.image.size()[1] :
                        total_pixels += 1
                        pixel_cl = Color(self.image.get_rgba(width, height))
                        if self.is_skin(pixel_cl) :
                            num_pixels += 1
                        
        else :
            num_pixels = 0
            for width in range(block[0], block[0] + self.block_sz) :
                for height in range(block[1], block[1] + self.block_sz) :
                    if 0<=width < self.image.size()[0] and 0<= height < self.image.size()[1] :
                        total_pixels += 1
                        pixel_cl = Color(self.image.get_rgba(width, height))
                        if self.is_hair(pixel_cl) :
                            num_pixels += 1
        
        
        if (float(num_pixels)/total_pixels >= self.fraction_pixel) :
            return True


    def add_neighbour_blocks(self, block, graph):
        '''
        Given a block (given by the argument 'block' which is the coordinate-tuple for the top-left corner)
        and a graph (could be a hair or a skin graph), add edges from the current block to its neighbours
        on the image that are already nodes of the graph
        Check blocks to the left, top-left and top of the current block and if any of these blocks is in the
        graph (means the neighbour is also of the same type - skin or hair) add an edge from the current block
        to the neighbour.
        '''
        left_x = block[0] - self.block_sz
        left_y = block[1]
        topleft_x = block[0] - self.block_sz
        topleft_y = block[1] - self.block_sz
        top_x = block[0] 
        top_y = block[1] - self.block_sz
        topright_x = block[0] + self.block_sz
        topright_y = block[1] - self.block_sz
        
        for (block_x, block_y) in ((left_x, left_y), (topleft_x, topleft_y), (top_x, top_y), (topright_x, topright_y)) :
            if 0<=block_x < self.image.size()[0] and 0<= block_y < self.image.size()[1] :
                block2 = (block_x, block_y)
                graph.add_edge(block, block2)
        


    def make_block_graph(self):
        '''
        Return the skin and hair graphs - nodes are the skin/hair blocks respectively
        Initialize skin and hair graphs. For every block if it is a  skin(hair) block
        add edges to its neighbour skin(hair) blocks in the corresponding graph
        For this to work the blocks have to be traversed in the top->bottom, left->right order
        '''
        skin_graph = Graph()
        hair_graph = Graph()
        
        for x_cordinate in range(0, self.image.size()[0] -1, self.block_sz) :
            for y_cordinate in range(0, self.image.size()[1]-1, self.block_sz) :
                if self.is_skin_hair_block((x_cordinate, y_cordinate), 's') :
                    skin_graph.add_node((x_cordinate, y_cordinate))
                    self.add_neighbour_blocks((x_cordinate, y_cordinate), skin_graph)
                if self.is_skin_hair_block((x_cordinate, y_cordinate), 'h') :
                    hair_graph.add_node((x_cordinate, y_cordinate))
                    self.add_neighbour_blocks((x_cordinate, y_cordinate), hair_graph)
                    
        return skin_graph, hair_graph
                    
        


    def find_bounding_box(self, component):
        '''
        Return the bounding box - a box is a pair of tuples - ((minx, miny), (maxx, maxy)) for the component
        Argument 'component' - is just the list of blocks in that component where each block is represented by the
        coordinates of its top-left pixel.
        '''
        minx = component[0][0]
        miny = component[0][1]
        maxx = component[0][0]
        maxy = component[0][1]
        for i in range(0, len(component), 1):
            if component[i][0] < minx :
                minx = component[i][0]
            if component[i][1] < miny :
                miny = component[i][1]
            if component[i][0] > maxx :
                maxx = component[i][0]
            if component[i][1] > maxy :
                maxy = component[i][1]
                
        return ((minx, miny), (maxx, maxy))
    
    
    def skin_hair_match(self, skin_box, hair_box):
        '''
        Return True if the skin-box and hair-box given are matching according to one of the pre-defined patterns
        '''
        if skin_box[0][0] in range(hair_box[0][0], hair_box[1][0]) :
            if skin_box[1][0] in range(hair_box[0][0], hair_box[1][0]) :
                if skin_box[0][1] in range(hair_box[0][1], hair_box[1][1]) :
                    return True   #pattern 1,2,3,4,7,8,12,13
                
        if skin_box[0][1] in range(hair_box[0][1], hair_box[1][1]) :
            if skin_box[0][0] in range(hair_box[0][0], hair_box[1][0]) : 
                return True  #pattern 6
            elif skin_box[1][0] in range(hair_box[0][0], hair_box[1][0]) : 
                return True  #pattern 5
            
        if hair_box[0][1] in range(skin_box[0][1], skin_box[1][1]) :
            if hair_box[1][1] in range(skin_box[0][1], skin_box[1][1]) :
                if hair_box[1][0] in range(skin_box[0][0], skin_box[1][0]):
                    return True
                elif hair_box[0][0] in range(skin_box[0][0], skin_box[1][0]) : 
                    return True  # 9, 10, 11
            
        


    def detect_faces(self):
        '''
        Main method - to detect faces in the image that this class was initialized with
        Return list of face boxes - a box is a pair of tuples - ((minx, miny), (maxx, maxy))
        Algo: (i) Make block graph (ii) get the connected components of the graph (iii) filter the connected components
        (iv) find bounding box for each component (v) Look for matches between face and hair bounding boxes
        Return the list of face boxes that have matching hair boxes
        '''
        skin_graph, hair_graph = self.make_block_graph()
        skin_comp1 = skin_graph.get_connected_components()
        hair_comp1 = hair_graph.get_connected_components()
        skin_comp = []
        hair_comp = []
        list1 = len(skin_comp1)
        for i in range(0, list1):
            if len(skin_comp1[i]) > self.min_blocks :
                skin_comp += [skin_comp1[i]]
                list1 -= 1
        list1 = len(hair_comp1)
        for i in range(0, list1):
            if len(skin_comp1[i]) > self.min_blocks :
                hair_comp += [hair_comp1[i]]
                list1 -= 1
        face_list = []       
        for skin in skin_comp :
            for hair in hair_comp :
                skin_box = self.find_bounding_box(skin)
                hair_box = self.find_bounding_box(hair)
                if self.skin_hair_match(skin_box, hair_box):
                    face_list.append(skin_box)

        return face_list
            
    
    
    def mark_box(self, box, color):
        '''
        Mark the box (same as in the above methods) with a given color (given as a raw triple)
        This is just a one-pixel wide line showing the box.
        '''
        for i in range(box[0][0], box[1][0]):
            self.image.set(i, box[0][1], color)
            self.image.set(i, box[1][1], color)
            
        for i in range(box[0][1], box[1][1]):
            self.image.set(box[0][0], i, color)
            self.image.set(box[1][0], i, color)


    def mark_faces(self, marked_file):
        '''
        Detect faces and mark each face detected -- mark the bounding box of each face in red
        and save the marked image in a new file
        '''
        face_list = self.detect_faces()
        for i in face_list :
            self.mark_box(i, (255, 0 , 0))
        self.image.save(marked_file)

if __name__ == '__main__':
    detect_face_in = FaceDetector('faces-01.jpeg')
    detect_face_in.mark_faces('faces-01-marked.jpeg')
