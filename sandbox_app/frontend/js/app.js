import { api } from "./api.js";

const APP_BUILD_ID = "20260711_kanban_lab_style_polish";
const browserWindow = typeof window !== "undefined" ? window : null;
const browserDocument = typeof document !== "undefined" ? document : null;
const localStorageRef = browserWindow?.localStorage || null;
const textNodeOriginals = new WeakMap();
const attributeOriginals = new WeakMap();
const THEME_MODES = ["auto", "light", "dark"];
const runtimeState = browserWindow
  ? (browserWindow.__compassAiSandboxRuntime ||= {})
  : {};
runtimeState.longTasks ||= new Map();
runtimeState.longTaskCounter ||= 0;
const longTasks = runtimeState.longTasks;

const RU_TO_EN = {
  "COMPASS AI Sandbox — локальная автономная песочница для генерации данных, просмотра datasets и экспериментов с моделями.": "COMPASS AI Sandbox: a local autonomous workspace for data generation, dataset review, and model experiments.",
  "Песочница": "Sandbox",
  "Главная": "Home",
  "Генерация данных": "Data Generation",
  "Просмотр данных": "Data Viewer",
  "Импорт данных": "Data Import",
  "Обучение": "Training",
  "Модели": "Models",
  "Назначение задач": "Task Assignment",
  "Канбан-лаборатория": "Kanban Lab",
  "Ошибка канбан-лаборатории": "Kanban Lab Error",
  "Отчеты": "Reports",
  "Настройки": "Settings",
  "Путь работы": "Workflow",
  "Датасеты": "Datasets",
  "Таблицы и фильтры": "Tables and Filters",
  "Сравнение": "Comparison",
  "Рекомендации": "Recommendations",
  "Экспорт": "Export",
  "Профили и лимиты": "Profiles and Limits",
  "Свои файлы": "Your Files",
  "Сервер": "Server",
  "Проверка...": "Checking...",
  "Локальное приложение": "Local App",
  "Обновить": "Refresh",
  "Справка": "Help",
  "Закрыть справку": "Close help",
  "Справка по текущей вкладке": "Help for current tab",
  "Переключить язык": "Switch language",
  "Переключить тему": "Switch theme",
  "Работает": "Online",
  "Проверить": "Check",
  "локальный сервер": "local server",
  "Недоступен": "Unavailable",
  "Загрузка...": "Loading...",
  "Готов": "Ready",
  "Готов к запуску": "Ready to run",
  "Ошибка": "Error",
  "Выполняется": "Running",
  "Завершено": "Completed",
  "Обновлено": "Refreshed",
  "Данные страницы запрошены заново.": "Page data was requested again.",
  "Генерация уже выполняется.": "Generation is already running.",
  "Подготовка...": "Preparing...",
  "Сохранение схемы...": "Saving schema...",
  "Генерация сотрудников...": "Generating employees...",
  "Генерация задач...": "Generating tasks...",
  "Генерация истории...": "Generating history...",
  "Создание пар для обучения...": "Creating training pairs...",
  "Сохранение файлов...": "Saving files...",
  "Генерация данных...": "Generating data...",
  "Строим признаки...": "Building features...",
  "Проверяем данные...": "Validating data...",
  "Делим данные...": "Splitting data...",
  "Обучаем модели...": "Training models...",
  "Считаем метрики...": "Calculating metrics...",
  "Сохраняем артефакты...": "Saving artifacts...",
  "Сохраняем файлы...": "Saving files...",
  "Импортируем файлы...": "Importing files...",
  "Проверяем таблицы...": "Validating tables...",
  "Сохраняем датасет...": "Saving dataset...",
  "Формируем отчет...": "Generating report...",
  "Собираем результаты...": "Collecting results...",
  "Распределяем задачи...": "Assigning tasks...",
  "Готовим объяснения...": "Preparing explanations...",
  "Готово": "Done",
  "Нет данных для отображения.": "No data to display.",
  "Начните здесь: создайте датасет, обучите модели, затем проверьте назначения задач.": "Start here: create a dataset, train models, then check task assignments.",
  "Карточки показывают, есть ли уже данные, модели и сохраненные результаты.": "Cards show whether data, models, and saved results already exist.",
  "Если чего-то нет, используйте кнопки перехода в нужную вкладку.": "If something is missing, use the buttons to jump to the right tab.",
  "Здесь создается полный учебный датасет: сотрудники, задачи, история выполнений и пары для обучения.": "Create a full training dataset here: employees, tasks, assignment history, and training pairs.",
  "Для своего домена выберите custom и задайте роли, уровни, навыки и собственные поля.": "For your own domain, choose custom and define roles, levels, skills, and custom fields.",
  "После генерации переходите в Просмотр данных или сразу в Обучение.": "After generation, go to Data Viewer or straight to Training.",
  "Выберите датасет и таблицу, затем переключайтесь между списком, сводкой, таблицей, графиками и канбаном.": "Choose a dataset and table, then switch between list, summary, table, charts, and kanban.",
  "Фильтры помогают быстро проверить статусы задач, роли, уровни и приоритеты.": "Filters help quickly inspect task statuses, roles, levels, and priorities.",
  "Удаление датасета стирает только выбранный пользовательский датасет.": "Deleting a dataset removes only the selected user-created dataset.",
  "Выберите датасет, целевой режим и модели. По умолчанию выбраны все доступные алгоритмы.": "Choose a dataset, target mode, and models. All available algorithms are selected by default.",
  "Сначала можно построить признаки отдельно, но обычный сценарий — нажать Запустить обучение.": "You can build features separately, but the normal path is to click Run Training.",
  "После обучения сравните метрики здесь или откройте вкладку Модели.": "After training, compare metrics here or open the Models tab.",
  "Здесь видны обученные модели, их метрики, формат артефактов и статус проверки.": "This tab shows trained models, metrics, artifact formats, and validation status.",
  "Выберите сессию обучения и модель, чтобы посмотреть детали или проверить экспорт.": "Choose a training session and model to view details or validate export.",
  "Если моделей нет, сначала перейдите в Обучение.": "If there are no models, go to Training first.",
  "Здесь проверяется, кому модель рекомендует назначить одну задачу или весь список задач.": "Check who the model recommends for one task or the full task list.",
  "Для основного сценария создайте проверочный набор из датасета, выберите обученную модель и запустите рекомендацию по одной задаче или распределение всех задач.": "For the main workflow, create a test set from a dataset, choose a trained model, then run a single-task recommendation or full assignment.",
  "LLM-пояснения включаются галочкой и зависят от доступности Ollama/Qwen.": "LLM explanations are enabled by checkbox and depend on Ollama/Qwen availability.",
  "Здесь можно загрузить копию проверочного набора или создать лабораторную копию из датасета.": "Load a copy of a test set here or create a lab copy from a dataset.",
  "Перемещайте задачи между столбцами, переносите или очищайте целые столбцы, добавляйте ручные задачи в To Do.": "Move tasks between columns, move or clear whole columns, and add manual tasks to To Do.",
  "После правок нажмите Принять канбан и рассчитать рекомендации: модель увидит текущее состояние копии, а исходный датасет не изменится.": "After editing, click Accept Kanban and calculate recommendations: the model will see the current copy state, while the source dataset stays unchanged.",
  "Эксперименты": "Experiments",
  "Источник лаборатории": "Lab Source",
  "Загружается копия задач и команды. Все перемещения и ручные задачи живут только в этой вкладке.": "A copy of tasks and team is loaded. All moves and manual tasks live only in this tab.",
  "оригинал не меняется": "source is unchanged",
  "Нет проверочных наборов": "No test sets",
  "Нет сохраненных досок": "No saved boards",
  "Нет обученных сессий": "No training sessions",
  "статус неизвестен": "status unknown",
  "Сбалансированно": "Balanced",
  "Лучшее качество": "Best Quality",
  "Быстрее доставка": "Fastest Delivery",
  "Развитие сотрудника": "Employee Growth",
  "Осторожнее к рискам": "Risk Aware",
  "Проверочный набор": "Test Set",
  "Название лабораторной доски": "Lab Board Name",
  "Сохраненная доска": "Saved Board",
  "Датасет для новой копии": "Dataset for New Copy",
  "Сессия обучения": "Training Session",
  "Модель": "Model",
  "Режим рекомендации": "Recommendation Mode",
  "Кандидатов на задачу": "Candidates per Task",
  "Добавлять LLM-объяснение при раскрытии задачи": "Add LLM explanation when opening a task",
  "Загрузить копию набора": "Load Set Copy",
  "Загрузить сохраненную доску": "Load Saved Board",
  "Сохранить текущую доску": "Save Current Board",
  "Удалить сохраненную": "Delete Saved",
  "Создать лабораторную копию из датасета": "Create Lab Copy from Dataset",
  "Сбросить изменения": "Reset Changes",
  "Принять канбан и рассчитать рекомендации": "Accept Kanban and Calculate Recommendations",
  "Задачи на доске": "Tasks on Board",
  "К рекомендации": "To Recommend",
  "Рекомендации": "Recommendations",
  "кандидаты не рассчитаны": "candidates not calculated",
  "теги не указаны": "tags not specified",
  "нет": "none",
  "задач": "tasks",
  "ч": "h",
  "навыки": "skills",
  "Столбец перенесен": "Column moved",
  "Канбан-доска": "Kanban Board",
  "Загрузите проверочный набор или создайте лабораторную копию из датасета.": "Load a test set or create a lab copy from a dataset.",
  "Добавить ручную задачу": "Add Manual Task",
  "Заполните поля так, чтобы модель понимала задачу: тип, сложность, часы и требуемые навыки.": "Fill fields so the model understands the task: type, complexity, hours, and required skills.",
  "Заполните поля из словаря текущего набора, чтобы модель видела знакомые проекты, типы и навыки.": "Fill fields from the current set dictionary so the model sees known projects, types, and skills.",
  "например: Срочный security review": "for example: Urgent security review",
  "Название": "Title",
  "Тип задачи": "Task Type",
  "Приоритет": "Priority",
  "Сложность 0..1": "Complexity 0..1",
  "Оценка часов": "Estimated Hours",
  "Проект": "Project",
  "Теги / навыки через запятую": "Tags / Skills comma-separated",
  "Теги / навыки": "Tags / Skills",
  "Выберите один или несколько пунктов из словаря текущего набора.": "Choose one or more items from the current set dictionary.",
  "Сначала загрузите набор": "Load a set first",
  "Добавить в To Do": "Add to To Do",
  "Персонал лаборатории": "Lab Team",
  "Меняйте сотрудников только в копии: удаляйте лишних и добавляйте новых с навыками из текущего набора.": "Edit employees only in the copy: remove extra people and add new ones with skills from the current set.",
  "сотрудников": "employees",
  "Нет сотрудников": "No employees",
  "В лабораторной копии пока нет сотрудников.": "There are no employees in the lab copy yet.",
  "ID / название нового сотрудника": "New Employee ID / Name",
  "например: emp_lab_security_001": "for example: emp_lab_security_001",
  "Роль": "Role",
  "Грейд": "Grade",
  "Доступность 0..1": "Availability 0..1",
  "Текущая нагрузка 0..1": "Current Workload 0..1",
  "Усталость 0..1": "Fatigue 0..1",
  "Качество 0..1": "Quality 0..1",
  "Скорость 0..1": "Speed 0..1",
  "Надежность дедлайнов 0..1": "Deadline Reliability 0..1",
  "Навыки сотрудника": "Employee Skills",
  "Добавить сотрудника": "Add Employee",
  "Удалить": "Delete",
  "Удалить всех сотрудников": "Delete All Employees",
  "навыки не указаны": "skills not specified",
  "Что требуется в задаче": "Task Requirements",
  "задача": "task",
  "тип не указан": "type not specified",
  "приоритет не указан": "priority not specified",
  "Дедлайн": "Deadline",
  "Требуемые навыки / теги": "Required Skills / Tags",
  "Низкий риск": "Low Risk",
  "Доступность": "Availability",
  "График соответствия задаче": "Task Fit Chart",
  "Пунктир — требования задачи, цветные линии — кандидаты.": "Dashed line is task requirements, colored lines are candidates.",
  "Сравнение задачи и кандидатов": "Task and Candidate Comparison",
  "Требования задачи": "Task Requirements",
  "Кандидаты": "Candidates",
  "Для этой задачи рекомендации еще не рассчитаны.": "Recommendations have not been calculated for this task yet.",
  "Канбан-доска эксперимента": "Experiment Kanban Board",
  "Перетаскивайте карточки между столбцами или переносите/очищайте столбец целиком.": "Drag cards between columns or move/clear a whole column.",
  "Перенести столбец": "Move Column",
  "Очистить": "Clear",
  "Детали задачи": "Task Details",
  "Выберите карточку на канбан-доске, чтобы увидеть требования, кандидатов, график и объяснение.": "Select a card on the kanban board to see requirements, candidates, chart, and explanation.",
  "Следующий статус": "Next Status",
  "Удалить задачу": "Delete Task",
  "Кандидаты модели": "Model Candidates",
  "Мини-рейтинг по текущему состоянию канбан-доски.": "Mini ranking for the current kanban board state.",
  "роль не указана": "role not specified",
  "Риск-fit": "Risk Fit",
  "Совпало": "Matched",
  "Не хватает": "Missing",
  "нет совпадений": "no matches",
  "нет пробелов": "no gaps",
  "LLM-объяснение": "LLM Explanation",
  "Локальное объяснение": "Local Explanation",
  "Сильные стороны": "Strengths",
  "Риски": "Risks",
  "Выберите проверочный набор": "Select a test set",
  "Выберите сохраненную доску": "Select a saved board",
  "Копия набора загружена": "Set copy loaded",
  "Сохраненная доска загружена": "Saved board loaded",
  "Выберите датасет": "Select a dataset",
  "Доска возвращена к исходной копии": "Board reset to original copy",
  "Доска и персонал возвращены к исходной копии": "Board and team reset to original copy",
  "Столбец очищен в лабораторной копии": "Column cleared in lab copy",
  "Лабораторная задача": "Lab Task",
  "Лабораторная доска сохранена": "Lab board saved",
  "Сохраненная доска удалена": "Saved board deleted",
  "Укажите хотя бы один тег или навык для ручной задачи": "Enter at least one tag or skill for a manual task",
  "Сначала загрузите набор, чтобы появились существующие проекты, типы и навыки": "Load a set first so existing projects, types, and skills are available",
  "Выберите тип задачи и проект из текущего набора": "Choose a task type and project from the current set",
  "Выберите хотя бы один существующий тег или навык для ручной задачи": "Choose at least one existing tag or skill for a manual task",
  "В ручной задаче можно использовать только существующие теги и навыки": "Manual tasks can use only existing tags and skills",
  "Ручная задача добавлена в To Do": "Manual task added to To Do",
  "Задача удалена из копии": "Task removed from copy",
  "Сначала загрузите набор, чтобы появились роли, грейды и навыки": "Load a set first so roles, grades, and skills are available",
  "Выберите роль и грейд из текущего набора": "Choose a role and grade from the current set",
  "Выберите хотя бы один навык для нового сотрудника": "Choose at least one skill for the new employee",
  "Новому сотруднику можно назначать только существующие навыки": "A new employee can use only existing skills",
  "Сотрудник с таким ID уже есть в лабораторной копии": "An employee with this ID already exists in the lab copy",
  "Сотрудник добавлен в лабораторную копию": "Employee added to the lab copy",
  "Выберите сотрудника для удаления": "Choose an employee to delete",
  "Сотрудник удален из лабораторной копии": "Employee removed from the lab copy",
  "Удалить из лабораторной копии всех сотрудников?": "Delete all employees from the lab copy?",
  "Все сотрудники удалены из лабораторной копии": "All employees removed from the lab copy",
  "Сначала загрузите копию набора": "Load a set copy first",
  "Канбан-рекомендации": "Kanban Recommendations",
  "Передаем текущую копию доски модели...": "Sending the current board copy to the model...",
  "Проверяем доску...": "Checking board...",
  "Считаем рекомендации...": "Calculating recommendations...",
  "Обновляем карточки...": "Updating cards...",
  "Рекомендации готовы": "Recommendations ready",
  "Рассчитано задач": "Tasks calculated",
  "Загружаем датасеты, наборы и модели...": "Loading datasets, sets, and models...",
  "Создавайте понятные отчеты по датасетам, моделям и результатам назначения.": "Create clear reports for datasets, models, and assignment results.",
  "Готовые отчеты можно открыть ссылками или удалить из списка.": "Finished reports can be opened from links or deleted from the list.",
  "Настройки задают значения по умолчанию, лимиты генерации и параметры LLM.": "Settings define defaults, generation limits, and LLM parameters.",
  "Редактор профилей нужен для своих предметных областей: медицина, продажи, поддержка, разработка и другие.": "Use the profile editor for custom domains: healthcare, sales, support, development, and others.",
  "Загрузите свои CSV, JSON или Parquet-файлы вместо генерации синтетических данных.": "Upload your own CSV, JSON, or Parquet files instead of generating synthetic data.",
  "Предпросмотр проверяет структуру файла до сохранения.": "Preview checks file structure before saving.",
  "После успешного импорта датасет появится в Просмотре данных и Обучении.": "After import, the dataset appears in Data Viewer and Training.",
  "Датасет": "Dataset",
  "Датасеты": "Datasets",
  "Данные": "Data",
  "Сотрудники": "Employees",
  "Сотрудник": "Employee",
  "Задачи": "Tasks",
  "Задача": "Task",
  "История выполнений": "Assignment History",
  "Пары для обучения": "Training Pairs",
  "Профиль": "Profile",
  "Тип": "Type",
  "Размер": "Size",
  "Создан": "Created",
  "Сводка": "Summary",
  "Таблица": "Table",
  "Графики": "Charts",
  "Канбан": "Kanban",
  "Поиск": "Search",
  "Поиск...": "Search...",
  "Строк на странице": "Rows per page",
  "Очистить фильтры": "Clear filters",
  "Обновить список": "Refresh list",
  "Удалить датасет": "Delete dataset",
  "Создать данные": "Create Data",
  "Импортировать файлы": "Import Files",
  "Нет датасетов": "No datasets",
  "Датасетов пока нет. Создайте данные или импортируйте свои файлы.": "No datasets yet. Create data or import your files.",
  "Просмотр данных": "Data Viewer",
  "Выберите датасет, таблицу и режим просмотра. Данные можно искать, фильтровать и проверять без открытия файлов.": "Choose a dataset, table, and view mode. You can search, filter, and inspect data without opening files.",
  "Профиль датасета": "Dataset Profile",
  "Размер таблиц": "Table Sizes",
  "Статусы задач": "Task Statuses",
  "Сводка по задачам": "Task Summary",
  "Канбан задач": "Task Kanban",
  "Задачи по статусам": "Tasks by Status",
  "Задачи по приоритетам": "Tasks by Priority",
  "Сотрудники по ролям": "Employees by Role",
  "Сотрудники по уровням": "Employees by Level",
  "Домен": "Domain",
  "Режим": "Mode",
  "не указан": "not specified",
  "не выбран": "not selected",
  "созданный": "generated",
  "импортированный": "imported",
  "Создание данных": "Data Creation",
  "Генерация данных": "Data Generation",
  "Создайте датасет под свой домен: людей, задачи, историю выполнений и пары для обучения моделей.": "Create a dataset for your domain: people, tasks, assignment history, and model training pairs.",
  "ID датасета": "Dataset ID",
  "Профиль предметной области": "Domain Profile",
  "Seed для повторяемости": "Seed for Reproducibility",
  "Размер датасета": "Dataset Size",
  "Маленький предпросмотр": "Small Preview",
  "Средний для проверки": "Medium Validation",
  "Большой для обучения": "Large Training",
  "Очень большой": "Huge Training",
  "Количество сотрудников": "Employee Count",
  "Количество задач": "Task Count",
  "Количество проектов": "Project Count",
  "История на сотрудника": "History per Employee",
  "Пар для обучения": "Training Pairs",
  "Кандидатов на задачу": "Candidates per Task",
  "Цель оптимизации": "Optimization Target",
  "заменить существующий датасет": "replace existing dataset",
  "Подтверждение большого запуска": "Large Run Confirmation",
  "Очень большой датасет может занять заметное время и место на диске.": "A huge dataset can take noticeable time and disk space.",
  "я понимаю размер запуска": "I understand the run size",
  "Создать полный датасет": "Create Full Dataset",
  "Только сотрудники": "Employees Only",
  "Только задачи": "Tasks Only",
  "Только история": "History Only",
  "Проверить настройки": "Check Settings",
  "Последний датасет": "Last Dataset",
  "Результат": "Result",
  "После генерации здесь появятся счетчики и быстрые кнопки следующих шагов.": "After generation, counters and quick next-step buttons will appear here.",
  "Датасет": "Dataset",
  "Генератор": "Generator",
  "Следующий шаг": "Next Step",
  "Что дальше": "Next",
  "Готово, данные сохранены.": "Done, data saved.",
  "Проверьте данные в просмотре, затем перейдите в обучение и запустите модели на этом датасете.": "Review the data, then go to Training and train models on this dataset.",
  "Открыть в просмотре данных": "Open in Data Viewer",
  "Перейти к обучению": "Go to Training",
  "Перейти к назначению задач": "Go to Task Assignment",
  "Генерация не выполнена": "Generation Failed",
  "Проверка настроек": "Settings Check",
  "Поля своей предметной области": "Custom Domain Fields",
  "Роли, уровни, теги, поля задач и поля результата": "Roles, levels, tags, task fields, and outcome fields",
  "можно менять": "editable",
  "системный профиль": "system profile",
  "Роли": "Roles",
  "Уровни / грейды": "Levels / Grades",
  "Навыки / теги": "Skills / Tags",
  "Типы задач": "Task Types",
  "Поля сотрудников": "Employee Fields",
  "Поля задач": "Task Fields",
  "Поля результата": "Outcome Fields",
  "Добавить поле": "Add Field",
  "Сохранить поля": "Save Fields",
  "Сбросить к общим полям": "Reset Generic Fields",
  "обязательно": "required",
  "Удалить поле": "Delete field",
  "Обучение моделей": "Model Training",
  "Выберите датасет и запустите обучение. По умолчанию включены все доступные методы, чтобы их можно было сравнить между собой.": "Choose a dataset and start training. All available methods are enabled by default so they can be compared.",
  "Цель модели": "Model Target",
  "Максимум пар": "Max Pairs",
  "Доля обучения": "Train Share",
  "Доля проверки": "Validation Share",
  "Доля теста": "Test Share",
  "перестроить признаки": "rebuild features",
  "автоматически построить признаки перед обучением": "build features automatically before training",
  "Модели для обучения": "Models to Train",
  "Выбрать базовые": "Select Core",
  "Выбрать все": "Select All",
  "Построить признаки": "Build Features",
  "Проверить признаки": "Check Features",
  "Запустить обучение": "Run Training",
  "Параметры моделей": "Model Parameters",
  "Оставьте значения по умолчанию, если не хотите тонко настраивать обучение.": "Keep defaults unless you want to fine-tune training.",
  "Сессии обучения": "Training Sessions",
  "Детали сессии": "Session Details",
  "Создать графики": "Create Charts",
  "Открыть графики": "Open Charts",
  "Удалить сессию": "Delete Session",
  "Выбранный датасет": "Selected Dataset",
  "Готово к запуску": "Ready to Run",
  "Выберите датасет, цель и модели. Затем нажмите «Запустить обучение».": "Choose a dataset, target, and models. Then click Run Training.",
  "Сравнение метрик": "Metric Comparison",
  "Метрики": "Metrics",
  "Метрики пока не рассчитаны.": "Metrics have not been calculated yet.",
  "лучшая модель пока не определена": "best model unknown",
  "Сессия обучения": "Training Session",
  "Модель": "Model",
  "Модели": "Models",
  "Размер проверки": "Validation Size",
  "попробовать экспорт в ONNX": "try ONNX export",
  "Детали модели": "Model Details",
  "Проверить": "Validate",
  "Экспорт / проверка": "Export / Validate",
  "Удалить модель": "Delete Model",
  "Что выбрано": "Current Selection",
  "Модели пока не обучены. Сначала перейдите во вкладку «Обучение».": "No models trained yet. Go to Training first.",
  "Проверочный набор": "Test Set",
  "Проверочные наборы": "Test Sets",
  "Проверка моделей на задачах": "Test Models on Tasks",
  "Выберите обученную модель, проверьте рекомендацию по одной задаче или распределите сразу весь набор с учетом нагрузки и рисков.": "Choose a trained model, test a recommendation for one task, or assign the full set with workload and risks considered.",
  "Проверка на вашем датасете": "Test on Your Dataset",
  "Превратите созданный или импортированный датасет в набор задач для рекомендаций.": "Turn a generated or imported dataset into a task set for recommendations.",
  "датасет -> набор -> модель -> назначение": "dataset -> set -> model -> assignment",
  "ID проверочного набора": "Test Set ID",
  "Статусы задач": "Task Statuses",
  "Готовые к работе: todo/in_progress/review/blocked": "Ready work: todo/in_progress/review/blocked",
  "Только todo": "Todo only",
  "Все, кроме done/failed": "All except done/failed",
  "Создать набор из датасета": "Create Set from Dataset",
  "Проверочный набор вручную": "Manual Test Set",
  "Создайте небольшую команду и задачи для быстрой проверки моделей.": "Create a small team and tasks for quick model checks.",
  "Сотрудников": "Employees",
  "Активных задач": "Active Tasks",
  "Глубина истории": "History Depth",
  "Уровни": "Levels",
  "Создать проверочный набор": "Create Test Set",
  "Рекомендации и распределение": "Recommendations and Assignment",
  "Выберите обученную модель, набор задач и режим расчета.": "Choose a trained model, task set, and scoring mode.",
  "Задача": "Task",
  "Режим рекомендации": "Recommendation Mode",
  "Режим распределения": "Assignment Mode",
  "Баланс качества и нагрузки": "Balance Quality and Workload",
  "Лучшее качество": "Best Quality",
  "Быстрее всего": "Fastest Delivery",
  "Лучшее обучение сотрудника": "Best Learning",
  "Осторожнее к рискам": "Risk Aware",
  "Сколько кандидатов показать": "Candidates to Show",
  "Максимальная нагрузка на сотрудника": "Max Workload per Employee",
  "Штраф за дисбаланс": "Fairness Penalty",
  "Штраф за усталость": "Fatigue Penalty",
  "Бонус за развитие": "Learning Bonus",
  "Штраф за нагрузку": "Workload Penalty",
  "Добавить объяснения через Qwen/Ollama": "Add explanations via Qwen/Ollama",
  "Загрузить задачи": "Load Tasks",
  "Рекомендовать по одной задаче": "Recommend One Task",
  "Распределить все задачи": "Assign All Tasks",
  "Удалить набор": "Delete Set",
  "Фильтры результатов": "Result Filters",
  "Найдите нужного сотрудника, статус, проект или риск в результатах.": "Find an employee, status, project, or risk in results.",
  "Очистить": "Clear",
  "Статус задачи": "Task Status",
  "Проект": "Project",
  "Риск": "Risk",
  "Рекомендация по одной задаче": "Single-Task Recommendation",
  "Выберите задачу и запустите рекомендацию, чтобы увидеть лучших кандидатов.": "Choose a task and run recommendation to see top candidates.",
  "Лучшие кандидаты": "Top Candidates",
  "Сравнение кандидатов": "Candidate Comparison",
  "Объяснение рекомендации": "Recommendation Explanation",
  "Доска после распределения": "Board after Assignment",
  "Назначено": "Assigned",
  "Без назначения": "Unassigned",
  "Распределение всех задач": "Full Task Assignment",
  "Запустите распределение, чтобы модель подобрала исполнителей для доступных задач.": "Run assignment so the model can pick assignees for available tasks.",
  "Объяснение распределения": "Assignment Explanation",
  "Файлы результата": "Result Files",
  "Сессии назначения": "Assignment Sessions",
  "Сохраненных сессий назначения пока нет.": "No saved assignment sessions yet.",
  "Сохраненные результаты распределения задач.": "Saved task assignment results.",
  "Удалить выбранную": "Delete Selected",
  "Назначение задач": "Task Assignment",
  "Сильные стороны": "Strengths",
  "Риски": "Risks",
  "Справедливость": "Fairness",
  "Нагрузка": "Workload",
  "Локальное объяснение": "Local explanation",
  "источник ранжирования": "ranking source",
  "Отчеты и выгрузки": "Reports and Exports",
  "Сформируйте понятные отчеты по данным, моделям и назначениям, а затем откройте готовые файлы для анализа.": "Create clear reports for data, models, and assignments, then open finished files for analysis.",
  "Отчеты по датасету": "Dataset Reports",
  "Сводка по составу данных, качеству и базовым распределениям.": "Summary of data composition, quality, and base distributions.",
  "Удалить отчет": "Delete Report",
  "Тип датасета": "Dataset Type",
  "Сгенерированный": "Generated",
  "Импортированный": "Imported",
  "Сформировать отчет": "Create Report",
  "Отчеты по моделям": "Model Reports",
  "Сравнение метрик, артефактов моделей и статусов проверки.": "Comparison of metrics, model artifacts, and validation statuses.",
  "Отчеты по назначениям": "Assignment Reports",
  "Рекомендации, распределение задач, справедливость и нагрузка.": "Recommendations, task assignment, fairness, and workload.",
  "Сессия назначения": "Assignment Session",
  "Старые отчеты обучения": "Legacy Training Reports",
  "Графики и HTML-отчеты обучения остаются доступны в разделе обучения. Здесь собраны новые пользовательские экспорты для датасетов, моделей и назначений.": "Training charts and HTML reports remain available in Training. New user exports for datasets, models, and assignments are collected here.",
  "Сохраненные отчеты": "Saved Reports",
  "Экспортированные отчеты пока не созданы.": "No exported reports yet.",
  "Готовые файлы HTML и CSV для просмотра и выгрузки.": "Finished HTML and CSV files for viewing and export.",
  "Детали отчета": "Report Details",
  "Выберите отчет из списка, чтобы открыть сводку и ссылки на файлы.": "Choose a report from the list to open its summary and file links.",
  "Краткая сводка": "Brief Summary",
  "В этом отчете нет отдельной сводки.": "This report has no separate summary.",
  "Настройки и схемы данных": "Settings and Data Schemas",
  "Управляйте профилями предметной области, лимитами генерации, моделями по умолчанию и подключением LLM в одном месте.": "Manage domain profiles, generation limits, default models, and LLM connection in one place.",
  "Основные настройки": "Main Settings",
  "Значения по умолчанию, лимиты генерации и параметры Qwen/Ollama.": "Defaults, generation limits, and Qwen/Ollama parameters.",
  "Сбросить": "Reset",
  "Seed по умолчанию": "Default Seed",
  "Профиль по умолчанию": "Default Profile",
  "Размер датасета по умолчанию": "Default Dataset Size",
  "Цель модели по умолчанию": "Default Model Target",
  "Режим рекомендации по умолчанию": "Default Recommendation Mode",
  "Режим распределения по умолчанию": "Default Assignment Mode",
  "Модели для обучения": "Training Models",
  "Лимит сотрудников для huge": "Huge Employee Limit",
  "Лимит задач для huge": "Huge Task Limit",
  "Лимит обучающих пар для huge": "Huge Training Pair Limit",
  "Адрес Ollama": "Ollama URL",
  "Модель Qwen/Ollama": "Qwen/Ollama Model",
  "Таймаут LLM, секунды": "LLM Timeout, seconds",
  "Автоматически скачивать модель Ollama": "Automatically pull Ollama model",
  "Сохранить настройки": "Save Settings",
  "Пути хранения": "Storage Paths",
  "Папки внутри sandbox_app для данных, моделей и отчетов": "Folders inside sandbox_app for data, models, and reports",
  "дополнительно": "advanced",
  "Сохранить пути": "Save Paths",
  "Схемы данных": "Data Schemas",
  "Настройте роли, уровни, теги и собственные поля без ручного редактирования файлов.": "Configure roles, levels, tags, and custom fields without editing files manually.",
  "Обновить схемы": "Refresh Schemas",
  "Группа полей": "Field Group",
  "Показать сводку": "Show Summary",
  "Создать профиль предметной области": "Create Domain Profile",
  "ID профиля": "Profile ID",
  "Название": "Name",
  "Описание": "Description",
  "Своя область": "Custom Domain",
  "Редактируемый профиль для своей предметной области": "Editable profile for your domain",
  "Создать схему": "Create Schema",
  "Параметры схемы": "Schema Settings",
  "Схема не выбрана.": "No schema selected.",
  "Сохранить схему": "Save Schema",
  "Удалить схему": "Delete Schema",
  "Поля пока не добавлены.": "No fields added yet.",
  "Название поля": "Field Name",
  "Тип поля": "Field Type",
  "Пользовательское поле": "Custom Field",
  "Обязательное поле": "Required Field",
  "Сводка схемы": "Schema Summary",
  "Количество словарей и пользовательских полей": "Dictionary and custom field counts",
  "Поля сотрудников": "Employee Fields",
  "Поля задач": "Task Fields",
  "Поля результата": "Outcome Fields",
  "Число": "Number",
  "Категория": "Category",
  "Да / нет": "Yes / No",
  "Текст": "Text",
  "Список тегов": "Tag List",
  "Результат": "Outcome",
  "Импорт своих данных": "Import Your Data",
  "Загрузите CSV, JSON или Parquet-файлы. Минимально нужны employees, tasks, assignment_history и training_pairs.": "Upload CSV, JSON, or Parquet files. At minimum, employees, tasks, assignment_history, and training_pairs are needed.",
  "заменить существующий импорт": "replace existing import",
  "Файлы таблиц": "Table Files",
  "Предпросмотр": "Preview",
  "Импортировать датасет": "Import Dataset",
  "Предпросмотр:": "Preview:",
  "Ошибок": "Errors",
  "Предупреждений": "Warnings",
  "Таблиц": "Tables",
  "Исправьте ошибки проверки и повторите импорт.": "Fix validation errors and retry import.",
  "Ошибка импорта": "Import Error",
  "Ошибка предпросмотра": "Preview Error",
  "Файлы отчета": "Report Files",
  "HTML-отчет и служебный файл отчета для выбранной сессии.": "HTML report and manifest for the selected session.",
  "Открыть HTML-отчет": "Open HTML Report",
  "Манифест": "Manifest",
  "готовится": "preparing",
  "Сводные графики": "Summary Charts",
  "Все сгенерированные графики для этого раздела.": "All generated charts for this section.",
  "Калибровка вероятностей": "Probability Calibration",
  "Матрица ошибок": "Confusion Matrix",
  "Важность признаков": "Feature Importance",
  "Кривая обучения": "Learning Curve",
  "Кривая ошибки": "Loss Curve",
  "Сравнение моделей": "Model Comparison",
  "Precision-recall кривая": "Precision-Recall Curve",
  "ROC-кривая": "ROC Curve",
  "Распределение оценок": "Score Distribution",
  "Графики пока не сгенерированы.": "Charts have not been generated yet.",
  "Нет кандидатов для сравнения.": "No candidates to compare.",
  "Сравнение итоговой оценки, факторов и рисков.": "Comparison of final score, factors, and risks.",
  "Место": "Rank",
  "Кандидат": "Candidate",
  "Роль": "Role",
  "Оценка": "Score",
  "Навыки": "Skills",
  "Качество": "Quality",
  "Скорость": "Speed",
  "Развитие": "Learning",
  "Макс. риск": "Max Risk",
  "Оценка модели": "Model Score",
  "Итоговая оценка": "Adjusted Score",
  "Совпадение навыков": "Skill Match",
  "Учет рисков": "Risk Fit",
  "Нет кандидатов для отображения.": "No candidates to display.",
  "Режим:": "Mode:",
  "топ": "top",
  "Совпавшие навыки": "Matched Skills",
  "Недостающие навыки": "Missing Skills",
  "Риски не обнаружены.": "No risks detected.",
  "низкий": "low",
  "средний": "medium",
  "высокий": "high",
  "К выполнению": "To Do",
  "В работе": "In Progress",
  "Проверка": "Review",
  "Готово": "Done",
  "Заблокировано": "Blocked",
  "Не выполнено": "Failed",
  "Нет задач": "No tasks",
  "Задача без названия": "Untitled task",
  "Распределение задач и нагрузки по команде.": "Task and workload distribution across the team.",
  "Рабочий маршрут без кода": "No-Code Workflow",
  "Создайте датасет, обучите модели и проверьте назначения задач прямо из интерфейса.": "Create a dataset, train models, and check assignments directly from the interface.",
  "Создайте датасет": "Create a Dataset",
  "Обучите модели": "Train Models",
  "Проверьте назначения": "Check Assignments",
  "Перейти": "Open",
};

