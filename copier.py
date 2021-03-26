import os
import io
import shutil

basepath ="\\\\192.168.255.11\\material\\ipad"

sourcepath = "c:\\users\\kimmohakkarainen\\OneDrive - Exadeci Oy\\DCIM"

extensions = { 'jpg', 'jpeg', 'gif', 'bmp', 'png', 'svg', 'crw', 'cr2', 'mp3','mp4'}

def isImage(entry):
    parts = entry.name.split('.')
    if len(parts) > 1:
        lastpart = parts[len(parts) - 1].lower()
        return lastpart in extensions
    else:
        return False


def recurseDirectory(base, path):
    directory = '\\'.join(path)
    spath = base + '\\' + directory
    dircreated = False
    try:
        for entry in os.scandir(spath):
            if(entry.is_dir()):
                recurseDirectory(base, path + [entry.name])
            elif isImage(entry):
                if not dircreated:
                    try:
                        os.makedirs(basepath + '\\' + directory)
                    except Exception as exp:
                        print(exp)
                    dircreated = True
                targetfile = basepath + '\\' +  directory + '\\' + entry.name
                #print('copy ' + entry.path + ' =>  ' + targetfile)
                try:
                    shutil.copyfile(entry.path, targetfile)
                except Exception as exp:
                    print(exp)
    except Exception as exp:
        print(exp)


recurseDirectory(sourcepath, [])
