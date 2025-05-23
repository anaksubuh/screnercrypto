@echo off
git config --global --add safe.directory "D:/sinau python/system 23 'streamlite crypto'"
git add .
git commit -m "AUTO UPDATE"
git branch -M main
git remote add origin https://github.com/anaksubuh/screnercrypto.git
git push -u origin main
pause