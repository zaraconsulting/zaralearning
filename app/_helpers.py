import glob, os

def clear_temp_dir():
    files = glob.glob('/temp/*')
    for f in files:
        os.remove(f)
    print('temp folder cleared')