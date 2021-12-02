#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : createDatasets.py
# @Author  : jade
# @Date    : 20-7-24 上午9:52
# @Mailbox : jadehh@live.com
# @Software: Samples
# @Desc    :
from jade import *
import json
import base64
import shutil
import cv2


def sortPoints(points, label):
    x1, y1 = points[0][0], points[0][1]
    x2, y2 = points[1][0], points[1][1]
    x3, y3 = points[2][0], points[2][1]
    x4, y4 = points[3][0], points[3][1]
    x_list = [x1, x2, x3, x4]
    y_list = [y1, y2, y3, y4]
    y_min1 = 10000000
    y_min1_index = -1
    y_min2 = 10000000
    y_min2_inedx = -1
    for i in range(len(y_list)):
        y = y_list[i]
        if y < y_min1:
            y_min1 = y
            y_min1_index = i

    for i in range(len(y_list)):
        y = y_list[i]
        if i == y_min1_index:
            continue
        if y < y_min2:
            y_min2 = y
            y_min2_inedx = i

    point1 = (x_list[y_min1_index], y_list[y_min1_index])
    point2 = (x_list[y_min2_inedx], y_list[y_min2_inedx])

    if point1[0] > point2[0]:
        point_bottom_right = point1
        point_bottom_left = point2
    else:
        point_bottom_right = point2
        point_bottom_left = point1
    ymin3_index = 0
    ymin4_index = 0
    for i in range(4):
        if i != y_min1_index and i != y_min2_inedx:
            ymin3_index = i
    for i in range(4):
        if i != y_min1_index and i != y_min2_inedx and i != ymin3_index:
            ymin4_index = i
    point3 = (x_list[ymin3_index], y_list[ymin3_index])
    point4 = (x_list[ymin4_index], y_list[ymin4_index])

    if point3[0] > point4[0]:
        point_top_right = point3
        point_top_left = point4
    else:
        point_top_right = point4
        point_top_left = point3

    # print "label = {},左下角 {}, 左上角{}, 右上角{},右下角{}".format(label,point_bottom_left,point_top_left,point_top_right,point_bottom_right)

    return [point_bottom_left, point_top_left, point_top_right, point_bottom_right]


def readjsonContent(json_path):
    with open(json_path, "rb") as f:
        json_content = dict(json.load(f))
    results = []
    # print(json_path)
    for result in json_content["shapes"]:
        points = []
        label = result["label"]
        if label:
            if label[-1] == "U":
                label = label

            if label == "container":
                label = ""
            result_points = sortPoints(result["points"], label)
            for point in result_points:
                points.append([int(point[0]), int(point[1])])
            if len(label) > 0:
                content_result = {"transcription": label, "points": [[points[0][0], points[0][1]],
                                                                     [points[1][0], points[1][1]],
                                                                     [points[2][0], points[2][1]],
                                                                     [points[3][0], points[3][1]]]}
                # 结果为 '{"A": "a", "B": "b"}'
                results.append(content_result)
        else:
            print("错误的json,json path = {}".format(json_path))
            return json.dumps(results)

    return json.dumps(results)


def create_labelme_dataset(root_dir):
    file_list = os.listdir(root_dir)
    save_path = CreateSavePath(os.path.join(GetPreviousDir(root_dir), GetToday()))
    for file in file_list:
        image_path_list = GetFilesWithLastNamePath(os.path.join(root_dir, file), ".jpg")
        for image_path in image_path_list:
            if os.path.exists(os.path.join(os.path.join(root_dir, file), image_path.split(".")[0] + ".json")) is False:
                os.remove(os.path.join(os.path.join(root_dir, file), image_path))
            else:
                try:
                    shutil.copyfile(os.path.join(os.path.join(root_dir, file), GetLastDir(image_path)),
                                    os.path.join(save_path, GetLastDir(image_path)))

                    shutil.copyfile(os.path.join(os.path.join(root_dir, file), GetLastDir(image_path)[:-4] + ".json"),
                                    os.path.join(save_path, GetLastDir(image_path)[:-4] + ".json"))
                except Exception as e:
                    print(e)
    return save_path


def dettojson(root_path, save_path):
    save_path = CreateSavePath(os.path.join(save_path, GetToday()))
    txt_list = GetFilesWithLastNamePath(root_path, ".txt")
    for txt_name in txt_list:
        with open(os.path.join(root_path, txt_name), "r") as f:
            content_list = f.read().split("\n")
            for content in content_list:
                image_name = content.split("\t")[0]
                try:
                    results = json.loads(content.split("\t")[1])
                    image_path = os.path.join(root_path, image_name)
                    shutil.copy(image_path, os.path.join(save_path, GetLastDir(image_name)))
                    image = cv2.imread(image_path)
                    height, width = image.shape[0], image.shape[1]
                    image_base64 = cv2_base64(image)
                    json_content = {
                        "version": "4.4.0",
                        "flags": {},
                        "shapes": [],
                        "imageHeight": height,
                        "imageWidth": width,
                        "imageData": image_base64,
                        "imagePath": os.path.join(save_path, GetLastDir(image_name))
                    }
                    shapes = []

                    for object in results:
                        label_name = object["transcription"]
                        points = object['points']
                        new_points = []
                        for point in points:
                            new_points.append([float(point[0]), float(point[1])])
                        shape = {"label": label_name, "points": new_points, "group_id": None, "shape_type": "polygon",
                                 "flags": {}}
                        shapes.append(shape)
                    json_content["shapes"] = shapes
                    with open(os.path.join(save_path, GetLastDir(image_name)[:-4] + ".json"), "w") as f:
                        json.dump(json_content, f)
                except Exception as e:
                    print(e)


