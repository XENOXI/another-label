# Системные требования
## Рекомндуемые 
Процессор: Intel Core i9-14900KS

Оперативная память: 8 гигабайт

Видеокарта: Nvidia RTX 3090

# Установка
Скачать репрозиторий на свой компьютер

#  Запуск приложения
Запускаем файл "labeler.py"

# Использование программы
## Пункты меню 
### File
* "Open video and calculate labels" - После выбора видео, оно будет размечаться с использованием ресурсов вашего компьютера.
* "Open video and import labels" - Выбераете сначало видео, а потом файл разметки (.csv).
* "Export labels to csv" - Сохраняет файл разметки видео (.csv).

## Классы и из обозначения
Выбранный Bounding box (обозначается бирюзовым цветом) ;
![](https://drive.google.com/uc?id=1wnF_ccs2jYarTd8nWm1SFiIjpszYmUiC)
normall (обозначается зелёным цветом);

unnormal (обозначается синим цветом).

## Управление
### Выбор  Bounding box
Выделение нужного Bounding box осуществляется нажатием правой кнопкой мыши на виде по нему или нажатием левой кнопкой мыши по нужной строке на time line.

Пререключение между Bounding boxes осуществляется стрелками вверх/вниз.

### Перемещение по time line
Перемещение между кадрами осуществляется с помощью ползунка времени и клавишами влево/вправо.

### Выделение обсласти
При зажатии клавиши  Shift и нажатие стрелок в прово/влево, происходит выделение области для раpметки.

### Изменение класса
Изменение класса в выбранной области осуществляетя нажатием цыфры:
* 1 - normall;
* 2 - unnormal.

# Правила разметки


