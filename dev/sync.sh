# copy folder over when first running script
./dev/sync-once.sh $1

# sync folder whenever a file changes in the repo.
fswatch --recursive -o ./ | xargs -n1 -I{} ./dev/sync-once.sh $1
