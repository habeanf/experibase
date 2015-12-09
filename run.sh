gsutil cp gs://yapresearch/yap.tar.gz .
tar xzvf yap.tar.gz
gsutil cp gs://yapresearch/runtasks.py .
chmod u+x runtasks.py
gsutil cp gs://yapresearch/settings.py .
gsutil cp gs://yapresearch/local_settings.py .

sudo pip install redis requests
./runtasks.py $1 > runtasks.log