const routes = {
  "/": {
    title: "Главная",
    eyebrow: "Путь работы",
    modulePath: "./pages/dashboard.js",
    exports: ["renderDashboard", "renderPage", "default"],
    help: [
      "Начните здесь: создайте датасет, обучите модели, затем проверьте назначения задач.",
      "Карточки показывают, есть ли уже данные, модели и сохраненные результаты.",
      "Если чего-то нет, используйте кнопки перехода в нужную вкладку.",
    ],
  },
  "/generator": {
    title: "Генерация данных",
    eyebrow: "Датасеты",
    modulePath: "./pages/generator.js",
    exports: ["renderGenerator", "renderPage", "default"],
    help: [
      "Здесь создается полный учебный датасет: сотрудники, задачи, история выполнений и пары для обучения.",
      "Для своего домена выберите custom и задайте роли, уровни, навыки и собственные поля.",
      "После генерации переходите в Просмотр данных или сразу в Обучение.",
    ],
  },
  "/viewer": {
    title: "Просмотр данных",
    eyebrow: "Таблицы и фильтры",
    modulePath: "./pages/viewer.js",
    exports: ["renderViewer", "renderPage", "default"],
    help: [
      "Выберите датасет и таблицу, затем переключайтесь между списком, сводкой, таблицей, графиками и канбаном.",
      "Фильтры помогают быстро проверить статусы задач, роли, уровни и приоритеты.",
      "Удаление датасета стирает только выбранный пользовательский датасет.",
    ],
  },
  "/training": {
    title: "Обучение",
    eyebrow: "Модели",
    modulePath: "./pages/training.js",
    exports: ["renderTraining", "renderPage", "default"],
    help: [
      "Выберите датасет, целевой режим и модели. По умолчанию выбраны все доступные алгоритмы.",
      "Сначала можно построить признаки отдельно, но обычный сценарий — нажать Запустить обучение.",
      "После обучения сравните метрики здесь или откройте вкладку Модели.",
    ],
  },
  "/models": {
    title: "Модели",
    eyebrow: "Сравнение",
    modulePath: "./pages/models.js",
    exports: ["renderModels", "renderPage", "default"],
    help: [
      "Здесь видны обученные модели, их метрики, формат артефактов и статус проверки.",
      "Выберите сессию обучения и модель, чтобы посмотреть детали или проверить экспорт.",
      "Если моделей нет, сначала перейдите в Обучение.",
    ],
  },
  "/assignment-lab": {
    title: "Назначение задач",
    eyebrow: "Рекомендации",
    modulePath: "./pages/assignment_lab.js",
    exports: [
      "renderAssignmentLab",
      "renderAssignmentLabPage",
      "renderPage",
      "default",
    ],
    help: [
      "Здесь проверяется, кому модель рекомендует назначить одну задачу или весь список задач.",
      "Для основного сценария создайте проверочный набор из датасета, выберите обученную модель и запустите рекомендацию по одной задаче или распределение всех задач.",
      "LLM-пояснения включаются галочкой и зависят от доступности Ollama/Qwen.",
    ],
  },
  "/kanban-lab": {
    title: "Канбан-лаборатория",
    eyebrow: "Эксперименты",
    modulePath: "./pages/kanban_lab.js",
    exports: ["renderKanbanLab", "renderPage", "default"],
    help: [
      "Здесь можно загрузить копию проверочного набора или создать лабораторную копию из датасета.",
      "Перемещайте задачи между столбцами, переносите или очищайте целые столбцы, добавляйте ручные задачи в To Do.",
      "После правок нажмите Принять канбан и рассчитать рекомендации: модель увидит текущее состояние копии, а исходный датасет не изменится.",
    ],
  },
  "/reports": {
    title: "Отчеты",
    eyebrow: "Экспорт",
    modulePath: "./pages/reports.js",
    exports: ["renderReports", "renderReportsPage", "renderPage", "default"],
    help: [
      "Создавайте понятные отчеты по датасетам, моделям и результатам назначения.",
      "Готовые отчеты можно открыть ссылками или удалить из списка.",
    ],
  },
  "/settings": {
    title: "Настройки",
    eyebrow: "Профили и лимиты",
    modulePath: "./pages/settings.js",
    exports: ["renderSettings", "renderPage", "default"],
    help: [
      "Настройки задают значения по умолчанию, лимиты генерации и параметры LLM.",
      "Редактор профилей нужен для своих предметных областей: медицина, продажи, поддержка, разработка и другие.",
    ],
  },
  "/import-data": {
    title: "Импорт данных",
    eyebrow: "Свои файлы",
    modulePath: "./pages/import_data.js",
    exports: ["renderImportData", "renderPage", "default"],
    help: [
      "Загрузите свои CSV, JSON или Parquet-файлы вместо генерации синтетических данных.",
      "Предпросмотр проверяет структуру файла до сохранения.",
      "После успешного импорта датасет появится в Просмотре данных и Обучении.",
    ],
  },
};

