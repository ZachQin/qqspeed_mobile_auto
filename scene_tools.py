import json
import os
import shutil
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import cv2


def show_rect(img, rect_list):
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    fig = plt.figure(figsize=(16, 10))
    img_ax = plt.axes()
    img_ax.imshow(rgb_img)
    for rect in rect_list:
        rect_patch = patches.Rectangle(rect[0:2], rect[2], rect[3], fill=False)
        img_ax.add_patch(rect_patch)
    plt.show()

def select_rect(img):
    result = None
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

    fig = plt.figure(figsize=(16, 10))
    img_ax = fig.add_axes([0.1, 0.1, 0.8, 0.6])
    img_ax.imshow(rgb_img)
    
    press = False
    lu = None
    rb = None
    lu_patch = None
    rb_patch = None
    rect_patch = None
    label = None
    turn = True

    def format_rect(lu, rb):
        x = lu[0]
        y = lu[1]
        w = rb[0]-lu[0]
        h = rb[1]-lu[1]
        if w < 0:
            x = x + w
            w = -w
        if h < 0:
            y = y + h
            h = -h
        return (int(x), int(y), int(w), int(h))

    def on_press(event):
        nonlocal press
        press = True

    def on_move(event):
        nonlocal press, turn, lu, rb, lu_patch, rb_patch, rect_patch, label
        if not press: return # 按住的时候才进入
        if event.inaxes is not img_ax: return # 点击图片区域才进入
        if turn:
            lu = (event.xdata, event.ydata)
            if lu == (None, None): return
            if rb_patch is not None:
                rb_patch.remove()
                rb_patch = None
            if lu_patch is not None:
                lu_patch.remove()
                lu_patch = None
            if label is not None:
                label.remove()
                label = None
            lu_patch = patches.Circle(lu, 20)
            img_ax.add_patch(lu_patch)
            if rect_patch is not None:
                rect_patch.remove()
                rect_patch = None
        else:
            rb = (event.xdata, event.ydata)
            if rb == (None, None): return
            if rb_patch is not None:
                rb_patch.remove()
            rb_patch = patches.Circle(rb, 20)
            img_ax.add_patch(rb_patch)
            if rect_patch is not None:
                rect_patch.remove()
                rect_patch = None
            rect = format_rect(lu, rb)
            rect_patch = patches.Rectangle(rect[0:2], rect[2], rect[3], fill=False)
            img_ax.add_patch(rect_patch)
            if label is not None:
                label.remove()
                label = None
            label = img_ax.text(0, 1.1, 'x: {x}, y: {y}, width: {width}, height: {height}'.format(x=rect[0], y=rect[1], width=rect[2], height=rect[3]), transform=img_ax.transAxes)
        event.canvas.draw()

    def on_release(event):
        nonlocal press, turn, lu, rb
        on_move(event)
        press = False
        if event.inaxes is img_ax:
            turn = not turn

    def button_ok(event):
        nonlocal lu, rb, fig, result
        if lu is not None and rb is not None:
            result = format_rect(lu, rb)
            plt.close()
        event.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_move)
    fig.canvas.mpl_connect('button_release_event', on_release)

    button_ax = fig.add_axes([0.46, 0.8, 0.08, 0.05])
    button = Button(button_ax, 'OK')
    button.on_clicked(button_ok)

    plt.show()
    return result

def default_json_dict(img_name):
    return {'class': 'default', 'priority': 0, 'tolerance': 5, 'rect_list': [], 'action_module': 'action', 'action_func':'action', 'img_name': img_name}

def load_json(json_path):
    json_dict = None
    try:
        with open(json_path, 'r') as f:
            json_dict = json.load(f)
    except FileNotFoundError as e:
        pass
    return json_dict

def save_json(json_dict, json_path):
    with open(json_path, 'w') as f:
        json.dump(json_dict, f, indent=4, sort_keys=True)


def _main(argv):  # pragma: no coverage
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-r', '--replace', action='store_true')
    parser.add_argument('-s', '--show', action='store_true')
    parser.add_argument('-p', '--path', required=True)
    parser.add_argument('-i', '--image', help='image file name.', default='p.png')
    parser.add_argument('-j', '--json', help='rectangles json file name.', default='config.json')
    cli_args = parser.parse_args(argv[1:])

    image_full_path = os.path.join(cli_args.path, cli_args.image)
    json_full_path = os.path.join(cli_args.path, cli_args.json)

    img = cv2.imread(image_full_path)
    if cli_args.add:
        rect = select_rect(img)
        if rect is None: return
        json_dict = load_json(json_full_path)
        if json_dict is None:
            json_dict = default_json_dict(cli_args.image)
        json_dict['rect_list'].append(rect)
        save_json(json_dict, json_full_path)
    if cli_args.replace:
        rect = select_rect(img)
        if rect is None: return
        shutil.copyfile('action_template.txt', os.path.join(cli_args.path, 'action.py'))
        json_dict = default_json_dict(cli_args.image)
        json_dict['rect_list'].append(rect)
        save_json(json_dict, json_full_path)
    if cli_args.show:
        show_rect(img, load_json(json_full_path)['rect_list'])

if __name__ == '__main__':  # pragma: no coverage
    _main(sys.argv)
