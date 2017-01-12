#!/bin/bash
. /DuckboxDisk/j00zek-NP/activePaths.config

daemonDir=$NPpath/plugins/IPTVplayer-port/IPTVdaemon
pluginDir=$NPpath/plugins/neutrinoIPTV/neutrinoIPTV
publicGitDir=$GITroot/crossplatform_iptvplayer/IPTVplayer

############################## Syncing GITLAB ##############################
if [ ! -d ~/Archive/iptvplayer-GitLab-master-version ];then
  mkdir -p ~/Archive
  echo 'Cloning...'
  git clone https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2.git ~/Archive/iptvplayer-GitLab-master-version
else
  echo 'Syncing GitLab...'
  cd ~/Archive/iptvplayer-GitLab-master-version
  git pull
fi
if [ ! -d ~/Archive/iptvplayerXXX-GitLab-master-version ];then
  echo 'Cloning XXX host...'
  git clone https://gitlab.com/iptv-host-xxx/iptv-host-xxx.git ~/Archive/iptvplayerXXX-GitLab-master-version
else
  echo 'Syncing GitLab XXX host...'
  cd ~/Archive/iptvplayerXXX-GitLab-master-version
  git pull
fi
############################## Syncing neutrinoIPTV ##############################
echo 'Syncing neutrinoIPTV...'
cd ~/Archive/iptvplayer-GitLab-master-version/