const appState = {
  lastDatasetId: localStorageRef?.getItem("sandbox:lastDatasetId") || "",
  language: localStorageRef?.getItem("sandbox:language") || detectSystemLanguage(),
  theme: localStorageRef?.getItem("sandbox:theme") || "auto",
};

function detectSystemLanguage() {
  const languages = browserWindow?.navigator?.languages || [
    browserWindow?.navigator?.language,
  ];
  const primary = String(languages.find(Boolean) || "en").toLowerCase();
  return primary.startsWith("ru") ? "ru" : "en";
}

function currentLanguage() {
  return appState.language === "ru" ? "ru" : "en";
}

function normalizeText(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

export function translateText(value) {
  const text = normalizeText(value);

  if (!text || currentLanguage() === "ru") {
    return String(value ?? "");
  }

  return RU_TO_EN[text] || String(value ?? "");
}

function translatedRouteValue(value) {
  return currentLanguage() === "ru" ? value : translateText(value);
}

function storeOriginalAttribute(element, attributeName) {
  let values = attributeOriginals.get(element);

  if (!values) {
    values = new Map();
    attributeOriginals.set(element, values);
  }

  if (!values.has(attributeName)) {
    values.set(attributeName, element.getAttribute(attributeName) || "");
  }

  return values.get(attributeName);
}

function translateAttributes(root) {
  const attributes = ["aria-label", "title", "placeholder"];
  const elements = root.querySelectorAll?.("*") || [];

  elements.forEach((element) => {
    attributes.forEach((attributeName) => {
      if (!element.hasAttribute(attributeName)) {
        return;
      }

      const original = storeOriginalAttribute(element, attributeName);
      element.setAttribute(
        attributeName,
        currentLanguage() === "ru" ? original : translateText(original),
      );
    });
  });
}

function translateTextNodes(root) {
  const walker = browserDocument.createTreeWalker(
    root,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;

        if (!parent || ["SCRIPT", "STYLE", "CODE", "PRE", "TEXTAREA"].includes(parent.tagName)) {
          return NodeFilter.FILTER_REJECT;
        }

        return normalizeText(node.textContent)
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      },
    },
  );

  const nodes = [];
  let node = walker.nextNode();

  while (node) {
    nodes.push(node);
    node = walker.nextNode();
  }

  nodes.forEach((textNode) => {
    if (!textNodeOriginals.has(textNode)) {
      textNodeOriginals.set(textNode, textNode.textContent);
    }

    const original = textNodeOriginals.get(textNode);
    const translated = currentLanguage() === "ru" ? original : translateText(original);
    textNode.textContent = translated;
  });
}

