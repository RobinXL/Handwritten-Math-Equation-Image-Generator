import cv2, os, random, argparse, logging, sys, glob
from PIL import Image
import numpy as np
from datetime import datetime
import helper

def process_args(args):
    parser = argparse.ArgumentParser(description='This is for generate random handwritten math equation')
    
    parser.add_argument('--output-path', dest='output_path',
                        type=str, required=True,
                        help=('Output file path'))
    parser.add_argument('--output-path_txt', dest='output_path_txt',
                        type=str, default='default',
                        help=('Output text file path, note: default set to same as image output path'))
    parser.add_argument('--random-pad-size', dest='random_pad_size',
                        type=list, default=range(12,45),
                        help=('Pad the image to the top, left, bottom, right with whitespace of size random.'))
    parser.add_argument('--backgrounded', dest='backgrounded',
                        type=bool, default=False,
                        help=('random pick a background, default white'))
    parser.add_argument('--background-path', dest='background_path',
                        type=str, default="./backgrounds/",
                        help=('background image file path'))
    parser.add_argument('--batch-size', dest='batch_size',
                        type=int, default=1,
                        help=('Generate a batch of random images'))
    parser.add_argument('--random_text_size', dest='random_text_size',
                        type=list, default=range(80,150),
                        help=('add randomness to text size'))
    parser.add_argument('--downsample', dest='downsample',
                        type=int, default=1,
                        help=('downsample image size'))
    parameters = parser.parse_args(args)
    return parameters

def img_resize_open(imagepath, lst, lst_path, standard_height=100):
    baseheight = standard_height
    if lst[lst_path.index(imagepath)] in operation_lst+symbol:
        baseheight = int(standard_height*0.8)
    if lst[lst_path.index(imagepath)] == '-':
        baseheight = int(standard_height*0.15)
    if lst[lst_path.index(imagepath)] == '.':
        baseheight = int(standard_height*0.15)
    if lst[lst_path.index(imagepath)] == '=':
        baseheight = int(standard_height*0.4)
    img = Image.open(imagepath)
    hpercent = (baseheight/float(img.size[1]))
    wsize = int((float(img.size[0])*float(hpercent)))
    img = img.resize((wsize,baseheight), Image.ANTIALIAS)
    return img

def random_equation():
    #operation_lst = ['times', '+', '-', 'div']
    #symbol = ['=', 'neq']
    first_number = random.uniform(0, 99)
    second_number = random.uniform(0, 99)
    third_number = random.uniform(0, 99)
    if bool(random.getrandbits(1)):
        first_number = int(first_number)
    else:
        round_number = random.randint(1,3)
        first_number = round(first_number, round_number)
        
    if bool(random.getrandbits(1)):
        second_number = int(second_number)
    else:
        round_number = random.randint(1,3)
        second_number = round(second_number, round_number)
        
    if bool(random.getrandbits(1)):
        third_number = int(third_number)
    else:
        round_number = random.randint(1,3)
        third_number = round(third_number, round_number)
            
    equation = [str(first_number)
                  , str(random.choice(operation_lst))
                  , str(second_number)
                  , str(random.choice(symbol))
                  , str(third_number)]
    return equation

operation_lst = ['times', '+', '-', 'div']
symbol = ['=', 'neq']

def main(args):

    parameters = process_args(args)
    output_path = parameters.output_path
    output_path_txt = parameters.output_path_txt
    random_pad_size = parameters.random_pad_size
    backgrounded = parameters.backgrounded
    background_path = parameters.background_path
    batch_size = parameters.batch_size
    random_text_size = parameters.random_text_size
    downsample = parameters.downsample
    
    if output_path_txt == 'default':
        output_path_txt = output_path
    
    for batch in range(0, batch_size):
        pad_size = random.choice(random_pad_size)
        lst = []
        lst_path = []
        '''
        equation = [str(round(random.uniform(0, 99),1))
                  , str(random.choice(operation_lst))
                  , str(round(random.uniform(0, 99),1))
                  , str(random.choice(symbol))
                  , str(round(random.uniform(0, 999),2))]
        '''
        equation = random_equation()
        for elem in equation:
            if helper.is_number(elem):
                for ele in elem:
                    lst.append(ele)
                continue
            lst.append(elem)

        for elem in lst:
            img_dir = 'data/'+elem.replace('.','dot')
            img = random.choice([x for x in os.listdir(img_dir)
                       if os.path.isfile(os.path.join(img_dir, x)) and x != '.DS_Store'])
            lst_path.append(os.path.join(img_dir,img))
        #random text size 
        standard_height = random.choice(random_text_size)
        image = img_resize_open(lst_path[0], lst, lst_path, standard_height)
        for i in range(1,len(lst)):
            if lst[i] in operation_lst+symbol:
                image = helper.append_images([image, img_resize_open(lst_path[i], lst, lst_path, standard_height)], 
                                              direction='horizontal', aligment='center', 
                                              bg_color=(255, 255, 255))
                continue

            image = helper.append_images([image, img_resize_open(lst_path[i], lst, lst_path, standard_height)],
                                          direction='horizontal', aligment='bottom',
                                          bg_color=(255, 255, 255))
        filename = 'Math'+str(batch)+'_' + str(datetime.now())[0:-7].replace('-','').replace(' ','').replace(':','') + '.png'

        old_size = image.size
        new_size = (old_size[0]+pad_size*2, old_size[1]+pad_size*2)
        new_im = Image.new("RGB", new_size, color=(255,255,255)) 
        new_im.paste(image, ((new_size[0]-old_size[0])/2,
                          (new_size[1]-old_size[1])/2))
        
        open_cv_image = np.array(new_im) 
        
        if backgrounded:
            background_images = []
            for file in glob.glob(os.path.join(background_path,"*.png")):
                background_images.append(str(file))
            random_background = random.choice(background_images)
            
            picked_background = cv2.imread(random_background)
            height, width, channels = open_cv_image.shape
            height_bg, width_bg, channels_bg = picked_background.shape
            
            start_margin = random.randint(0, 100)
            
            #handle when image is wider than background
            if (width_bg-start_margin) < width:
                print '    too wide, resize ...'
                open_cv_image = helper.image_resize(open_cv_image, width=(width_bg-start_margin))
                height, width, channels = open_cv_image.shape
            crop_bkgd = picked_background[start_margin:height+start_margin, start_margin:width+start_margin]
            crop_bkgd = np.float32(crop_bkgd)
            open_cv_image = (crop_bkgd/255)*open_cv_image
            
        if downsample != 1:
            open_cv_image = helper.image_resize(open_cv_image, width=int(width/downsample))
        cv2.imwrite(os.path.join(output_path,filename), open_cv_image)
        
        #new_im.save(os.path.join(output_path,filename))
        latex_str = ' '.join(lst).replace('times', '\\times').replace('div', '\\div').replace('neq', '\\neq')
        print '    Generated latex: ', latex_str
        with open(os.path.join(output_path_txt, filename).replace('.png','')+".txt", "w") as text_file:
            text_file.write(latex_str)



    
if __name__ == '__main__':
    print 'Job started ...'
    main(sys.argv[1:])
    print 'Job done!'