def createDatasets(root_path):
    if os.path.exists(os.path.join(root_path, "train_icdar2015_label.txt")) is True:
        os.remove(os.path.join(root_path, "train_icdar2015_label.txt"))
    if os.path.exists(os.path.join(root_path, "test_icdar2015_label.txt")) is True:
        os.remove(os.path.join(root_path, "test_icdar2015_label.txt"))
    years = os.listdir(root_path)
    with open(os.path.join(root_path, "train_icdar2015_label.txt"), "w") as f1:
        for year in years:
            if len(year.split("-")) > 1 and os.path.isdir(os.path.join(root_path, year)):
                with open(os.path.join(root_path, year, "train_icdar2015_label.txt"), "r") as f:
                    content_list = (f.read().split("\n"))[:-1]
                    for content in content_list:
                        new_c = year + "/" + content
                        f1.write(new_c + "\n")

    with open(os.path.join(root_path, "test_icdar2015_label.txt"), "w") as f1:
        for year in years:
            if len(year.split("-")) > 1 and os.path.isdir(os.path.join(root_path, year)):
                with open(os.path.join(root_path, year, "test_icdar2015_label.txt"), "r") as f:
                    content_list = (f.read().split("\n"))[:-1]
                    for content in content_list:
                        new_c = year + "/" + content
                        f1.write(new_c + "\n")


def removeNolabelDatasets(root_path):
    image_path_list = GetAllImagesPath(root_path)
    for image_path in image_path_list:
        if os.path.exists(os.path.join(root_path, GetLastDir(image_path)[:-4] + ".json")):
            result = readjsonContent(os.path.join(root_path, GetLastDir(image_path)[:-4] + ".json"))
            if result == '[]':
                print("删除{}".format(image_path))
                os.remove(os.path.join(root_path, GetLastDir(image_path)[:-4] + ".json"))
                os.remove(image_path)
        else:
            print("删除{}".format(image_path))
            os.remove(image_path)


def GetContaNumberPath(image_path_list):
    ContaNumber_list = []
    for file in image_path_list:
        json_result_list = json.loads(readjsonContent(file.split(".")[0] + ".json"))

        conta_number = json_result_list[0]["transcription"]
        for json_result in json_result_list:
            if len((json_result["transcription"])) == 11:
                conta_number = (json_result["transcription"])
        ContaNumber_list.append(conta_number)
    return ContaNumber_list


def SplitDataSets(image_path_list, ContaNumber_list,split_rate):
    repeat_list = []
    repeat_image_path_list = []
    train_image_file_list = []
    for i in range(len(image_path_list)):
        if ContaNumber_list[i] not in repeat_list:
            repeat_list.append(ContaNumber_list[i])
            train_image_file_list.append(image_path_list[i])
        else:
            repeat_image_path_list.append(image_path_list[i])
    if split_rate > len(train_image_file_list) / len(image_path_list): ##应该从repeat里面分出一部分给train_image_file_list
        extra_count = ( int((split_rate - len(train_image_file_list) / len(image_path_list)) * len(image_path_list)))
        extra_image_path_list = random.sample(repeat_image_path_list,extra_count)
        train_image_file_list.extend(extra_image_path_list)
        test_image_files = [file for file in repeat_image_path_list if file not in extra_image_path_list]
    else:
        test_image_files =  random.sample(image_path_list,int((1-split_rate)*len(image_path_list)))

    return train_image_file_list , test_image_files

def CreateTextDetDatasets(root_path, save_root_path, split_rate=0.9):
    ##　　
    removeNolabelDatasets(root_path)
    image_path_list = GetAllImagesPath(root_path)
    ContaNumber_list = GetContaNumberPath(image_path_list)
    save_path = CreateSavePath(os.path.join(save_root_path, GetLastDir(root_path)))
    save_image_path = CreateSavePath(os.path.join(save_path, "image"))
    if os.path.exists(os.path.join(save_path, "train_icdar2015_label.txt")):
        os.remove(os.path.join(save_path, "train_icdar2015_label.txt"))
    if os.path.exists(os.path.join(save_path, "test_icdar2015_label.txt")):
        os.remove(os.path.join(save_path, "test_icdar2015_label.txt"))
    index = 0
    ##分割数据集应该是从整体数据集中挑选出重复的数据

    train_image_files, test_image_files = SplitDataSets(image_path_list, ContaNumber_list,split_rate)

    progressBar = ProgressBar(len(train_image_files))
    for image_path in train_image_files:
        shutil.copyfile(image_path, os.path.join(save_image_path, GetLastDir(image_path)))
        result = readjsonContent(os.path.join(root_path, GetLastDir(image_path)[:-4] + ".json"))

        with open(os.path.join(save_path, "train_icdar2015_label.txt"), "a") as f:
            content = "image/" + GetLastDir(image_path) + "\t" + result
            f.write(content + "\n")
        progressBar.update()

    progresstestBar = ProgressBar(len(test_image_files))
    for image_path in test_image_files:
        shutil.copyfile(image_path, os.path.join(save_image_path, GetLastDir(image_path)))
        result = readjsonContent(os.path.join(root_path, GetLastDir(image_path)[:-4] + ".json"))

        with open(os.path.join(save_path, "test_icdar2015_label.txt"), "a") as f:
            content = "image/" + GetLastDir(image_path) + "\t" + result
            f.write(content + "\n")
        progresstestBar.update()
    createDatasets(save_root_path)

