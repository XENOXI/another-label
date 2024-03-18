# Системные требования
## Рекомндуемые 
* Процессор: Intel Core i9-14900KS;
* Оперативная память: 8 гигабайт;
* Видеокарта: Nvidia RTX 3090.

# Установка
Скачать репозиторий на свой компьютер и разархивировать его.

#  Запуск приложения
Запускаем файл "labeler.py"

# Использование программы
## Пункты меню 
### File
* "Open video and calculate labels" - После выбора видео оно будет размечено с использованием ресурсов вашего компьютера;
* "Open video and import labels" - Сначала выберите видео, затем файл разметки (.csv);
* "Export labels to csv" - Сохраните файл разметки видео в формате .csv.

## Классы и из обозначения
* Выбранный bounding box (обозначается бирюзовым цветом);

![](https://drive.google.com/uc?id=1qSwyisrEhTmF9S9u16hdy6RmV-6Dveaj)

* Класс normall (обозначается зелёным цветом);

![](https://drive.google.com/uc?id=17Ytgip4Qamx49vSdF9_nSFVkJDkogHQZ)

* Класс unnormal (обозначается синим цветом).

![](https://drive.google.com/uc?id=1UydaRCWEFlg7_mgwOoKrNSwc5vuoWMiQ)

## Управление
### Активные клавиши
* N – Создать новый объект bounding box;
* A - Добавить bounding box для выбранного объекта в кадре;
* Del – Удалить bounding box на кадре;
* Backspace - Удалить timeline bounding box;
* Ctrl + Z - Отменить действие (до 10 действий);
* Ctrl + Y - Вернуть действи.

### Изменение размера видео
Для изменения размера видео нужно потянуть за нижнюю часть видео.

### Перемещение по time line
Перемещение между кадрами осуществляется с помощью ползунка времени и клавишами влево/вправо.

### Выбор bounding box
Выделение нужного Bounding box осуществляется нажатием правой кнопки мыши на видео в нем или нажатием левой кнопки мыши по нужной строке на таймлайне.

Переключение между Bounding boxes осуществляется стрелками вверх/вниз.

![highlighting](https://github.com/XENOXI/another-label/assets/73095626/208c82d0-3843-45be-bf5b-339ba6e518dd)

### Выделение временого отрезка
При зажатии клавиши Shift и нажатии стрелок вправо/влево или при нажатии левой кнопки мыши и перетаскивании курсора в нужную сторону (если вы упёрлись в границу окна, перетаскивайте в нужную сторону для перемотки таймлайна), происходит выделение временного отрезка Bounding box для изменения его класса в выбранном промежутке времени.

### Изменение класса
Изменение класса в выбранной области осуществляется нажатием цифры:
* 1 - normall;
* 2 - unnormal.

 ![разметка1](https://github.com/XENOXI/another-label/assets/73095626/d1a1dd4d-6ea5-49cc-a517-d1b25f8cd300)

 ### Редактирование bounding box

Для того чтобы редактировать рамку bounding box, его нужно выбрать. При зажатии левой кнопки мыши внутри bounding box его можно перемещать, а если потянуть за рамку, то изменятся его размеры.

![редактирование](https://github.com/XENOXI/another-label/assets/73095626/3c9e0e18-0509-45a9-9804-f089bd847676)

# Правила разметки
Наша задача - Детекция силуэта человека с высокой скоростью движения (более 5 км/ч), с характерными для бега движениями силуэта, резкой смены траектории (рыви, прыжки, челночный бег, резкий разворот на 90 градусов).  Под резким ускорением не попадают: падения, приседания, отжимания.Если в кадре показан прыгающий человек, то классом "ненормальные" мы отмечаем сам прыжок (т.е. подготовка к прыжку отмечается классом "нормальные", а сам прыжок - классом "ненормальные"). 

Условия для выделения человека:
* Человек с  с характерными для бега движениями силуэта, резкой смены траектории (рыви, прыжки, челночный бег,  резкий разворот на 90 градусов)
* Возможность четкого детектирования цвета, формы одежды (если мы види человека в отражении, но не может однозначьно сказать какая на нём одежда, то мы его не детектируем).

## Рекомендации
Программа работает на процессоре и не требует оперативной памяти, поэтому может не переключаться между кадрами со скоростью видеовоспроизведения. Если возникают сомнения относительно скорости действий человека, рекомендуется отдельно воспроизвести видео и внимательно изучить нужный момент.
