d:
cd python

REM "C:\Program Files\Git\cmd\git.exe" config --global credential.helper store


"C:\Program Files\Git\cmd\git.exe" status
"C:\Program Files\Git\cmd\git.exe" add .
"C:\Program Files\Git\cmd\git.exe" commit -m "Scheduled Commit"
"C:\Program Files\Git\cmd\git.exe" push origin master

exit

REM "C:\Program Files\Git\cmd\git.exe" config --global credential.helper store

REM "C:\Program Files\Git\cmd\git.exe" remote remove origin

REM "C:\Program Files\Git\cmd\git.exe" remote add origin git@github.com:stockpy/stockpy.github.io.git

REM "C:\Program Files\Git\cmd\git.exe" remote add origin stockpy@github.com:stockpy/stockpy.github.io.git

REM "C:\Program Files\Git\cmd\git.exe" remote add origin git@github.com:stockpy/stockpy.github.io.git

REM OpenSSH-Win32 로 한방에 됐음
REM ssh-keygen -t rsa -b 4096 -C "stockpython"

REM "C:\Program Files\Git\cmd\git.exe" pull origin master

git add/rm <file>