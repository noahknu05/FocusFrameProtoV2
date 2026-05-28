& c:\Users\noahp\OneDrive\Skrivebord\KiStudie\ProtoypeV1\venv\Scripts\Activate.ps1
Set-Location -Path "c:\Users\noahp\OneDrive\Skrivebord\KiStudie\ProtoypeV1\Final_Proto"
pyinstaller --onefile --windowed --uac-admin --icon "logo.ico" --add-data "logo.png;." "FocusFrame.py"
