#!/bin/bash
cd $(dirname "$0")
mypath=`pwd`
#echoerr()

# echo "currentpath: "$mypath >&2
echo "currentpath: "$mypath
myupdateFolder=myupdate
myupdatepath=$mypath/$myupdateFolder
errorstage=0
mkdir -p $myupdatepath
if [ $? -eq 0 ]; then
    echo OK
else
    echo FAIL
    errorstage=1
fi

if [ $errorstage -eq 0 ]; then
  tar Jxf $mypath/update.tar.xz -C $myupdatepath
  if [ $? -eq 0 ]; then
      echo OK
  else
      echo FAIL
      errorstage=2
  fi
fi

if [ $errorstage -eq 0 ]; then
  sudo bash $myupdatepath/update/config/setup.sh
  if [ $? -eq 0 ]; then
      echo OK
  else
      echo FAIL
      errorstage=3
  fi
fi

rm $mypath/update.tar.xz
if [ $? -eq 0 ]; then
    echo OK
else
    echo FAIL
fi

rm -r $myupdatepath
if [ $? -eq 0 ]; then
    echo OK
else
    echo FAIL
fi

exit 0
