#!/bin/bash

exists=false

# Does it exist already?
app="/Library/Management/BlackboardCollaborate/Blackboard Collaborate Launcher.app"  
userapp="~/Applications/Blackboard Collaborate Launcher.app"
installedversion=`/usr/bin/defaults read "$app/Contents/Info.plist" CFBundleShortVersionString`
  # /   (root directory)
if [ -e "$userapp" ]
then
  # App exists in homedir, make sure it's the right version
  userversion=`/usr/bin/defaults read "$userapp/Contents/Info.plist" CFBundleShortVersionString`
    # Is it the right version?
    if [ "$userversion" == "$installedversion"]
        then
        exists=true
    else
        # if Not, remove it
        /bin/rm -rf $userapp
    fi
fi

# if doesn't exist, copy it
if [ "$exists" = false ]
    then
    /bin/mkdir -p ~/Applications
    /bin/cp -R "$app" ~/Applications
fi