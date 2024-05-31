#!/bin/bash

# shellcheck disable=SC2086

#-----------------------------------
# definitions
#-----------------------------------
declare -r CMAKE="cmake"
# .buildsettings
declare -r SETTING_FILE_NAME=".buildsettings"
declare -r BUILD_DIR="BUILD_DIR"
declare -r PROJECT_HOME="PROJECT_HOME"
declare -a TEMPLATE_SETTINGS=(
	"${PROJECT_HOME}=."
	"${BUILD_DIR}=build"
)
# command options
declare -a SHORT_OPTIONS=(
	"c"
	"b"
	"g"
	"h"
	"d"
	"t:"
	"v"
)
declare -a LONG_OPTIONS=(
	"configure"
	"build"
	"generate"
	"help"
	"debug"
	"type:"
	"vebose"
	"clean"
	"cmake-args:"
)
#-----------------------------------
# variables
#-----------------------------------
# configuration values
declare buildDirectory=""
declare projectHome=""
# build target name
declare targetName=""
# build type
declare buildType=""
declare doConfiguration=true
declare doBuild=true
declare enableVerbose=false
declare doCleanup=false
declare cmakeArgs=""

declare IsDebug=false

#-----------------------------------
# utilities
#-----------------------------------
function println() {
	echo -e "${@}" >&2
}
function Exit() {
	exit
}
function FileExists() {
	if [ -e $1 ]; then
		return 1
	fi
	return 0
}

#-----------------------------------
# debug
#-----------------------------------
function PrintDebug() {
	if "${IsDebug}"; then
		println "[DEBUG]" "$@"
	fi
}

function PrintProperties() {
	PrintDebug "Project home: ${projectHome}"
	PrintDebug "Build:"
	PrintDebug "  Directory: ${buildDirectory}"
	PrintDebug "  Target: ${targetName}"
	PrintDebug "  Type: ${buildType}"
	PrintDebug "Cmake arguments: ${cmakeArgs}"
}

#-----------------------------------
# usage
#-----------------------------------
function Title() {
	echo "$@"
}
function Body() {
	echo -e "\t$*"
}
function Return() {
	echo ""
}
function Usage() {
	Title "Usage:"
	Body "build.sh [options] [build target]"
	Return

	Title "Options:"
	Body "-c --configure: Only configure cmake."
	Body "-b --build    : Only build."
	Body "-g --generate : Create \"${SETTING_FILE_NAME}\""
	Body "-t --type     : Specify build type. e.g.-t Debug"
	Body "-v --verbose  : Enable verbose output for cmake."
	Return

	Body "--clean       : Cleanup the repository."
	Body "--cmake-args  : Arguments passed to cmake. Concatnate with ','"
}

#-----------------------------------
# settings file
#-----------------------------------
declare -a configLines
function ImportSettingFile() {
	declare -r file="./${SETTING_FILE_NAME}"
	if [ ! -e ${file} ]; then
		return 1
	fi
	while read -r line; do
		configLines+=("${line}")
	done <${file}
	return 0
}

function GetSettingValue() {
	if [[ $1 =~ ("${2}"[ \t]*=[ \t]*)(.*) ]]; then
		echo "${BASH_REMATCH[2]}"
		return
	fi
	echo ""
}

function FindSetting() {
	for line in "${configLines[@]}"; do
		ret=$(GetSettingValue "${line}" "$1")
		if [ "${ret}" != "" ]; then
			echo "${ret}"
			return
		fi
	done
	echo ""
}

function Setup() {
	if ! ImportSettingFile; then
		println "'${SETTING_FILE_NAME}' does not exist."
		Exit
	fi
	# set configuration value
	projectHome=$(FindSetting "${PROJECT_HOME}")
	buildDirectory=$(FindSetting "${BUILD_DIR}")

	if [ ! -e ${projectHome} ]; then
		println "Project home does not exist. '${projectHome}'"
		Exit
	fi
	if [ ! -e "$(dirname ${buildDirectory})" ]; then
		println "Build directory does not exist. '$buildDirectory'"
		Exit
	fi
	if [ ! -e ${buildDirectory} ]; then
		mkdir ${buildDirectory}
	fi
}

#-----------------------------------
# commands
#-----------------------------------
function CreateSettingsFile() {
	if [ -e ./${SETTING_FILE_NAME} ]; then
		return
	fi
	for line in "${TEMPLATE_SETTINGS[@]}"; do
		echo "${line}" >>./${SETTING_FILE_NAME}
		echo ${line}
	done
	echo "Successfully created \"${SETTING_FILE_NAME}\"."
}

function Build() {
	declare command="${CMAKE} --build ${buildDirectory}"
	if [ "${targetName}" != "" ]; then
		command+=" --target ${targetName}"
	fi
	if [ "${buildType}" != "" ]; then
		command+=" --config ${buildType}"
	fi
	if "${enableVerbose}"; then
		command+=" -v"
	fi
	if [ "${cmakeArgs}" != "" ]; then
		command+=" ${cmakeArgs/,/ }"
	fi
	PrintDebug "Command: ${command}"
	${command}
	return $?
}

function Configure() {
	PrintDebug "Command: ${CMAKE} -S ${projectHome} -B ${buildDirectory}"
	${CMAKE} -S ${projectHome} -B ${buildDirectory}
	return $?
}

function ExecuteCommandWithoutError() {
	PrintDebug "$@" " 2>/dev/null"
	# shellcheck disable=SC2068
	$@ 2>/dev/null
	return $?
}

function Cleanup() {
	ExecuteCommandWithoutError "cd ${projectHome}"
	ExecuteCommandWithoutError "rm -rf ${buildDirectory}"
	ExecuteCommandWithoutError "cd ${OLDPWD}"
	println "Cleaned up project repository."
}

#-----------------------------------
# option
#-----------------------------------
function GetShortOptions() {
	IFS=""
	echo "${SHORT_OPTIONS[*]}"
}
function GetLongOptions() {
	IFS=","
	echo "${LONG_OPTIONS[*]}"
}

function ParseOptions() {
	# args=$(getopt -o cbghdt:v -l configure,build,generate,help,debug,type:,verbose -- "$@")
	args=$(getopt -o "$(GetShortOptions)" -l "$(GetLongOptions)" -- "$@")
	eval "set -- $args"

	while [ $# -gt 0 ]; do
		case $1 in
		-c | --configure)
			doBuild=false
			shift
			;;
		-b | --build)
			doConfiguration=false
			shift
			;;
		-g | --generate)
			CreateSettingsFile
			Exit
			;;
		-h | --help)
			Usage
			Exit
			;;
		-d | --debug)
			IsDebug=true
			shift
			;;
		-t | --type)
			buildType="$2"
			shift 2
			;;
		-v | --verbose)
			enableVerbose=true
			shift
			;;
		--clean)
			doCleanup=true
			shift
			;;
		--cmake-args)
			cmakeArgs=$2
			shift 2
			;;
		--)
			targetName=$2
			shift
			break
			;;
		esac
	done
}

#-----------------------------------
# entry point
#-----------------------------------
ParseOptions "$@"

Setup

PrintProperties # for debug

if "${doCleanup}"; then
	Cleanup
	Exit
fi

if "${doConfiguration}"; then
	if ! Configure; then
		Exit
	fi
fi

if "${doBuild}"; then
	if ! Build; then
		Exit
	fi
fi
