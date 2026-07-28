document.addEventListener('DOMContentLoaded', () => {
  const monthSelect = document.getElementById('monthSelect');
  const daySelect = document.getElementById('daySelect');
  const todoList = document.getElementById('todoList');
  const doneList = document.getElementById('doneList');
  const addBtn = document.getElementById('addBtn');

  // Populate Days 1-31
  for (let i = 1; i <= 31; i++) {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = i;
    daySelect.appendChild(opt);
  }

  // Initial State from UI Mockups if empty
  let tasks = [
    { id: 1, text: 'Task 1', completed: false },
    { id: 2, text: 'Task 2', completed: false },
    { id: 3, text: 'Task 3', completed: true },
    { id: 4, text: 'Task 4', completed: true }
  ];

  // Key for LocalStorage based on selected Date
  function getStorageKey() {
    const month = monthSelect.value || 'default';
    const day = daySelect.value || 'default';
    return `daily_calendar_tasks_${month}_${day}`;
  }

  function loadTasks() {
    const key = getStorageKey();
    const saved = localStorage.getItem(key);
    if (saved) {
      try {
        tasks = JSON.parse(saved);
      } catch (e) {
        console.error("Error loading tasks", e);
      }
    } else {
      // Default initial tasks matching designs
      tasks = [
        { id: 1, text: 'Task 1', completed: false },
        { id: 2, text: 'Task 2', completed: false },
        { id: 3, text: 'Task 3', completed: true },
        { id: 4, text: 'Task 4', completed: true }
      ];
    }
    render();
  }

  function saveTasks() {
    const key = getStorageKey();
    localStorage.setItem(key, JSON.stringify(tasks));
  }

  monthSelect.addEventListener('change', loadTasks);
  daySelect.addEventListener('change', loadTasks);

  function render() {
    todoList.innerHTML = '';
    doneList.innerHTML = '';

    const pendingTasks = tasks.filter(t => !t.completed);
    const completedTasks = tasks.filter(t => t.completed);

    pendingTasks.forEach(task => {
      const item = createTaskElement(task);
      todoList.appendChild(item);
    });

    completedTasks.forEach(task => {
      const item = createTaskElement(task);
      doneList.appendChild(item);
    });
  }

  function createTaskElement(task) {
    const item = document.createElement('div');
    item.className = `task-item ${task.completed ? 'completed' : ''}`;
    item.dataset.id = task.id;

    // Custom Radio / Circle Checkbox
    const radio = document.createElement('div');
    radio.className = 'task-radio';
    const checkSpan = document.createElement('span');
    checkSpan.className = 'task-radio-check';
    checkSpan.textContent = '✔';
    radio.appendChild(checkSpan);

    radio.addEventListener('click', () => {
      task.completed = !task.completed;
      saveTasks();
      render();
    });

    // Task Input Wrapper (Underlined Input)
    const inputWrapper = document.createElement('div');
    inputWrapper.className = 'task-input-wrapper';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'task-input';
    input.value = task.text;

    input.addEventListener('change', (e) => {
      task.text = e.target.value;
      saveTasks();
    });

    input.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') {
        input.blur();
      }
    });

    inputWrapper.appendChild(input);

    item.appendChild(radio);
    item.appendChild(inputWrapper);

    // Mobile Actions (edit / 🗑) for pending tasks
    if (!task.completed) {
      const actions = document.createElement('div');
      actions.className = 'task-actions';

      const editBtn = document.createElement('button');
      editBtn.className = 'btn-edit-inline';
      editBtn.innerHTML = '✏️';
      editBtn.title = 'Edit Task';
      editBtn.addEventListener('click', () => {
        input.focus();
        input.select();
      });

      const sep = document.createElement('span');
      sep.className = 'action-separator';
      sep.textContent = '/';

      const trashBtn = document.createElement('button');
      trashBtn.className = 'btn-trash-inline';
      trashBtn.innerHTML = '🗑️';
      trashBtn.title = 'Delete Task';
      trashBtn.addEventListener('click', () => {
        deleteTask(task.id);
      });

      actions.appendChild(editBtn);
      actions.appendChild(sep);
      actions.appendChild(trashBtn);

      item.appendChild(actions);
    }

    return item;
  }

  // Add Task
  addBtn.addEventListener('click', () => {
    const newId = Date.now();
    const newTask = {
      id: newId,
      text: `Task ${tasks.length + 1}`,
      completed: false
    };
    tasks.push(newTask);
    saveTasks();
    render();

    // Automatically focus the new task input
    setTimeout(() => {
      const newEl = todoList.querySelector(`[data-id="${newId}"] .task-input`);
      if (newEl) {
        newEl.focus();
        newEl.select();
      }
    }, 50);
  });

  // Delete Task
  function deleteTask(id) {
    tasks = tasks.filter(t => t.id !== id);
    saveTasks();
    render();
  }

  // Initial load
  loadTasks();
});
