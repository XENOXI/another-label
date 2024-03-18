$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Start-Process -Wait -FilePath "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"
    # Обновление pip
    python -m pip install --upgrade pip
}

# Проверка доступного пространства на диске (минимум 5 гигабайт)
$freeSpace = (Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Root -eq "C:\"}).Free
if ($freeSpace -lt 5GB) {
    Write-Host "Недостаточно свободного места на диске." -ForegroundColor Red
    exit
}
# Установка необходимых библиотек
python -m pip install requests numpy pandas

python -m pip install torch torchvision
python -m pip install ultralytics