function applyLanguage(root = browserDocument?.body) {
  if (!root || !browserDocument) {
    return;
  }

  browserDocument.documentElement.lang = currentLanguage();
  translateTextNodes(root);
  translateAttributes(root);
  updateLanguageButton();
}

if (browserWindow) {
  browserWindow.__compassAiApplyLanguage = applyLanguage;
}

function setLanguage(language) {
  appState.language = language === "ru" ? "ru" : "en";
  localStorageRef?.setItem("sandbox:language", appState.language);
  closeRouteHelp();
  renderLongTaskToasts();
  renderRoute();
}

function updateLanguageButton() {
  const button = browserDocument?.querySelector("#languageButton");

  if (!button) {
    return;
  }

  button.textContent = currentLanguage().toUpperCase();
  button.setAttribute(
    "aria-label",
    currentLanguage() === "ru" ? "Переключить язык" : "Switch language",
  );
  button.setAttribute(
    "title",
    currentLanguage() === "ru" ? "Переключить язык" : "Switch language",
  );
}

function nextLanguage() {
  return currentLanguage() === "ru" ? "en" : "ru";
}

function currentTheme() {
  return THEME_MODES.includes(appState.theme) ? appState.theme : "auto";
}

function themeLabel(theme = currentTheme()) {
  if (currentLanguage() === "ru") {
    return {
      auto: "Авто",
      light: "Светлая",
      dark: "Темная",
    }[theme] || "Авто";
  }

  return {
    auto: "Auto",
    light: "Light",
    dark: "Dark",
  }[theme] || "Auto";
}

