d:
cd python
"C:\Program Files\Git\cmd\git.exe" config --global credential.helper store

"C:\Program Files\Git\cmd\git.exe" status
"C:\Program Files\Git\cmd\git.exe" add .
"C:\Program Files\Git\cmd\git.exe" commit -m "Scheduled Commit"
"C:\Program Files\Git\cmd\git.exe" push origin master

exit

REM "C:\Program Files\Git\cmd\git.exe" config --global credential.helper store