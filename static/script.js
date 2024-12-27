const API_URL = 'http://localhost:5000';
let editModal;

document.addEventListener('DOMContentLoaded', () => {
    editModal = new bootstrap.Modal(document.getElementById('editModal'));
    setupModeToggle();
    loadEntries();
});

function setupModeToggle() {
    const addMode = document.getElementById('addMode');
    const seeMode = document.getElementById('seeMode');
    const addSection = document.getElementById('addSection');
    const seeSection = document.getElementById('seeSection');

    addMode.addEventListener('change', () => {
        addSection.style.display = 'block';
        seeSection.style.display = 'none';
    });

    seeMode.addEventListener('change', () => {
        addSection.style.display = 'none';
        seeSection.style.display = 'block';
        loadEntries();
    });
}

async function addEntry() {
    const english = document.getElementById('englishInput').value.trim();
    const french = document.getElementById('frenchInput').value.trim();
    const loadingSpinner = document.getElementById('loadingSpinner');
    const buttonText = document.getElementById('buttonText');
    const addButton = document.getElementById('addButton');

    if (!english && !french) {
        alert('Please fill in at least one field');
        return;
    }

    try {
        // Show loading state
        loadingSpinner.style.display = 'inline-block';
        buttonText.textContent = 'Adding...';
        addButton.disabled = true;

        const response = await fetch(`${API_URL}/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                english,
                french,
                context: "",
                notes: ""
            }),
        });

        const data = await response.json();
        if (response.ok) {
            clearInputs();
            alert(data.message || 'Entry added successfully!');
            if (document.getElementById('seeMode').checked) {
                loadEntries();
            }
        } else {
            throw new Error(data.error || 'Error adding entry');
        }
    } catch (error) {
        console.error('Error adding entry:', error);
        alert(error.message || 'Error adding entry');
    } finally {
        // Hide loading state
        loadingSpinner.style.display = 'none';
        buttonText.textContent = 'Add Entry';
        addButton.disabled = false;
    }
}

async function loadEntries() {
    try {
        const response = await fetch(`${API_URL}/entries`);
        if (!response.ok) {
            throw new Error('Failed to load entries');
        }
        const entries = await response.json();
        displayEntries(entries);
    } catch (error) {
        console.error('Error loading entries:', error);
        alert('Error loading entries');
    }
}

function displayEntries(entries) {
    const tableBody = document.getElementById('entriesTable');
    tableBody.innerHTML = '';

    entries.forEach(entry => {
        const row = document.createElement('tr');
        const english = cleanInput(entry.english || '');
        const french = cleanInput(entry.french || '');
        const context = cleanInput(entry.context || '').replace(/\\n/g, '<br><br>');
        const notes = cleanInput(entry.notes || '').replace(/\\n/g, '<br><br>');

        // Create the edit button using createElement instead of innerHTML
        const editButton = document.createElement('button');
        editButton.className = 'btn btn-edit btn-sm';
        editButton.textContent = 'Edit';
        editButton.addEventListener('click', () => {
            editEntry(entry.id, entry.english, entry.french, entry.context, entry.notes);
        });

        // Create the delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => {
            deleteEntry(entry.id);
        });

        // Create the actions cell
        const actionsCell = document.createElement('td');
        actionsCell.appendChild(editButton);
        actionsCell.appendChild(document.createTextNode(' ')); // Space between buttons
        actionsCell.appendChild(deleteButton);

        row.innerHTML = `
            <td>${english}</td>
            <td>${french}</td>
            <td>${context}</td>
            <td>${notes}</td>
        `;
        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    });
}

function cleanInput(input) {
    return escapeHtml(input).replace(/\\/g, '').replace(/'/g, '&#39;');
}

function escapeQuotes(input) {
    return (input || '').replace(/'/g, "\\'");
}

function editEntry(id, english, french, context, notes) {
    document.getElementById('editId').value = id || '';
    document.getElementById('editEnglish').value = english || '';
    document.getElementById('editFrench').value = french || '';
    document.getElementById('editContext').value = context || '';
    document.getElementById('editNotes').value = notes || '';
    editModal.show();
}

async function saveEdit() {
    const id = document.getElementById('editId').value;
    if (!id) {
        alert('Error: No document ID found');
        return;
    }

    const english = document.getElementById('editEnglish').value.trim();
    const french = document.getElementById('editFrench').value.trim();
    const context = document.getElementById('editContext').value.trim();
    const notes = document.getElementById('editNotes').value.trim();

    if (!english && !french) {
        alert('Please fill in at least one field');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/entries/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                english,
                french,
                context,
                notes
            }),
        });

        const data = await response.json();
        if (response.ok) {
            editModal.hide();
            loadEntries();
            alert(data.message || 'Entry updated successfully!');
        } else {
            throw new Error(data.error || 'Error updating entry');
        }
    } catch (error) {
        console.error('Error updating entry:', error);
        alert(error.message || 'Error updating entry');
    }
}

async function deleteEntry(id) {
    if (!id) {
        alert('Error: No document ID found');
        return;
    }

    if (!confirm('Are you sure you want to delete this entry?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/entries/${id}`, {
            method: 'DELETE',
        });

        const data = await response.json();
        if (response.ok) {
            loadEntries();
            alert(data.message || 'Entry deleted successfully!');
        } else {
            throw new Error(data.error || 'Error deleting entry');
        }
    } catch (error) {
        console.error('Error deleting entry:', error);
        alert(error.message || 'Error deleting entry');
    }
}

function clearInputs() {
    document.getElementById('englishInput').value = '';
    document.getElementById('frenchInput').value = '';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function decodeHtml(str) {
    const div = document.createElement('div');
    div.innerHTML = str;
    return div.textContent || div.innerText;
}
