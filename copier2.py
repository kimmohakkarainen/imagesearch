import os
import io

basepath = "\\\\192.168.255.11\\material\\ipad"
#basepath = "\\temp"

non_included_extensions = { 'jpg', 'jpeg', 'svg', 'png', 'gif', 'cr2', 'crw', 'mpeg', 'mpg', 'bmp', 'ico' }
extensions = set()
dir_count = 0

def recurseDirectory(path:str):
    global dir_count
    dir_count = dir_count + 1
    if dir_count % 1000 == 0:
        print('dir count ' + str(dir_count) + ' extensions ' + str(len(extensions)))
        #print(extensions)
    try:
        for ntr in os.scandir(path):
            if ntr.is_dir():
                recurseDirectory(ntr.path)
            elif ntr.is_file():
                parts = ntr.name.split(".")
                if len(parts) > 1:
                    extension = parts[len(parts) - 1].lower()
                    if extension in non_included_extensions:
                        pass
                    else:
                        extensions.add(extension)
    except Exception as exp:
        print(exp)


recurseDirectory(basepath)

with io.open('toberemoved.txt','w') as file:
    #file.writelines(extensions)
    for ext in extensions:
        file.write(ext + '\n')