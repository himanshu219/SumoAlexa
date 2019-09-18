git stash
git pull origin dev
git stash apply
if [ $? -eq 0 ]; then
    echo "OK"
    git commit -a -m "updated"
    ask lambda upload -f arn:aws:lambda:us-east-1:456227676011:function:SumoLogic-12ece74fd46e -s lambda/
else
    echo "FAIL while stashing"
fi
