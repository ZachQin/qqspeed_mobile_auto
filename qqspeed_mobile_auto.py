import importlib
import json
import os
import time

import numpy

import cv2
import mobile_action


def bin2img(bin):
    if bin is None:
        return None
    buffer = numpy.asarray(bytearray(bin),dtype='uint8')
    img = None
    try:
        img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    except Exception as e:
        img = None
    return img

def template_diff(template, img, rect_list, scene_name = None):
    mean_list = []
    for rect in rect_list:
        img_area = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2], :]
        template_area = template[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2], :]
        diff = cv2.absdiff(img_area, template_area)
        channel_mean = cv2.mean(diff)
        mean = sum(channel_mean)/img.shape[2]
        mean_list.append(mean)
    diff_result = sum(mean_list)/len(mean_list)
    if scene_name is not None:
        print(scene_name + ' diff result: ' + str(diff_result))
    return diff_result

class Scene(object):
    def __init__(self, name, cls, priority, tolerance, img, rect_list, action):
        self.name = name
        self.cls = cls
        self.priority = priority
        self.tolerance = tolerance
        self.img = img
        self.rect_list = rect_list
        self.action = action

def import_action(scene, module_name, func_name):
    module = importlib.import_module('scenes.' + scene + '.' + module_name)
    return getattr(module, func_name)

def load_scene():
    scene_list = []
    with os.scandir('scenes') as iterater:
        for entry in iterater:
            if entry.is_file():
                continue
            name = entry.name
            json_dict = None
            with open(os.path.join(entry.path, 'config.json')) as json_f:
                json_dict = json.load(json_f)
            cls = json_dict['class']
            priority = json_dict['priority']
            tolerance = json_dict['tolerance']
            img = cv2.imread(os.path.join(entry.path, json_dict['img_name']))
            rect_list = list(map(tuple, json_dict['rect_list']))
            action = import_action(name, json_dict['action_module'], json_dict['action_func'])
            scene = Scene(name, cls, priority, tolerance, img, rect_list, action)
            scene_list.append(scene)
    return scene_list

def main():
    scenes = load_scene()
    while True:
        img_bin = mobile_action.screencap()
        screen_img = bin2img(img_bin)
        if screen_img is None:
            print('No screen cap!')
            time.sleep(1)
            continue
        diffence_map = {scene: template_diff(scene.img, screen_img, scene.rect_list, scene_name = scene.name) for scene in scenes}
        min_scene = min(diffence_map, key = lambda k: (diffence_map[k], -k.priority))
        min_diffence = diffence_map[min_scene]
        if min_diffence < min_scene.tolerance:
            print('#### Match scene: {name}   diffence: {diffence}'.format(name=min_scene.name, diffence=min_diffence))
            min_scene.action(screen_img)
        else:
            time.sleep(0.5)
        # print('Match scene: {name}   diffence: {diffence}'.format(name=min_scene.name, diffence=min_diffence))
        # time.sleep(0.5)

if __name__ == '__main__':
    main()
