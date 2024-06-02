#!/usr/bin/python3

""" cmake project builder """

import subprocess
import argparse
from dataclasses import dataclass
from typing import Any
import os
import locale
import json
import shutil

MY_NAME: str = "C Project Builder"


# -----------------------------------
# option
# -----------------------------------
class Application:
    @dataclass
    class Option:
        short: str = None
        long: str = None
        help: str = None
        needArgument: bool = False
        default: Any = ...

    @dataclass
    class PositionalArgument:
        name: str
        help: str
        required: bool = True
        default: Any = ...

    __parser: argparse.ArgumentParser

    def __init__(self):
        self.__parser = argparse.ArgumentParser(description=MY_NAME)

    def DefineArguments(
        self, arguments: tuple[PositionalArgument], options: tuple[Option]
    ) -> None:
        for arg in arguments:
            nargs = None if arg.required else "?"
            self.__parser.add_argument(
                arg.name, nargs=nargs, default=arg.default, help=arg.help
            )
        for opt in options:
            if opt.short is None:
                if opt.needArgument:
                    self.__parser.add_argument(
                        "--" + opt.long, help=opt.help, default=opt.default
                    )
                else:
                    self.__parser.add_argument(
                        "--" + opt.long, help=opt.help, action="store_true"
                    )
            else:
                if opt.needArgument:
                    self.__parser.add_argument(
                        "-" + opt.short,
                        "--" + opt.long,
                        help=opt.help,
                        default=opt.default,
                    )
                else:
                    self.__parser.add_argument(
                        "-" + opt.short,
                        "--" + opt.long,
                        help=opt.help,
                        action="store_true",
                    )

    def GetArguments(self):
        return self.__parser.parse_args()


# -----------------------------------
# settings file
# -----------------------------------
class BuildSetting:
    # constant
    FILE_NAME: str = "buildsettings.json"

    def __init__(self, directory: str) -> None:
        self.values: BuildSetting.Values = BuildSetting.Values()
        self.__path: str = os.path.join(directory, BuildSetting.FILE_NAME)

    def Load(self) -> None:
        if not os.path.exists(self.__path):
            raise RuntimeError(f"{BuildSetting.FILE_NAME} does not exist.")
        jsonObject = self.__import()
        self.values.projectHome = jsonObject[BuildSetting.Name.PROJECT_HOME]
        self.values.buildDirectory = jsonObject[BuildSetting.Name.BUILD_DIR]

    def Create(self) -> None:
        if os.path.exists(self.__path):
            return
        with open(self.__path, mode="w", encoding=locale.getpreferredencoding()) as f:
            json.dump(self.__TEMPLATE, f, indent=2)

    def __import(self) -> Any:
        with open(self.__path, encoding=locale.getpreferredencoding()) as f:
            return json.load(f)

    @property
    def __TEMPLATE(self) -> Any:
        return {
            BuildSetting.Name.PROJECT_HOME: ".",
            BuildSetting.Name.BUILD_DIR: "build",
        }

    @dataclass
    class Values:
        buildDirectory: str = ""
        projectHome: str = ""

    class Name:
        BUILD_DIR: str = "BuildDirectory"
        PROJECT_HOME: str = "ProjectHome"


# -----------------------------------
# static class: debug
# -----------------------------------
class Debug:
    enabled: bool = False

    @classmethod
    def Print(cls, message):
        if cls.enabled:
            print("[DEBUG]" + message)


