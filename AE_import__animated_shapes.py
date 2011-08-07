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


import re  
  

def get_file_info(file):
    '''This checks file for information as described in file_details below'''

    file_validity_counter = 0

    # massive room for optimized code here. maybe join the first n lines and
    # run regular expressions here too! 
    for line in file:  
        current_line = line  
        
        # FPS
        if current_line.find("Units Per Second") != -1:
            fps = line_split = float(current_line.split()[-1])
            file_validity_counter += 1
    
        # source dimensions
        if current_line.find("Source Width") != -1:
            source_width = line_split = int(current_line.split()[-1])
            file_validity_counter += 1
        if current_line.find("Source Height") != -1:
            source_height = line_split = int(current_line.split()[-1])
            file_validity_counter += 1
    
        # aspect ratios
        if current_line.find("Source Pixel Aspect Ratio") != -1:
            source_px_aspect = line_split = float(current_line.split()[-1])
            file_validity_counter += 1
        if current_line.find("Comp Pixel Aspect Ratio") != -1:
            comp_aspect = line_split = float(current_line.split()[-1])
            file_validity_counter += 1

        # check up
        if file_validity_counter == 5:
            break    

    if file_validity_counter != 5:
        print("File contains unpredicted information, parsing ended")  
        return None
    
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


        # deal

        # Parse:     #1	Shape data        
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
                
                print(current_line)

        
                
        # TODO read this again.
        if current_line.find("XSpline") != -1:
        
            # record the frame number.
            
            frame = re.search("\s*(\d*)\s*XSpline", current_line)
            if frame.group(1) != None:
                frame = frame.group(1)
                print("frame:", frame)
          
          
            # pick part the part of the line that deals with geometry 
            match = re.search("XSpline\((.+)\)\n", current_line)  
              
            line_to_strip = match.group(1)  
            points = re.findall('(\(.*?\))', line_to_strip)  
              
            # shapes_and_states[key_to_check].append(frames_and_states_per_shape)  
              
            #print(len(points))  
            #for point in points:  
            #    print(point)  
            #print("="*40)          
    
    print(shapes_and_states)
          
    # TODO[ ]    
    # if the file doesn't appear to contain any animated data that we
    # know how to parse, then the dictionary remains empty or we return None






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
    parse_details = parse_file(file)

    #if parse_details != None:
    #    for shape in parse_details:
    #        print(shape)
        




    # remember to close the file
    file.close()    




# data_directory = 'C:/Users/zeffii\Downloads/' # windows    
data_directory = '/home/zeffii/Downloads/MOCHA/' # linux    
data_file = 'mocha2.ae'  

init_fileparsing(data_directory, data_file)