import os
import sys
import json

location_2 = [
    ["x+5", "y", "w//2-1", "h"],
    ["x+w//2", "y", "w//2-1", "h"]
]
location_3 = [
    ["x+5", "y", "w//4-1", "h"],
    ["x+(w//4)", "y", "w//2-1", "h"],
    ["x+(w*3//4)", "y", "w//4-1", "h"],
    ["x+5", "y", "w*3//4-1", "h"],
    ["x+(w//4)", "y", "w*3//4-1", "h"],
]
location_3_eq = [
    ["x+5", "y", "w//3-1", "h"],
    ["x+(w//3)", "y", "w//3-1", "h"],
    ["x+(w*2//3)", "y", "w//3-1", "h"],
    ["x+5", "y", "w//3*2-1", "h"],
    ["x+(w//3)", "y", "w//3*2-1", "h"],
]
location_4 = [
    ["x+5", "y", "w//2-1", "h//2-1"],
    ["x+5", "y+h//2", "w//2-1", "h//2-1"],
    ["x+w//2", "y", "w//2-1", "h//2-1"],
    ["x+w//2", "y+h//2", "w//2-1", "h//2-1"],
    ["x+5", "y", "w//2-1", "h"],
    ["x+w//2", "y", "w//2-1", "h"]
]
location_5 = [
    ["x+5", "y", "w//3-1", "h//2-1"],
    ["x+5", "y+h//2", "w//3-1", "h//2-1"],
    ["x+5", "y", "w//3-1", "h"],
    ["x+(w//3)", "y", "w//3-1", "h"],
    ["x+(w*2//3)", "y", "w//3-1", "h//2-1"],
    ["x+(w*2//3)", "y+h//2", "w//3-1", "h//2-1"],
    ["x+(w*2//3)", "y", "w//3-1", "h"],
    ["x+5", "y", "w//3*2-1", "h"],
    ["x+(w//3)", "y", "w//3*2-1", "h"]
]
location_6 = [
    ["x+5", "y", "w//2-1", "h//4-1"],
    ["x+w//2", "y", "w//2-1", "h//4-1"],
    ["x+5", "y+h//4", "w//4-1", "h*3//4-1"],
    ["x+w//4", "y+h//4", "w//2-1", "h//2-1"],
    ["x+w//4", "y+h//4", "w//2-1", "h*3//4-1"],
    ["x+w*3//4", "y+h//4", "w//4-1", "h*3//4-1"],
    ["x+w//4", "y+h*3//4", "w//2-1", "h//4-1"]
]

temp_file = '/dev/shm/move_windows_time'

if __name__ == '__main__':
    if len(sys.argv)>1 and int(sys.argv[1])>=0:
        time = int(sys.argv[1])
    else:
        if os.path.exists(temp_file):
            with open(temp_file) as f:
                time = int(f.read().strip()) + 1
        else:
            time = 0
        if len(sys.argv)>1:
            time += int(sys.argv[1]) - 1
        with open(temp_file,"w") as f:
            f.write(str(time))
    monitor_file = "/tmp/mwtw_" + os.popen("xrandr |md5sum").read().strip().split()[0]
    if os.path.exists(monitor_file):
        with open(monitor_file) as f:
            monitor_list = json.load(f)
    else:
        monitor_list = []
        temp = os.popen("xrandr |grep -w connected|sed 's/ /\\n/g'|grep +").read().strip().split("\n")
        for i in range(0, len(temp)):
            if os.system("xrandr|grep -w %s|grep primary 1>/dev/null 2>/dev/null" % temp[i]) == 0:
                primary = i
                break
        seq = [primary]
        for i in range(0, len(temp)):
            if i != primary:
                seq.append(i)
        for j in seq:
            i = temp[j]
            monitor_list.append([int(i.split("x")[1].split("+")[1]), int(i.split("x")[1].split("+")[2]), int(i.split("x")[0]), int(i.split("x")[1].split("+")[0])])
            if j == primary:
                monitor_list[len(monitor_list)-1][3]-=56
                monitor_list[len(monitor_list)-1][1]+=8
        with open(monitor_file,"w") as f:
            json.dump(monitor_list, f)
    location_list = []
    for i in range(0, len(monitor_list)):
        f = lambda x:[i, x]
        h = monitor_list[i][3]
        w = monitor_list[i][2]
        r = w/h
        if h>2000:
            if w>7500: # 8K
                location_list.extend(map(f,location_6))
            elif r>2:  # high resolution ultra-wide
                location_list.extend(map(f,location_5))
            else:      # 4K
                location_list.extend(map(f,location_4))
        elif w>=5120:  # medium resolution ultra-wide
            location_list.extend(map(f,location_3_eq))
        elif w>= 2500 and r>2: # low resolution ultra-wide
            location_list.extend(map(f,location_3))
        else:         # normal
            location_list.extend(map(f,location_2))
    time %= len(location_list)
    x,y,w,h = monitor_list[location_list[time][0]]
    os.system("wmctrl -r :ACTIVE: -b remove,maximized_vert,maximized_horz")
    os.system("wmctrl -r :ACTIVE: -e 0,%d,%d,%d,%d" % tuple([eval(i) for i in location_list[time][1]]))