subDIR='components'
  [ -e $publicGitDir/i$subDIR ] && rm -rf $publicGitDir/i$subDIR/* || mkdir -p $publicGitDir/i$subDIR
  cp -a ~/Archive/iptvplayer-GitLab-master-version/IPTVPlayer/$subDIR/* $publicGitDir/i$subDIR
subDIR='tools'
  [ -e $publicGitDir/i$subDIR ] && rm -rf $publicGitDir/i$subDIR/* || mkdir -p $publicGitDir/i$subDIR
  cp -a ~/Archive/iptvplayer-GitLab-master-version/IPTVPlayer/$subDIR/* $publicGitDir/i$subDIR

  rm -rf $publicGitDir/ihosts

subDIRs="cache icons/logos hosts iptvdm libs locale"
for subDIR in $subDIRs
do
  [ -e $publicGitDir/$subDIR ] && rm -rf $publicGitDir/$subDIR/* || mkdir -p $publicGitDir/$subDIR
  cp -a ~/Archive/iptvplayer-GitLab-master-version/IPTVPlayer/$subDIR/* $publicGitDir/$subDIR
done

subDIRs="icomponents itools hosts libs scripts iptvdm"
for subDIR in $subDIRs
do
  #ln -sf ../__init__.py $publicGitDir/$subDIR/__init__.py
  touch $publicGitDir/$subDIR/__init__.py
done
cp -a ~/Archive/iptvplayerXXX-GitLab-master-version/IPTVPlayer/hosts/* $publicGitDir/hosts/
cp -f ~/Archive/iptvplayer-GitLab-master-version/IPTVPlayer/version.py $publicGitDir
wersja=`cat ./IPTVPlayer/version.py|grep 'IPTV_VERSION='|cut -d '"' -f2`
sed -i "s/^name=.*$/name=IPTV for Neutrino @j00zek v.$wersja/" $pluginDir/neutrinoIPTV.cfg
sed -i "s/^name.polski=.*$/name.polski=IPTV dla Neutrino @j00zek w.$wersja/" $pluginDir/neutrinoIPTV.cfg
echo "$wersja">$daemonDir/version
############################## logos structure & names ##############################
rm -f $publicGitDir/icons/*
mv -f $publicGitDir/icons/logos/*.png $publicGitDir/icons/
cp -a ~/Archive/iptvplayerXXX-GitLab-master-version/IPTVPlayer/icons/logos/XXXlogo.png $publicGitDir/icons/XXX.png
rm -rf $publicGitDir/icons/logos/
rm -rf $publicGitDir/icons/favourites*
cd $publicGitDir/icons/
for myfile in `ls ./*logo.png`
do
  newName=`echo $myfile|sed 's/logo//'`
  mv -f $myfile $newName
done
############################## hosts names ##############################
cd $publicGitDir/hosts/
rm -f ./list.txt
for myfile in `ls ./*.py`
do
  newName=`echo $myfile|sed 's/host//'`
  [ $myfile == $newName ] || mv -f $myfile $newName
done
############################## Adapt congig.py file ##############################
myFile=$publicGitDir/icomponents/iptvconfigmenu.py
sed -i '/class ConfigMenu(ConfigBaseWidget)/,$d' $myFile
#remove unnecesary stuff
sed -i 's;from iptvpin import IPTVPinWidget;;g
  
  ' $myFile
#own settings
sed -i 's;\(^.*ListaGraficzna.*default[ ]*=[ ]*\)True\(.*$\);\1False\2; 
  s;\(^.*showcover.*default[ ]*=[ ]*\)True\(.*$\);\1False\2; 
  s;\(^.*autoCheckForUpdate.*default[ ]*=[ ]*\)True\(.*$\);\1False\2; 
  s;\(^.*wgetpath.*default = \)"";\1"wget"; 
  s;\(^.*f4mdumppath.*default = \)"";\1"f4mdump"; 
  s;\(^.*rtmpdumppath.*default = \)"";\1"rtmpdump"; 
  ' $myFile

############################## making paths unique also on fat partitions #######################################################################
subDIRs="cache icomponents icons hosts libs scripts itools iptvdm locale"
for subDIR in $subDIRs
do
  [ -e $daemonDir/$subDIR ] || ln -sf $publicGitDir/$subDIR $daemonDir/$subDIR
done

############################## cleaning unused components #######################################################################################
echo 'Cleaning not used components from scripts...'
cd $publicGitDir
for myfile in `find -type f -name '*.py'`
do
  #echo $myfile
  
  sed -i "s;\(from .*\.\)components\(\.iptvplayerinit\);\1dToolsSet\2;g" $myfile #use own fake initscript
  sed -i "s;\(from .*\.\)tools\(\.iptvtools\);\1dToolsSet\2;g" $myfile #use own fake tools script
  sed -i "s;\(from .*\.\)components\.recaptcha_v2widget;\1dToolsSet.recaptcha_v2widget;g" $myfile #use own fake capcha
  toDel='MessageBox';[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='ConfigBaseWidget';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='ConfigHostsMenu';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='IPTVDirectorySelectorWidget';	[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='IPTVSetupMainWidget';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='Screen';			[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='VirtualKeyBoard';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='Label';			[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='ConfigListScreen';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='boundFunction';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='IPTVUpdateWindow';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='ActionMap';			[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='ConfigExtMoviePlayer';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  toDel='IPTVMultipleInputBox';		[[ `grep -c $toDel<$myfile` -gt 1 ]] || sed -i "/import .*$toDel/d" $myfile
  #toDel='self.console_appClosed_conn';	[[ `grep -q $toDel<$myfile` ]] || sed -i "/$toDel/d" $myfile
  #toDel='self.console_stderrAvail_conn';[[ `grep -q $toDel<$myfile` ]] || sed -i "/$toDel/d" $myfile
  
  #adding missing
  toAdd='iptvplayerinit import TranslateTXT as _';         [[ `grep -c "$toAdd"<$myfile` -ge 1 ]] || sed -i "/ihost import IHost/a from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvplayerinit import TranslateTXT as _" $myfile
  
  #probably to del later ;)
  #toDel='eConsoleAppContainer';		[[ `grep -c $toDel<$myfile` -ge 1 ]] && echo $myfile #sed -i "s/\(^.*$toDel\)/#\1/g" $myfile
  sed -i 's/\(raise BaseException\)("\(.*\)")/printDBG("\1(\2)")/g' $myfile
  #sed -i "s/\(getListForItem begin\)\(['\"]+\)/\1 Index=%d, selItem=%s \2 % (Index,str(selItem))/g" $myfile

  # NEW folders structure
  sed -i "s;\(from .*\.\)components\(.*\);\1icomponents\2;g" $myfile #new folders structure to workarround with fat issues
  sed -i "s;\(from .*\.\)tools\(.*\);\1itools\2;g" $myfile #new folders structure to workarround with fat issues
  sed -i "s;\(import .*\.\)components\(.*\);\1icomponents\2;g" $myfile #new folders structure to workarround with fat issues
  sed -i "s;\(import .*\.\)tools\(.*\);\1itools\2;g" $myfile #new folders structure to workarround with fat issues
  sed -i "s;\(import .*\dToolsSet.\)itools\(.*\);\1iptvtools\2;g" $myfile #new folders structure to workarround with fat issues
done
#removing local imports from the list
echo 'Removing some hosts and adding couple new 3rd party...'
cd $publicGitDir

#specific for hosts
sed -i "s/\(_url.*hostXXX.py\)/\1DISABLED/g" $publicGitDir/hosts/XXX.py
############################## Syncing contrib apps ##############################
#echo 'Syncing contrib apps...'
#wget -q http://iptvplayer.pl/resources/bin/sh4/exteplayer3_ffmpeg3.0 -O $publicGitDir/bin/sh4/exteplayer3
#wget -q http://iptvplayer.pl/resources/bin/sh4/uchardet -O $publicGitDir/bin/sh4/uchardet
############################## Keep only interesting hosts ##############################
cd $publicGitDir
#step 1 remove all definitevely unwanted
HostsList='anime chomikuj favourites disabled blocked localmedia wolnelekturypl'
for myfile in $HostsList
do
  rm -rf ./hosts/*$myfile*
  rm -rf ./icons/*$myfile*
done
cp -f $NPpath/plugins/IPTVplayer-port/hostrafalcool1.py $publicGitDir/hosts/rafalcool1.py
############################## copying to GIT public repo to fit license ##############################
#echo 'Syncing public GIT...'
#cp -a $publicGitDir/* $GITroot/cmdline_iptvplayer/
#rm -rf $GITroot/cmdline_iptvplayer/dToolsSet
#rm -f $GITroot/cmdline_iptvplayer/IPTVdaemon.py
#rm -f $GITroot/cmdline_iptvplayer/testcmdline.py
#rm -f $GITroot/cmdline_iptvplayer/cmdlineIPTV.py

###################### step 2 create lua list with titles
cd $publicGitDir
echo "HostsList={ ">$pluginDir/luaScripts/hostslist.lua
echo "# -*- coding: utf-8 -*-
HostsList=[ ">$daemonDir/dToolsSet/hostslist.py
for myfile in `cd ./hosts;ls ./*.py|grep -v '_init_'|sort -fi`
do
    fileNameRoot=`echo $myfile|sed 's/\.\/\(.*\)\.py/\1/'`
    tytul=`sed -n '/def gettytul..:/ {n;p}' ./hosts/$myfile`
    if `grep -v '[ \t]*#'< ./hosts/$myfile|grep -q 'optionList\.append(getConfigListEntry('`;then
	hasConfig=1
    else
	hasConfig=0
    fi
    if ! `echo $tytul|grep -q 'return'`;then
      tytul=$fileNameRoot
    else
      #tytul=`echo $tytul|cut -d "'" -f2|sed "s;http://;;"|sed "s;/$;;"|sed "s;www\.;;"`
      tytul=`echo $tytul|sed "s/^.*['\"]\(.*\)['\"].*$/\1/"|sed 's/^ *//;s/ *$//;s/http[s]*://;s/\///g;s/www\.//'`
    fi
    #echo "	{id=\"$fileNameRoot\", title=\"$tytul\", fileName=\"hosts/$fileNameRoot.py\", logoName=\"icons/$fileNameRoot.png\", type=\"py\"},">>$pluginDir/luaScripts/hostslist.lua
    echo "      {id=\"$fileNameRoot\", title=\"$tytul\", type=\"py\"},">>$pluginDir/luaScripts/hostslist.lua
    echo "	(\"$fileNameRoot\", \"$tytul\"),">>$daemonDir/dToolsSet/hostslist.py
done
echo "	]">>$daemonDir/dToolsSet/hostslist.py
##################### step 3 the same for lua scripts
cd $pluginDir
for myfile in `cd ./luaHosts;ls ./*.lua|sort -fi`
do
    fileNameRoot=`echo $myfile|sed 's/\.\/\(.*\)\.lua/\1/'`
    tytul=`sed -n '/def gettytul..:/ {n;p}' ./luaHosts/$myfile`
    if ! `echo $tytul|grep -q 'return'`;then
      tytul=$fileNameRoot
    else
      tytul=`echo $tytul|cut -d "'" -f2|sed "s;http://;;"|sed "s;/$;;"|sed "s;www\.;;"`
    fi
    echo "	{id=\"$fileNameRoot\", title=\"$tytul\", fileName=\"luaHosts/$fileNameRoot.lua\", logoName=\"luaHosts/$fileNameRoot.png\", type=\"lua\"},">>$pluginDir/luaScripts/hostslist.lua
done
echo "	}">>$pluginDir/luaScripts/hostslist.lua
