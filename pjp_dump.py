#!/usr/bin/env python2.7
import argparse
from pjp.classdir import ClassDir
from pjp.classfile import ClassFile
from pjp.jarfile import JarFile
from pjp.constantpool import ConstantClass
import glob
import pickle
import json
import zipfile
from sets import Set

def dump_class(jar_dir):
    jar_files = glob.glob("{0}/*.jar".format(jar_dir))
    class_groups = []
    index = 0
    for jar_file in jar_files:
        print("{}/{} {}".format(index, len(jar_files), jar_file))
        index += 1
        jar = JarFile(jar_file)
        for classfile in jar.classes:
            jclass = ClassFile(jar[classfile])
            for constant in jclass.constant_pool:
                if isinstance(constant, ConstantClass):
                    parts = constant.value.split("/")
                    length = len(parts)
                    key = ""
                    if length > 2:
                        key = ".".join(parts[:2])
                    elif length > 1:
                        key = ".".join(parts[:1])
                    else:
                        key = parts[0]

                    key = key.strip("[L")
                    if key not in class_groups:
                        class_groups.append(key)

    with open("classes_prefix.json", "wb") as f:
        json.dump(class_groups, f, indent=2)

def diff_class(jvm_lib_dir):
    f = open("classes_prefix.json","r")
    used_class_paths = json.load(f)

    jars = glob.glob("{}/*.jar".format(jvm_lib_dir))
    for jar in jars:
        class_paths =Set()
        jarfile = zipfile.ZipFile(jar)
        for file in jarfile.filelist:
            filename_parts = file.filename.split("/")
            length = len(filename_parts)
            if length > 2:
                class_path = ".".join(filename_parts[:-1])   
                class_paths.add(class_path)
        
        unused_class_paths=Set()
        for class_path in class_paths:
            used = False
            for used_class_path in used_class_paths:
                if class_path.startswith(used_class_path):
                    used = True
                    break
            if not used:
                unused_class_paths.add(class_path)
        
        unused = (len(unused_class_paths) == len(class_paths))
        
        print("{} total unused:{}".format(jar, unused))
        print(json.dumps(list(unused_class_paths), indent=4))

def main():
    parser = argparse.ArgumentParser(description='jar class handler')
    subparsers = parser.add_subparsers(dest="command");

    dump_parser = subparsers.add_parser("dump",help="dump jar classes")
    dump_parser.add_argument('jar_dir', help='jar directory')

    diff_parser = subparsers.add_parser("diff", help="diff jar classes")
    diff_parser.add_argument("jar_dir", help="jvm jars dir")
    args = parser.parse_args()

    if args.command == "dump":
        dump_class(args.jar_dir)
    elif args.command == "diff":
        diff_class(args.jar_dir)
        

if __name__ == '__main__':
    main()
