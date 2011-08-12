'''
This script attempts to parse a Mocha animated shape export.

Copyright (C) 2011  Dealga McArdle

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

you can contact me at blenderscripting.blogspot
'''

# coded verbosely for debug, thar be assumptions here.

import bpy
from mathutils import Vector
import re  

file_details = {}  


def XSpline_eval(points):
    ''' avoids using eval, this step might be a little paranoid
    
    XSpline_eval() takes a list of Point(*args) in the form of a string like
    (x,y,k1,k2,sBool) and converts it to a list of tuple(floats)
    
    straight eval was possible, but it introduces security vulnerabilities.
    
    '''
    
    point_list = []  
    for point in points:  
        point = point[1:-1]
        point = point.split(",")

        # LOW PRIORITY
        # [TODO] maybe rewrite to deal with the last param of point as a bool
        point_arguments = []
        for element in point:
            point_arguments.append(float(element))

        # convert to tuple, and append to list
        point_arguments = tuple(point_arguments)
        point_list.append(point_arguments)
    
    return point_list



def get_file_info(file):
    '''This checks file for information as described in file_details below'''

    file_validity_counter = 0

    # massive room for optimized code here. maybe join the first n lines and
    # run regular expressions here too! 
    for line in file:  
        current_line = line  
        
        # FPS
        if current_line.find("Units Per Second") != -1:
            fps = float(current_line.split()[-1])
            file_validity_counter += 1
    
        # source dimensions
        if current_line.find("Source Width") != -1:
            source_width = int(current_line.split()[-1])
            file_validity_counter += 1
        if current_line.find("Source Height") != -1:
            source_height = int(current_line.split()[-1])
            file_validity_counter += 1
    
        # aspect ratios
        if current_line.find("Source Pixel Aspect Ratio") != -1:
            source_px_aspect = float(current_line.split()[-1])
            file_validity_counter += 1
        if current_line.find("Comp Pixel Aspect Ratio") != -1:
            comp_aspect = float(current_line.split()[-1])
            file_validity_counter += 1

        # check up
        if file_validity_counter == 5:
            break    

    if file_validity_counter != 5:
        print("File contains unpredicted information, parsing ended")  
        return None

    global file_details
    file_details = {    "Frames Per Second": fps,
                        "Source Width": source_width,
                        "Source Height": source_height,
                        "Source Pixel Aspect Ratio": source_px_aspect,
                        "Comp Pixel Aspect Ratio": comp_aspect}
    
    print("Phase 1 of parsing complete, file details found, looking good")        
    return file_details



def parse_file(file):
    ''' this gathers the shape details, and frame number but does not 
    include much error checking yet 
    
    at present this does not parse translation/scale/sheer.
    '''
    # setup empty dictionary
    shapes_and_states = {}
    
    # keys: use strings for shape names like 'Shape data #1'
    # values: use lists to store
    shape_name = "Shape data "
    shape_track_token = 0
    key_to_check = ""
    
    for line in file:  
        current_line = line  

        # Parse:     #n	Shape data, where n is a number
        if current_line.find("Shape data\n") != -1:
            shape_data = re.search("(#\d+)\sShape data\n", current_line)
            if shape_data.group(1) != None:
                
                # add key if not present
                key_to_check = shape_name + shape_data.group(1)
                if key_to_check not in shapes_and_states:
                    shapes_and_states[key_to_check] = []
                else:
                    print("Duplicate shape names found, abort parsing")
                    return None
                

        # Parse: the content of the line containing the XSpline details
        if current_line.find("XSpline") != -1:
        
            # assumption, that frames are integer only, not subframe float
            frame = re.search("\s*(\d*)\s*XSpline", current_line)
            if frame.group(1) != None:
                frame = int(frame.group(1)) # -1
                  
            # digest the part of the line that deals with geometry 
            match = re.search("XSpline\((.+)\)\n", current_line)  
            line_to_strip = match.group(1)  
            points = re.findall('(\(.*?\))', line_to_strip)  
  
            # perhaps store the frame number with the xspline? necessary?
            states_of_shape = XSpline_eval(points)
                        
            # shapes_and_states[key_to_check].append(frames_and_states)
            shapes_and_states[key_to_check].append(states_of_shape)

    # cleanup before return to calling function         
    # if the file doesn't appear to contain any animated data that we
    # know how to parse, then the dictionary remains empty and we return None
    if len(shapes_and_states) == 0:
        return None
    else:
        return shapes_and_states


# helper routine
def get_coordinates_from_state(state):
    
    width = file_details['Source Width']
    height = file_details['Source Height']
    
    coord_list = []        
    for coordinate in state:
        x = coordinate[0] * width
        y = coordinate[1] * height
        coVec = Vector((x,y,0.0, 1.0))
        coord_list.append(coVec)
    return coord_list



def create_shape_and_keyframes(shape, frames):

    # create the base shape, the same as first shape on frame 1


    iterator = 0 
    print(shape)
    for state in frames:
        print("frame", iterator)
        print(get_coordinates_from_state(state))
                
        iterator+=1
        
    # ending shape.    
    print("-----")



def init_fileparsing(data_directory, data_file):
    fullpath = data_directory + data_file  

    print("="*50)
    print("Getting File Information for:", data_file)  

    file = open(fullpath)

    # check the file
    file_details = get_file_info(file)
    if file_details != None:
        for key in file_details:
            print(">", key, file_details[key])
    else:
        file.close()
        print("Exited file parsing routine")
        return

    # get all shape data (shapes/frames)
    shapes_and_states = parse_file(file)
    
    # whatever the result, we no longer need the file open on disk.
    file.close()

    if shapes_and_states != None:
        for shape in shapes_and_states:
            create_shape_and_keyframes(shape, shapes_and_states[shape])
    else:
        print("check the source file for congruency with desired format")
        print("Ending routine")
        return 
   
    # display some information, size of shape and how many frames each shape has
    print("gathered", len(shapes_and_states), "shapes")
    for shape in shapes_and_states:
        num_frames = len(shapes_and_states[shape])
        coords = len(shapes_and_states[shape][0])
        fdx = "frames of data and xspline("
        print(shape, "w/",num_frames,fdx,coords,"points )")
    
    return



# data_directory = 'C:/Users/zeffii\Downloads/' # windows    
data_directory = '/home/zeffii/Downloads/MOCHA/' # linux    
data_file = 'mocha2.ae'  

init_fileparsing(data_directory, data_file)