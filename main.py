# File selector Module
from tkinter import *
from tkinter import filedialog
# Select path for backup
root = Tk()
root.withdraw()
ORIG_DIR = filedialog.askdirectory()
BACKUP_DIR = filedialog.askdirectory()

def open_file():
    filepath1 = ORIG_DIR  # "C:/temp"

def save_file():
    filepath2 = BACKUP_DIR  # "C:/backups"

BACKUP_PREFIX = "Backup af filer"  # Name before date

# choose backup method: 'SIMPLE' OR 'BZ2' OR '7zip':
METHOD = '7zip'  # 7zip.exe required for 7zip

# in case of 7zip, specify 7z executable path:
SEVENZIPPATH = "C:/Program Files/7-Zip/7z.exe"  # location of by default "c:/Programs/7-Zip/7z.exe"


import os, time, shutil, sys, tarfile, subprocess, traceback

# Backup without compression
def backup_directory_simple(srcdir, dstdir):
    if os.path.exists(dstdir):
        exit_stop("backup path %s already exists!" % dstdir)
    try:
        shutil.copytree(srcdir, dstdir)
    except:
        print
        "Error while copying tree in %s to %s" % (srcdir, dstdir)
        print
        "Traceback:\n%s" % traceback.format_exc()
        return False
    return dstdir

# bz2 code
def backup_directory_bz2(srcdir, tarpath):
    if os.path.exists(tarpath):
        exit_stop("backup path %s already exists!" % tarpath)
    try:
        tar = tarfile.open(tarpath, "w:bz2")
        for filedir in os.listdir(srcdir):
            tar.add(os.path.join(srcdir, filedir), arcname=filedir)
        tar.close()
    except:
        print
        "Error while creating tar archive: %s" % tarpath
        print
        "Traceback:\n%s" % traceback.format_exc()
        return False
    return tarpath

# 7zip code
def backup_directory_7zip(srcdir, arcpath):
    if os.path.exists(arcpath):
        exit_stop("backup path %s already exists!" % arcpath)
    try:
        # -mx9 means maximum compression
        arglist = [SEVENZIPPATH, "a", arcpath, "*", "-r", "-mx9"]
        print("try running cmd:\n %s\nin directory\n %s" %
              (' '.join(arglist), srcdir))
        # run 7zip
        sp = subprocess.Popen(
            args=arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=srcdir)
    except:
        print
        "Error while running 7zip subprocess. Traceback:"
        print
        "Traceback:\n%s" % traceback.format_exc()
        return False
    # wait for process to terminate, get stdout and stderr
    stdout, stderr = sp.communicate()

    if stderr:
        print
        "7zip STDERR:\n%s" % stderr
        return False
    return arcpath

def any_key():
    print
    "Press any key to continue."
    getch()

def exit_stop(exitstring):
    print
    exitstring
    any_key()
    sys.exit(exitstring)

try:
    # Win32
    from msvcrt import getch
except ImportError:
    # UNIX
    def getch():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# build timestring, check settings and invoke corresponding backup function


timestr = time.strftime("_%y%m%d_%H%M%S", time.localtime())
if METHOD not in ["SIMPLE", "BZ2", "7zip"]:
    exit_stop("METHOD not 'SIMPLE' OR 'BZ2' OR '7zip'")
if not os.path.exists(ORIG_DIR):
    exit_stop("ORIG_DIR does not exist: %s" % os.path.abspath(ORIG_DIR))
if not os.path.exists(BACKUP_DIR):
    exit_stop("BACKUP_DIR does not exist: %s" % os.path.abspath(BACKUP_DIR))
else:
    print("write snapshot of\n  %s\nto\n  %s\nusing the %s method...\n" %
          (os.path.abspath(ORIG_DIR), os.path.abspath(BACKUP_DIR), METHOD))
    if METHOD == "SIMPLE":
        rv = backup_directory_simple(srcdir=ORIG_DIR,
                                     dstdir=os.path.join(BACKUP_DIR, BACKUP_PREFIX + timestr))
    elif METHOD == "BZ2":
        rv = backup_directory_bz2(srcdir=ORIG_DIR,
                                  tarpath=os.path.join(BACKUP_DIR,
                                                       BACKUP_PREFIX + timestr + ".tar.bz2"))
    else:
        try:
            if not os.path.exists(SEVENZIPPATH):
                exit_stop("7zip executable not found: %s" % SEVENZIPPATH)
        except NameError:
            exit_stop("variable SEVENZIPPATH not defined")
        rv = backup_directory_7zip(srcdir=os.path.abspath(ORIG_DIR),
                                   arcpath=os.path.abspath(os.path.join(BACKUP_DIR,
                                                                        BACKUP_PREFIX + timestr + ".7z")))


any_key()