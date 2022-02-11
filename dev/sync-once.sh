echo 'syncing'
rsync -e ssh --exclude={'.git','**/__pycache__','*.egg-info'} --delete -a ./ $1:~/pi-top-4-Miniscreen
