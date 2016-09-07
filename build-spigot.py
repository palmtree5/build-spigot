from subprocess import call
import requests
import os
import sys
import json
import shutil
from datetime import datetime as dt


def usr_help():
    """Outputs help to the user"""
    print("Remote Spigot build tool")
    print("build-spigot.py <version> <build_dir> <ram>")
    print("<version>: The Minecraft version for which to build Spigot")
    print("<ram>: The amount of ram java will get for running BuildTools.jar (example: 2G)")


def get_settings_from_file():
    with open("settings.json", "r") as fin:
        settings = json.load(fin)
    settings_t = (settings["mcver"], settings["ram"])
    return settings_t


def main(settings):
    mcver = settings[0]
    build_dir = "build"
    ram = "-Xmx" + settings[1]

    build_path = os.path.join(os.getcwd(), build_dir)
    app_path = os.getcwd()

    if os.path.isdir(build_path):
        print("Removing build directory")
        call(["rm", "-rf", build_path])
    print("Creating build directory")
    os.mkdir(build_path, mode=0o755)

    print("Changing to the build directory")
    os.chdir(build_path)

    print("Downloading BuildTools.jar")
    r = requests.get("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar")
    with open("BuildTools.jar", "wb") as bt_jar:
        bt_jar.write(r.content)
    java_path = shutil.which("java")
    print("Starting build...")
    call([java_path, ram, "-jar", "BuildTools.jar", "--rev", mcver])

    print("Build complete! Copying output to another directory")

    os.chdir(app_path)
    output_path = os.path.join(app_path, "completed")
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    os.chdir(output_path)
    timestamp = str(int(dt.now().timestamp()))
    cur_output_dir = os.path.join(output_path, timestamp)
    if not os.path.isdir(cur_output_dir):
        os.mkdir(cur_output_dir)
    os.chdir(cur_output_dir)
    for files in build_path:
        if files.endswith(".jar"):
            shutil.copy2(os.path.join(build_path, files), cur_output_dir)
    api_dir = os.path.join(build_path, "Spigot", "Spigot-API", "target")
    for files in api_dir:
        if files.endswith(".jar"):
            shutil.copy2(os.path.join(api_dir, files), cur_output_dir)
    print("Done copying files. Your files are located in " + cur_output_dir)



if __name__ == "__main__":
    if os.path.isfile("settings.json"):
        main(get_settings_from_file())
    elif len(sys.argv[1:]) == 2:
        main((sys.argv[1], sys.argv[2]))
    else:
        usr_help()
        raise RuntimeError("You must either create a settings.json or provide the arguments specified!")