function applyTheme() {
  const theme = currentTheme();
  browserDocument?.documentElement.setAttribute("data-theme", theme);
  updateThemeButton();
}

function setTheme(theme) {
  appState.theme = THEME_MODES.includes(theme) ? theme : "auto";
  localStorageRef?.setItem("sandbox:theme", appState.theme);
  applyTheme();
}

function nextTheme() {
  const index = THEME_MODES.indexOf(currentTheme());
  return THEME_MODES[(index + 1) % THEME_MODES.length];
}

function updateThemeButton() {
  const button = browserDocument?.querySelector("#themeButton");

  if (!button) {
    return;
  }

  const label = themeLabel();
  button.textContent = label;
  button.setAttribute(
    "aria-label",
    currentLanguage() === "ru" ? "Переключить тему" : "Switch theme",
  );
  button.setAttribute(
    "title",
    currentLanguage() === "ru"
      ? "Авто: тема следует системе. Нажмите, чтобы выбрать вручную."
      : "Auto follows the system theme. Click to choose manually.",
  );
}

function normalizePath(pathname) {
  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }

  return pathname;
}

function getCurrentRoute() {
  const path = normalizePath(browserWindow?.location.pathname || "/");
  return routes[path] ? path : "/";
}

function cacheBustedModulePath(modulePath) {
  return `${modulePath}?v=${encodeURIComponent(APP_BUILD_ID)}`;
}

