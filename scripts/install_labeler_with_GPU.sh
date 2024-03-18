#!/bin/bash

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo "Python не установлен на компьютере. Установите Python и запустите этот скрипт снова." >&2
    exit 1
fi

# Проверка доступного пространства на диске (минимум 5 гигабайт)
freeSpace=$(df -BG / | awk 'NR==2 {print $4}')
if [[ $freeSpace -lt 5 ]]; then
    echo "Недостаточно свободного места на диске." >&2
    exit 1
fi

pip install torch torchvision torchaudio

# Установка необходимых библиотек
pip install ultralytics