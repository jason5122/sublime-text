#!/bin/bash

# open -na Alacritty --args --working-directory "`(pwd)`" -e bash --login
# { alacritty msg create-window --working-directory "`(pwd)`" && open -a Alacritty; } || open -na Alacritty --args --working-directory "`(pwd)`" -e bash --login
# { alacritty msg create-window --working-directory "`(pwd)`" && open -a Alacritty; } || open -na Alacritty --args --working-directory "`(pwd)`" -e $SHELL --login
{ alacritty msg create-window --working-directory "$(pwd)" && open -a Alacritty; } || open -na Alacritty --args --working-directory "$(pwd)" -e $SHELL --login
