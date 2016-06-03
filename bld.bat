set MENU_DIR=%PREFIX%\Menu
mkdir %MENU_DIR%

set SCRIPT_DIR=%PREFIX%\Scripts
mkdir %SCRIPT_DIR%

copy %RECIPE_DIR%\menu-windows.json %MENU_DIR%\stocks.json
if errorlevel 1 exit 1

copy %RECIPE_DIR%\stocks-dashboard.py %SCRIPT_DIR%\stocks-dashboard.py
if errorlevel 1 exit 1

copy %RECIPE_DIR%\stocks_dashboard.bat %SCRIPT_DIR%
if errorlevel 1 exit 1