# -----------------------------------
# command executer
# wrapper subprocess
# -----------------------------------
class SubProcessWrapper:
    @staticmethod
    def Run(args: tuple[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(args, check=True)

    @staticmethod
    def RunSimply(args: tuple[str]) -> int:
        try:
            return subprocess.run(args, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode

    @staticmethod
    def RunWithoutOutput(args: tuple[str]) -> int:
        try:
            Debug.Print(f"run command: {args}")
            return subprocess.run(
                args, shell=True, check=True, capture_output=True
            ).returncode
        except subprocess.CalledProcessError as e:
            Debug.Print(f"error {e.returncode}: {e.stderr}")
            return e.returncode


class Cmake:
    CMAKE: str = "cmake"

    def __init__(self, projectHome: str, buildDirectory: str) -> None:
        if not os.path.exists(projectHome):
            raise FileNotFoundError(f"ProjectHome does not exist. '{projectHome}'")
        if not os.path.exists(os.path.dirname(buildDirectory)):
            raise FileNotFoundError(
                f"BuildDirectory does not exist. '{buildDirectory}'"
            )
        self.__projectHome: str = projectHome
        self.__buildDirectory: str = buildDirectory

    def Configure(self) -> bool:
        command: tuple[str] = [
            Cmake.CMAKE,
            "-S",
            self.__projectHome,
            "-B",
            self.__buildDirectory,
        ]
        Debug.Print(f"command: {command}")
        self.__Enter()
        if SubProcessWrapper.RunSimply(command) == 0:
            return True
        self.__Exit()
        return False

    def Build(
        self,
        target: str = "all",
        buildType: str = None,
        enableVerbose: bool = False,
        cmakeArgs: tuple[str] = None,
    ):
        command: list[str] = [
            Cmake.CMAKE,
            "--build",
            self.__buildDirectory,
            "--target",
            target,
        ]
        if buildType is not None and buildType != "":
            command.extend(["--config", buildType])
        if enableVerbose:
            command.append("-v")
        if cmakeArgs is not None and cmakeArgs != [] and cmakeArgs != [""]:
            command.extend(cmakeArgs)
        Debug.Print(f"command: {command}")
        self.__Enter()
        if SubProcessWrapper.RunSimply(command) == 0:
            self.__Exit()
            return True
        self.__Exit()
        return False

    def Cleanup(self) -> None:
        shutil.rmtree(self.__buildDirectory)
        os.mkdir(self.__buildDirectory)

    def __Enter(self):
        os.chdir(self.__projectHome)

    def __Exit(self):
        os.chdir(os.getenv("OLDPWD"))


# -----------------------------------
# ProjectBuilder
# -----------------------------------
class ProjectBuilder:
    @dataclass
    class Controls:
        # self
        doConfiguration: bool = True
        doBuild: bool = True
        doCleanup: bool = False
        createSetting: bool = False
        isDebug: bool = False

    CMAKE: str = "cmake"

    def __init__(self) -> None:
        self.__system: Application = Application()
        self.__system.DefineArguments(
            self.__ArgumentDefinitions, self.__OptionDefinitions
        )
        self.__controls: ProjectBuilder.Controls = ProjectBuilder.Controls()
        self.response: str = ""
        self.__arguments: Any
        self.__setting: BuildSetting = BuildSetting(os.path.dirname(__file__))

    def Setup(self):
        self.__arguments = self.__system.GetArguments()
        self.__controls.isDebug = self.__arguments.debug
        self.__controls.doCleanup = self.__arguments.clean
        self.__controls.doConfiguration = self.__arguments.configure
        self.__controls.doBuild = self.__arguments.build
        self.__controls.createSetting = self.__arguments.create_settings
        Debug.enabled = self.__controls.isDebug
        self.__PrintArgument()
        self.__verifyControls()

    def __verifyControls(self) -> None:
        # どちらもfalseの時は、オプションなしなので、すべて実行する
        if not self.__controls.doConfiguration and not self.__controls.doBuild:
            self.__controls.doConfiguration = True
            self.__controls.doBuild = True

    def Run(self) -> None:
        if self.__controls.createSetting:
            self.__setting.Create()
            self.response = f"Successfully created '{BuildSetting.FILE_NAME}'"
            return
        self.__setting.Load()
        cmake = Cmake(
            self.__setting.values.projectHome,
            os.path.join(
                self.__setting.values.projectHome,
                self.__setting.values.buildDirectory,
            ),
        )
        if self.__controls.doCleanup:
            cmake.Cleanup()
            self.response = "Cleaned up project repository."
            return
        if self.__controls.doConfiguration:
            if not cmake.Configure():
                return
        if self.__controls.doBuild:
            if not cmake.Build(
                self.__arguments.target,
                self.__arguments.type,
                self.__arguments.verbose,
                self.__arguments.cmake_args.split(","),
            ):
                return

    @property
    def controls(self) -> Controls:
        return self.__controls

    @property
    def __ArgumentDefinitions(self) -> tuple[Application.PositionalArgument]:
        return [
            Application.PositionalArgument(
                name="target", required=False, default="all", help="Build target name."
            ),
        ]

    @property
    def __OptionDefinitions(self) -> tuple[Application.Option]:
        return [
            # short options
            Application.Option(
                short="c", long="configure", help="Only configure cmake."
            ),
            Application.Option(short="b", long="build", help="Only build."),
            Application.Option(
                short="v", long="verbose", help="Enable verbose output for cmake."
            ),
            Application.Option(
                short="t",
                long="type",
                needArgument=True,
                default="",
                help="Specify build type. e.g. -t=Debug",
            ),
            # long options
            Application.Option(long="clean", help="Cleanup the repository."),
            Application.Option(
                long="cmake-args",
                needArgument=True,
                default="",
                help="Arguments passed to cmake. e.g. --cmake-args=arg1,arg2...",
            ),
            Application.Option(
                long="create-settings", help=f"Create '{BuildSetting.FILE_NAME}'"
            ),
            Application.Option(long="debug", help="Output debug messages."),
        ]

    def __PrintArgument(self) -> None:
        Debug.Print(f"target: {self.__arguments.target}")
        Debug.Print("options:")
        Debug.Print(f"  configure: {self.__arguments.configure}")
        Debug.Print(f"  build: {self.__arguments.build}")
        Debug.Print(f"  verbose: {self.__arguments.verbose}")
        Debug.Print(f"  type: {self.__arguments.type}")
        Debug.Print(f"  clean: {self.__arguments.clean}")
        Debug.Print(f"  cmake-args: {self.__arguments.cmake_args}")
        Debug.Print(f"  create-settings: {self.__arguments.create_settings}")
        Debug.Print(f"  debug: {self.__arguments.debug}")


def main():
    app = ProjectBuilder()
    try:
        app.Setup()
        app.Run()
        if app.response != "":
            print(app.response)
    except Exception as e:
        print(f"{MY_NAME}: {e}")


if __name__ == "__main__":
    main()
