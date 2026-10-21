cmake_minimum_required(VERSION 3.20)
project(BalloonFightRecompiled VERSION 0.1.0 LANGUAGES C CXX)

set(NESRECOMP_ROOT "${CMAKE_SOURCE_DIR}/.deps/nesrecomp" CACHE PATH "Pinned NESRecomp checkout")
set(BALLOON_FIGHT_ROM "${CMAKE_SOURCE_DIR}/private/balloon-fight-usa.nes" CACHE FILEPATH "Locally prepared USA ROM")
option(BALLOON_FIGHT_HEADLESS "Build without SDL video and audio" OFF)
option(BALLOON_FIGHT_ORACLE "Build the independent TriCNES comparison executable" OFF)

find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
if(NOT EXISTS "${NESRECOMP_ROOT}/runner/cyc/project.cmake")
    message(FATAL_ERROR "Run python3 tools/bootstrap.py to fetch the pinned NESRecomp revision.")
endif()
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/prepare_rom.py"
    "${BALLOON_FIGHT_ROM}" --check RESULT_VARIABLE rom_check)
if(NOT rom_check EQUAL 0)
    message(FATAL_ERROR "The supported local ROM is missing or does not match. Run tools/prepare_rom.py with your ROM or ZIP.")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${BALLOON_FIGHT_ROM}" "${CMAKE_SOURCE_DIR}/tools/prepare_rom.py")

set(NESRECOMP_HEADLESS "${BALLOON_FIGHT_HEADLESS}")
set(NESRECOMP_RECOMP_UI "OFF" CACHE STRING "Prototype uses the engine's basic SDL host")
set(NESRECOMP_GAME_VERSION "${PROJECT_VERSION}-prototype")
include("${NESRECOMP_ROOT}/runner/cyc/project.cmake")
set(host_options NO_RECOMP_UI)
if(BALLOON_FIGHT_HEADLESS)
    list(APPEND host_options HEADLESS)
endif()
nesrecomp_add_cycle_game(balloon_fight
    ROM "${BALLOON_FIGHT_ROM}"
    GAME_CONFIG "${CMAKE_SOURCE_DIR}/game.toml"
    PLAYERS 2 REGION NTSC ${host_options})
if(BALLOON_FIGHT_ORACLE)
    # The oracle helper expects cyc.cmake's paths in the calling scope.
    include("${NESRECOMP_ROOT}/runner/cyc/cyc.cmake")
    nesrecomp_cyc_add_oracle(balloon_fight_oracle)
    # The optional reference core retains C#-style implicit narrowing.
    target_compile_options(balloon_fight_oracle PRIVATE
        $<$<COMPILE_LANG_AND_ID:CXX,Clang,AppleClang>:-Wno-c++11-narrowing>)
endif()