async function loadRouteRenderer(route) {
  const pageModule = await import(cacheBustedModulePath(route.modulePath));

  for (const exportName of route.exports) {
    const renderer = pageModule[exportName];

    if (typeof renderer === "function") {
      return renderer;
    }
  }

  throw new Error(`Page renderer was not found for ${route.modulePath}`);
}

export function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function setLastDatasetId(datasetId) {
  appState.lastDatasetId = datasetId;
  localStorageRef?.setItem("sandbox:lastDatasetId", datasetId);
}

export function getLastDatasetId() {
  return appState.lastDatasetId;
}

export function toast(title, message = "") {
  const stack = browserDocument?.querySelector("#toastStack");
  const translatedTitle = translateText(title);
  const translatedMessage = translateText(message);

  if (!stack) {
    console.log(`${translatedTitle}: ${translatedMessage}`);
    return;
  }

  const item = browserDocument.createElement("div");
  item.className = "toast";
  item.innerHTML = `<strong>${htmlEscape(translatedTitle)}</strong><span>${htmlEscape(translatedMessage)}</span>`;
  stack.append(item);
  browserWindow?.setTimeout(() => item.remove(), 5200);
}

function ensureLongToastStack() {
  if (!browserDocument) {
    return null;
  }

  let stack = browserDocument.querySelector("#longToastStack");

  if (!stack) {
    stack = browserDocument.createElement("div");
    stack.id = "longToastStack";
    stack.className = "long-toast-stack";
    stack.setAttribute("aria-live", "polite");
    browserDocument.body.append(stack);
  }

  return stack;
}

