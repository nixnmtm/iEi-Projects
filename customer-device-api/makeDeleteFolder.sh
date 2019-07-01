#!/bin/bash
mypath=`pwd`
echo $mypath

deletePath="/home/puzzle/deletePuzzleService"
rm -r $deletePath
mkdir $deletePath
chmod 777 -R $deletePath

deleteFile="client_delete.sh"
my=/home/puzzle

pjArray=(customer-device-api)
for pjName in "${pjArray[@]}"
do
    cd $my
    cd $pjName
    echo `pwd`
    cp -i $deleteFile $deletePath/$pjName"_"$deleteFile
done

## for delete part
yes | cp -i $mypath/delete.sh $my/puzzleServiceDelete.sh
