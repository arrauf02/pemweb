let tasks = [];


/**
 * Memuat data tugas dari localStorage saat aplikasi pertama kali dimuat.
 */
function loadTasks() {
    const storedTasks = localStorage.getItem('tasks');
    if (storedTasks) {
        tasks = JSON.parse(storedTasks);
    }
    // Render tampilan setelah memuat data
    renderTasks();
}

/**
 * Menyimpan array tugas saat ini ke localStorage.
 */
function saveTasks() {
    localStorage.setItem('tasks', JSON.stringify(tasks));
    updateIncompleteCount(); // Perbarui hitungan setiap kali data disimpan
}

// --- Fungsi Validasi ---

/**
 * Melakukan validasi pada input form tugas.
 * @param {string} name - Nama tugas.
 * @param {string} deadline - Tanggal deadline.
 * @returns {string|null} - Pesan error jika ada, atau null jika valid.
 */
function validateTask(name, deadline) {
    if (!name.trim()) {
        return "Nama tugas tidak boleh kosong.";
    }

    if (!deadline) {
        return "Deadline tugas wajib diisi.";
    }

    const deadlineDate = new Date(deadline);
    const today = new Date();
    // Reset waktu untuk perbandingan tanggal saja
    today.setHours(0, 0, 0, 0);

    // Cek apakah tanggal deadline adalah tanggal yang valid dan bukan tanggal masa lalu (kecuali hari ini)
    if (isNaN(deadlineDate.getTime()) || deadlineDate < today) {
        return "Deadline tidak valid atau sudah terlewat.";
    }

    return null; // Valid
}

// --- Fungsi Interaksi Pengguna & Rendering ---

/**
 * Menambahkan tugas baru ke array dan localStorage.
 * @param {Event} e - Event submit form.
 */
function addTask(e) {
    e.preventDefault();

    const nameInput = document.getElementById('task-name');
    const courseInput = document.getElementById('task-course');
    const deadlineInput = document.getElementById('task-deadline');
    const errorDisplay = document.getElementById('form-error');

    const name = nameInput.value;
    const course = courseInput.value;
    const deadline = deadlineInput.value;

    const validationError = validateTask(name, deadline);

    if (validationError) {
        errorDisplay.textContent = validationError;
        return;
    }

    errorDisplay.textContent = ''; // Hapus error jika valid

    const newTask = {
        id: Date.now(), // ID unik berdasarkan timestamp
        name: name,
        course: course || 'Umum',
        deadline: deadline,
        isCompleted: false
    };

    tasks.push(newTask);
    saveTasks();
    renderTasks();

    // Reset form
    nameInput.value = '';
    courseInput.value = '';
    deadlineInput.value = '';
}

/**
 * Menandai tugas sebagai selesai atau belum selesai.
 * @param {number} id - ID tugas yang akan diubah statusnya.
 */
function toggleComplete(id) {
    const taskIndex = tasks.findIndex(task => task.id === id);
    if (taskIndex !== -1) {
        tasks[taskIndex].isCompleted = !tasks[taskIndex].isCompleted;
        saveTasks();
        renderTasks();
    }
}

/**
 * Menghapus tugas dari array dan localStorage.
 * @param {number} id - ID tugas yang akan dihapus.
 */
function deleteTask(id) {
    // Konfirmasi sebelum menghapus
    if (confirm("Anda yakin ingin menghapus tugas ini?")) {
        tasks = tasks.filter(task => task.id !== id);
        saveTasks();
        renderTasks();
    }
}

/**
 * Mengambil tugas yang telah difilter dan dicari.
 * @returns {Array<Object>} - Array tugas yang telah difilter.
 */
function getFilteredTasks() {
    const filterStatus = document.getElementById('filter-status').value;
    const searchCourse = document.getElementById('search-course').value.toLowerCase();

    let filteredTasks = tasks;

    // 1. Filter Status
    if (filterStatus === 'incomplete') {
        filteredTasks = filteredTasks.filter(task => !task.isCompleted);
    } else if (filterStatus === 'completed') {
        filteredTasks = filteredTasks.filter(task => task.isCompleted);
    }

    // 2. Filter/Cari Mata Kuliah
    if (searchCourse) {
        filteredTasks = filteredTasks.filter(task => 
            task.course.toLowerCase().includes(searchCourse)
        );
    }

    return filteredTasks;
}

/**
 * Merender daftar tugas ke dalam DOM berdasarkan filter saat ini.
 */
function renderTasks() {
    const taskList = document.getElementById('task-list');
    const filteredTasks = getFilteredTasks();
    
    taskList.innerHTML = ''; // Kosongkan daftar

    if (filteredTasks.length === 0) {
        taskList.innerHTML = `<p style="text-align: center; color: #999;">Tidak ada tugas yang cocok dengan filter.</p>`;
        return;
    }

    // Urutkan: Tugas Belum Selesai (segera) -> Tugas Selesai (paling bawah)
    filteredTasks.sort((a, b) => {
        // Prioritaskan tugas belum selesai di atas
        if (a.isCompleted && !b.isCompleted) return 1;
        if (!a.isCompleted && b.isCompleted) return -1;
        // Jika status sama, urutkan berdasarkan deadline (yang paling dekat di atas)
        return new Date(a.deadline) - new Date(b.deadline);
    });

    filteredTasks.forEach(task => {
        const li = document.createElement('li');
        li.className = `task-item ${task.isCompleted ? 'completed' : ''}`;
        
        const completeButtonText = task.isCompleted ? 'Batalkan' : 'Selesai';
        const completeButtonClass = task.isCompleted ? 'complete-btn' : 'complete-btn mark-done';

        li.innerHTML = `
            <div class="task-info">
                <h4>${task.name} <span style="font-size: 0.8em; color: #007bff;">(${task.course})</span></h4>
                <p>Deadline: ${new Date(task.deadline).toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                <p style="color: ${task.isCompleted ? 'green' : (new Date(task.deadline) < new Date() ? 'red' : '#333')}; font-weight: bold;">Status: ${task.isCompleted ? 'Selesai' : 'Belum Selesai'}</p>
            </div>
            <div class="task-actions">
                <button class="${completeButtonClass}" onclick="toggleComplete(${task.id})">${completeButtonText}</button>
                <button class="delete-btn" onclick="deleteTask(${task.id})">Hapus</button>
            </div>
        `;
        taskList.appendChild(li);
    });
}

/**
 * Memperbarui tampilan jumlah tugas yang belum selesai.
 */
function updateIncompleteCount() {
    const incompleteCount = tasks.filter(task => !task.isCompleted).length;
    document.getElementById('incomplete-count').textContent = incompleteCount;
}

// --- Inisialisasi Aplikasi ---

// 1. Tambahkan event listener untuk form
document.getElementById('task-form').addEventListener('submit', addTask);

// 2. Tambahkan event listener untuk filter/pencarian
document.getElementById('filter-status').addEventListener('change', renderTasks);
document.getElementById('search-course').addEventListener('input', renderTasks);

// 3. Muat tugas saat halaman pertama kali dibuka
document.addEventListener('DOMContentLoaded', loadTasks);