function syncToastOffsets() {
  const stack = browserDocument?.querySelector("#longToastStack");
  const height = stack?.children.length ? stack.getBoundingClientRect().height : 0;
  const offset = height ? `${Math.ceil(height) + 12}px` : "0px";
  browserDocument?.documentElement.style.setProperty("--long-toast-offset", offset);
}

function translatedStep(state) {
  const steps = state.steps.length ? state.steps : ["Выполняется"];
  return steps[Math.min(state.stepIndex, steps.length - 1)] || state.message || "Выполняется";
}

function renderLongTaskToast(state) {
  if (!state.element) {
    return;
  }

  const percent = Math.max(0, Math.min(100, Math.round(state.percent)));
  const title = translateText(state.title);
  const message = translateText(state.message || translatedStep(state));
  const status = translateText(
    state.status === "done"
      ? "Завершено"
      : state.status === "error"
        ? "Ошибка"
        : "Выполняется",
  );

  state.element.dataset.status = state.status;
  state.element.innerHTML = `
    <div class="long-toast-header">
      <div>
        <strong class="long-toast-title">${htmlEscape(title)}</strong>
        <span class="long-toast-status">${htmlEscape(status)}</span>
      </div>
      <span class="long-toast-percent">${percent}%</span>
    </div>
    <p class="long-toast-message">${htmlEscape(message)}</p>
    <div class="long-toast-track" aria-hidden="true">
      <span class="long-toast-bar" style="width: ${percent}%"></span>
    </div>
  `;
}

function renderLongTaskToasts() {
  longTasks.forEach(renderLongTaskToast);
  syncToastOffsets();
}

function removeLongTask(id) {
  const state = longTasks.get(id);

  if (!state) {
    return;
  }

  if (state.timer) {
    browserWindow?.clearInterval(state.timer);
  }

  if (state.verifyTimer) {
    browserWindow?.clearInterval(state.verifyTimer);
  }

  state.element?.remove();
  longTasks.delete(id);
  syncToastOffsets();
}

function finishLongTask(id, status, message, removeDelayMs) {
  const current = longTasks.get(id);

  if (!current) {
    return;
  }

  if (current.timer) {
    browserWindow.clearInterval(current.timer);
    current.timer = null;
  }

  if (current.verifyTimer) {
    browserWindow.clearInterval(current.verifyTimer);
    current.verifyTimer = null;
  }

  current.status = status;
  current.percent = 100;
  current.message = message;
  renderLongTaskToast(current);
  syncToastOffsets();
  browserWindow.setTimeout(() => removeLongTask(id), removeDelayMs);
}

function datasetVerificationPassed(summary, verify) {
  const counts = summary?.summary_counts || summary?.dataset?.counts || {};
  const expected = verify?.expectedCounts || {};

  return Object.entries(expected).every(([key, value]) => {
    if (!Number.isFinite(value) || value <= 0) {
      return true;
    }

    return Number(counts[key] || 0) >= value;
  });
}

function startLongTaskVerification(id, verify) {
  if (!verify || verify.type !== "dataset" || !verify.datasetId || !browserWindow) {
    return null;
  }

  const intervalMs = Number.isFinite(verify.intervalMs) ? verify.intervalMs : 7000;
  const datasetKind = verify.datasetKind || "generated";
  const query = `?dataset_kind=${encodeURIComponent(datasetKind)}`;

  return browserWindow.setInterval(async () => {
    const current = longTasks.get(id);

    if (!current || current.status !== "running") {
      return;
    }

    try {
      const summary = await api.datasetSummary(verify.datasetId, query);

      if (datasetVerificationPassed(summary, verify)) {
        current.message = "Сохранение файлов...";
        finishLongTask(id, "done", verify.doneMessage || "Готово", 4200);
      }
    } catch (error) {
      // Verification is best-effort. The main request still owns real errors.
    }
  }, intervalMs);
}

function tickLongTask(id) {
  const state = longTasks.get(id);

  if (!state || state.status !== "running") {
    return;
  }

  const stepSize = state.percent < 55 ? 4 : state.percent < 82 ? 2 : 1;
  state.percent = Math.min(92, state.percent + stepSize);

  if (state.steps.length > 1) {
    const stepCount = state.steps.length;
    state.stepIndex = Math.min(
      stepCount - 1,
      Math.floor((state.percent / 94) * stepCount),
    );
  }

  state.message = translatedStep(state);
  renderLongTaskToast(state);
}

export function startLongTaskToast(options = {}) {
  const stack = ensureLongToastStack();
  const fallbackTitle = options.title || "Выполняется";

  if (!stack || !browserWindow) {
    return {
      update() {},
      done(message = "Завершено") {
        toast(fallbackTitle, message);
      },
      error(message = "Ошибка") {
        toast(fallbackTitle, message);
      },
      close() {},
    };
  }

  const id = `long-task-${++runtimeState.longTaskCounter}`;
  const element = browserDocument.createElement("div");
  element.className = "toast long-toast";
  element.dataset.status = "running";
  stack.append(element);

  const state = {
    id,
    element,
    title: fallbackTitle,
    message: options.message || options.steps?.[0] || "Подготовка...",
    steps: Array.isArray(options.steps) ? options.steps.filter(Boolean) : [],
    stepIndex: 0,
    percent: Number.isFinite(options.percent) ? options.percent : 6,
    status: "running",
    timer: null,
    verifyTimer: null,
  };

  longTasks.set(id, state);
  renderLongTaskToast(state);
  syncToastOffsets();
  state.timer = browserWindow.setInterval(() => tickLongTask(id), 1250);
  state.verifyTimer = startLongTaskVerification(id, options.verify);

  return {
    update(update = {}) {
      const current = longTasks.get(id);

      if (!current || current.status !== "running") {
        return;
      }

      if (update.title) {
        current.title = update.title;
      }

      if (update.message) {
        current.message = update.message;
      }

      if (Array.isArray(update.steps)) {
        current.steps = update.steps.filter(Boolean);
      }

      if (Number.isFinite(update.stepIndex)) {
        current.stepIndex = Math.max(0, Math.floor(update.stepIndex));
      }

      if (Number.isFinite(update.percent)) {
        current.percent = Math.max(0, Math.min(99, update.percent));
      }

      renderLongTaskToast(current);
      syncToastOffsets();
    },
    done(message = "Завершено") {
      finishLongTask(id, "done", message, 4200);
    },
    error(message = "Ошибка") {
      finishLongTask(id, "error", message, 7000);
    },
    close() {
      removeLongTask(id);
    },
  };
}

