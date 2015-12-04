while true
do
    if test -n "$(find . -maxdepth 1 -name 'devo*' -print -quit)"
    then
        echo found
        experiment=`ls -1 devo* | cut -d '.' -f 2`
        name="runstatus.$experiment.log"
        echo creating $experiment.tar.gz
        cmd="tar czvf results.tar.gz log error.log devo* interm*"
        echo $cmd
        $cmd
        echo Uploading
        #./upload.py $experiment $experiment.tar.gz $name
        #sudo shutdown -h now
        exit
    else
        echo not found
    fi
    sleep 60
done
