import cv2, os, random, argparse, logging, sys
from PIL import Image
import numpy as np
from datetime import datetime

def process_args(args):
    parser = argparse.ArgumentParser(description='This is for generate random handwritten math equation')
    parser.add_argument('--output-path', dest='output_path',
                        type=str, required=True,
                        help=('Output file path'))
    parser.add_argument('--output-path_txt', dest='output_path_txt',
                        type=str, default='default',
                        help=('Output text file path, note: default set to same as image output path'))
    parser.add_argument('--pad-size', dest='pad_size',
                        type=int, default=8,
                        help=('Pad the image to the top, left, bottom, right with whitespace of size Default=8.'
                        ))
    parameters = parser.parse_args(args)
    return parameters

def append_images(images, direction='horizontal',
                  bg_color=(255,255,255), aligment='center'):

    widths, heights = zip(*(i.size for i in images))

    if direction=='horizontal':
        new_width = sum(widths)
        new_height = max(heights)
    else:
        new_width = max(widths)
        new_height = sum(heights)

    new_im = Image.new('RGB', (new_width, new_height), color=bg_color)


    offset = 0
    for im in images:
        if direction=='horizontal':
            y = 0
            if aligment == 'center':
                y = int((new_height - im.size[1])/2)
            elif aligment == 'bottom':
                y = new_height - im.size[1]
            new_im.paste(im, (offset, y))
            offset += im.size[0]
        else:
            x = 0
            if aligment == 'center':
                x = int((new_width - im.size[0])/2)
            elif aligment == 'right':
                x = new_width - im.size[0]
            new_im.paste(im, (x, offset))
            offset += im.size[1]

    return new_im

def img_resize_open(imagepath):
    baseheight = 60
    if lst[lst_path.index(imagepath)] in operation_lst+symbol:
        baseheight = 45
    if lst[lst_path.index(imagepath)] == '-':
        baseheight = 6
    if lst[lst_path.index(imagepath)] == '.':
        baseheight = 10
    if lst[lst_path.index(imagepath)] == '=':
        baseheight = 18
    img = Image.open(imagepath)
    hpercent = (baseheight/float(img.size[1]))
    wsize = int((float(img.size[0])*float(hpercent)))
    img = img.resize((wsize,baseheight), Image.ANTIALIAS)
    return img

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    
    return False

lst = []
lst_path = []
operation_lst = ['times', '+', '-', 'div']
symbol = ['=', 'neq']

def main(args):
    parameters = process_args(args)
    output_path = parameters.output_path
    output_path_txt = parameters.output_path_txt
    pad_size = parameters.pad_size
    
    if output_path_txt == 'default':
        output_path_txt = output_path
    
    equation = [str(round(random.uniform(0, 99),1)), str(random.choice(operation_lst))
            , str(round(random.uniform(0, 99),1)), str(random.choice(symbol)), str(round(random.uniform(0, 999),2))]
    
    for elem in equation:
        if is_number(elem):
            for ele in elem:
                lst.append(ele)
            continue
        lst.append(elem)
        
    for elem in lst:
        img_dir = 'data/'+elem.replace('.','dot')
        img = random.choice([x for x in os.listdir(img_dir)
                   if os.path.isfile(os.path.join(img_dir, x)) and x != '.DS_Store'])
        lst_path.append(os.path.join(img_dir,img))
    
    image = img_resize_open(lst_path[0])
    for i in range(1,len(lst)):
        if lst[i] in operation_lst+symbol:
            image = append_images([image, img_resize_open(lst_path[i])], direction='horizontal', aligment='center',
                            bg_color=(255, 255, 255))
            continue

        image = append_images([image, img_resize_open(lst_path[i])], direction='horizontal', aligment='bottom',
                            bg_color=(255, 255, 255))
    filename = 'Math' + str(datetime.now())[0:-7].replace('-','').replace(' ','').replace(':','') + '.jpg'
    
    old_size = image.size
    new_size = (old_size[0]+pad_size*2, old_size[1]+pad_size*2)
    new_im = Image.new("RGB", new_size, color=(255,255,255)) 
    new_im.paste(image, ((new_size[0]-old_size[0])/2,
                      (new_size[1]-old_size[1])/2))
    
    new_im.save(os.path.join(output_path,filename))
    
    #output latex as .txt
    with open(os.path.join(output_path_txt, filename)+".txt", "w") as text_file:
        text_file.write(' '.join(lst).replace('times', '\\\\ t i m e s').replace('div', 
                                            '\\\\ d i v').replace('neq', '\\\\ n e q'))

if __name__ == '__main__':
    main(sys.argv[1:])