function bindGlobalAppEvents() {
  if (!browserWindow || runtimeState.globalEventsBound === true) {
    return;
  }

  runtimeState.globalEventsBound = true;

  browserWindow.addEventListener("sandbox-toast", (event) => {
    const detail = event.detail || {};
    toast(detail.title || detail.type || "Info", detail.message || "");
  });

  browserWindow.addEventListener("sandbox-long-task-start", (event) => {
    const detail = event.detail || {};

    if (detail.controller) {
      return;
    }

    detail.controller = startLongTaskToast(detail.options || detail);
  });

  browserWindow.addEventListener("resize", syncToastOffsets);
}

export function renderError(error) {
  return `
    <article class="card">
      <h2>${htmlEscape(translateText("Ошибка"))}</h2>
      <p class="muted">${htmlEscape(error.message || error)}</p>
    </article>
  `;
}

export function tableFromRows(rows, columns) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return `<div class="empty">${htmlEscape(translateText("Нет данных для отображения."))}</div>`;
  }

  const resolvedColumns = columns || Object.keys(rows[0]);
  const head = resolvedColumns
    .map((column) => `<th>${htmlEscape(column)}</th>`)
    .join("");
  const body = rows
    .map((row) => {
      const cells = resolvedColumns
        .map((column) => {
          const value = row[column];
          const displayValue =
            typeof value === "object" ? JSON.stringify(value) : String(value ?? "");

          return `<td>${htmlEscape(displayValue)}</td>`;
        })
        .join("");

      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="table-wrap">
      <table class="table">
        <thead><tr>${head}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

export function pageNotice(title, body, badge = "Backend stage pending") {
  return `
    <article class="card">
      <span class="badge">${htmlEscape(translateText(badge))}</span>
      <h2>${htmlEscape(translateText(title))}</h2>
      <p class="muted">${htmlEscape(translateText(body))}</p>
    </article>
  `;
}

function renderHelpModal(route) {
  const helpItems = route.help || [];

  return `
    <div class="modal-backdrop" data-help-modal>
      <section class="help-modal" role="dialog" aria-modal="true" aria-labelledby="helpTitle">
        <div class="section-heading">
          <div>
            <p class="eyebrow">${htmlEscape(translateText("Справка"))}</p>
            <h2 id="helpTitle">${htmlEscape(translatedRouteValue(route.title))}</h2>
          </div>
          <button class="icon-help-button" id="closeHelpButton" type="button" aria-label="${htmlEscape(translateText("Закрыть справку"))}">×</button>
        </div>
        <div class="help-list">
          ${helpItems
            .map(
              (item, index) => `
                <article class="help-step">
                  <span>${index + 1}</span>
                  <p>${htmlEscape(translateText(item))}</p>
                </article>
              `,
            )
            .join("")}
        </div>
      </section>
    </div>
  `;
}

function openRouteHelp() {
  const route = routes[getCurrentRoute()];
  const existing = browserDocument?.querySelector("[data-help-modal]");
  existing?.remove();
  browserDocument?.body.insertAdjacentHTML("beforeend", renderHelpModal(route));
  browserDocument?.querySelector("#closeHelpButton")?.focus();
}

function closeRouteHelp() {
  browserDocument?.querySelector("[data-help-modal]")?.remove();
}

async function updateBackendStatus() {
  const statusElement = browserDocument?.querySelector("#backendStatus");

  if (!statusElement) {
    return;
  }

  try {
    await api.health();
    statusElement.className = "status-pill status-ok";
    statusElement.innerHTML = `<span class="status-dot"></span><span>${htmlEscape(translateText("Работает"))}</span>`;
  } catch (error) {
    statusElement.className = "status-pill status-error";
    statusElement.innerHTML = `<span class="status-dot"></span><span>${htmlEscape(translateText("Недоступен"))}</span>`;
  }
}

async function renderRoute() {
  const routePath = getCurrentRoute();
  const route = routes[routePath];
  const root = browserDocument?.querySelector("#appRoot");

  if (!root) {
    return;
  }

  browserDocument.querySelector("#pageTitle").textContent = translatedRouteValue(route.title);
  browserDocument.querySelector("#routeEyebrow").textContent = translatedRouteValue(route.eyebrow);
  browserDocument.title = routePath === "/"
    ? "COMPASS AI"
    : `COMPASS AI · ${translatedRouteValue(route.title)}`;

  browserDocument.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === routePath);
  });

  root.classList.add("loading");
  root.innerHTML = `<div class="empty">${htmlEscape(translateText("Загрузка..."))}</div>`;

  try {
    const renderer = await loadRouteRenderer(route);
    const rendered = await renderer(root);

    if (typeof rendered === "string") {
      root.innerHTML = rendered;
    } else if (rendered === undefined && root.innerHTML === "") {
      root.innerHTML = "";
    } else if (rendered !== undefined) {
      root.innerHTML = String(rendered);
    }
  } catch (error) {
    root.innerHTML = renderError(error);
    console.error(error);
  } finally {
    root.classList.remove("loading");
    applyLanguage(browserDocument.body);
  }
}

function bindNavigation() {
  browserDocument?.body.addEventListener("click", (event) => {
    const link = event.target.closest("[data-link]");

    if (!link) {
      return;
    }

    const url = new URL(link.href);

    if (url.origin !== browserWindow?.location.origin) {
      return;
    }

    event.preventDefault();
    browserWindow.history.pushState({}, "", url.pathname);
    closeRouteHelp();
    renderRoute();
  });

  browserWindow?.addEventListener("popstate", renderRoute);

  browserDocument
    ?.querySelector("#languageButton")
    ?.addEventListener("click", () => {
      setLanguage(nextLanguage());
    });

  browserDocument
    ?.querySelector("#themeButton")
    ?.addEventListener("click", () => {
      setTheme(nextTheme());
    });

  browserDocument
    ?.querySelector("#refreshButton")
    ?.addEventListener("click", async () => {
      await updateBackendStatus();
      await renderRoute();
      toast("Обновлено", "Данные страницы запрошены заново.");
    });

  browserDocument
    ?.querySelector("#helpButton")
    ?.addEventListener("click", openRouteHelp);

  browserDocument?.body.addEventListener("click", (event) => {
    if (event.target.closest("#closeHelpButton")) {
      closeRouteHelp();
      return;
    }

    if (event.target.matches("[data-help-modal]")) {
      closeRouteHelp();
    }
  });

  browserWindow?.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeRouteHelp();
    }
  });
}

bindGlobalAppEvents();

browserDocument?.addEventListener("DOMContentLoaded", async () => {
  if (runtimeState.appBootstrapped === true) {
    return;
  }

  runtimeState.appBootstrapped = true;
  applyTheme();
  bindNavigation();
  await updateBackendStatus();
  await renderRoute();
  applyLanguage(browserDocument.body);
});

browserWindow
  ?.matchMedia?.("(prefers-color-scheme: dark)")
  ?.addEventListener?.("change", () => {
    if (currentTheme() === "auto") {
      applyTheme();
    }
  });
