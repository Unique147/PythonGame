
<p><strong> Название проекта:</strong> Decisive survival</p>
<p><strong> Автор проекта:</strong> Галынов Кирилл Александрович</p>
<p><strong> Идея проекта:</strong> идея взята с двух игр в жанре roguelike Vampire 
Survivors и Magic survival, где игрок выходит на обширное поле и его цель —
выжить против наступающих волн врагов. У игрока есть оружие, чтобы 
сражаться с врагами. Также были переняты некоторые идеи связанные с 
ядовитыми зонами на карте и с предметами, которые повышают здаровье, 
если оно убвавилось в ходе выживания.</p>
<p><strong> Реализация проекта:</strong> проект включает в себя 15 классов, каждый из 
которых отвечает за определенные аспекты игрового процесса. В проекте 
реализованы механики передвижения персонажа с ограничением выхода за 
границы карты. Особенной чертой является автоматическая атака персонажа, 
которая выполняется без участия игрока. Присутствуют противники, также 
ограниченные границами карты, и происходит нанесение урона при 
коллизии.</p>
<p>Заметной особенностью является непрерывное приближение врагов к 
персонажу и их пополнение после убийства для поддержания постоянного 
числа противников на карте. В игре предусмотрены ядовитые зоны, 
появляющиеся каждые 15 секунд в случайном количестве (до 100), которые 
наносят урон игроку. Также на карте размещаются "Аптечки", 
восстанавливающие здоровье персонажа, и "Порталы", перемещающие 
игрока в случайную точку карты.</p>
<p>Полностью реализовано основное меню с пунктами "Начать игру", 
"Выбор уровня", "Настройки" и "Выход". Добавлено меню паузы, 
позволяющее вернуться в основное меню без завершения игры, а также меню 
смерти с возможностью перезапуска игры или возвращения в основное меню. 
Проект также включает в себя смену уровней и звуковое сопровождение.</p>
<p><strong> Описание технологий:</strong> для запуска игры требуется 3 библиотеки (sys, 
pygame, random), управление в меню происходит с помощью стерелочек 
клавиатуры и кнопки "Enter". Внутри игры управление осуществляется с 
помощью кнопок "W", "A", "S", "D" , а запуск меню паузы с помощью 
кнопки "Esc".</p>
