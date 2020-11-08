@echo off
rem FOR %%variable IN (set) DO command [command-parameters]
for /r %%i in (data\3dstl\*.obj) do (
    FOR /L %%v IN (2,1,20) do (
        python main.py --line_data %%i --volume %%v
    )
)
pause