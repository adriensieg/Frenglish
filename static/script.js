let editModal;

document.addEventListener('DOMContentLoaded', () => {
    editModal = new bootstrap.Modal(document.getElementById('editModal'));
    setupModeToggle();
    loadEntries();
    // Initialize challenge mode if selected
    if (document.getElementById('challengeMode').checked) {
        loadRandomEntry();
    }
});

function setupModeToggle() {
    const addMode = document.getElementById('addMode');
    const seeMode = document.getElementById('seeMode');
    const consultingMode = document.getElementById('consultingMode');
    const challengeMode = document.getElementById('challengeMode');
    const addSection = document.getElementById('addSection');
    const seeSection = document.getElementById('seeSection');
    const consultingSection = document.getElementById('consultingSection');
    const challengeSection = document.getElementById('challengeSection');

    addMode.addEventListener('change', () => {
        addSection.style.display = 'block';
        seeSection.style.display = 'none';
        consultingSection.style.display = 'none';
        challengeSection.style.display = 'none';
        document.getElementById('resultSection').style.display = 'none';
    });

    seeMode.addEventListener('change', () => {
        addSection.style.display = 'none';
        seeSection.style.display = 'block';
        consultingSection.style.display = 'none';
        challengeSection.style.display = 'none';
        loadEntries();
    });

    consultingMode.addEventListener('change', () => {
        addSection.style.display = 'none';
        seeSection.style.display = 'none';
        consultingSection.style.display = 'block';
        challengeSection.style.display = 'none';
        document.getElementById('consultingResultSection').style.display = 'none';
        document.getElementById('consultingInput').value = '';
        document.getElementById('consultingOutput').value = '';
    });

    challengeMode.addEventListener('change', () => {
        addSection.style.display = 'none';
        seeSection.style.display = 'none';
        consultingSection.style.display = 'none';
        challengeSection.style.display = 'block';
        loadRandomEntry();
    });
}

async function processConsulting() {
    const inputText = document.getElementById('consultingInput').value.trim();
    const spinner = document.getElementById('consultingSpinner');
    const buttonText = document.getElementById('consultingButtonText');
    const button = document.getElementById('consultingButton');
    const resultSection = document.getElementById('consultingResultSection');

    if (!inputText) {
        alert('Please enter some text');
        return;
    }

    try {
        // Show loading state
        spinner.style.display = 'inline-block';
        buttonText.textContent = 'Processing...';
        button.disabled = true;

        const response = await fetch('/consulting', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: inputText
            }),
        });

        const data = await response.json();
        if (response.ok) {
            document.getElementById('consultingOutput').value = data.result;
            resultSection.style.display = 'block';
        } else {
            throw new Error(data.error || 'Error processing text');
        }
    } catch (error) {
        console.error('Error processing text:', error);
        alert(error.message || 'Error processing text');
    } finally {
        // Hide loading state
        spinner.style.display = 'none';
        buttonText.textContent = 'Submit';
        button.disabled = false;
    }
}

async function addEntry() {
    const english = document.getElementById('englishInput').value.trim();
    const french = document.getElementById('frenchInput').value.trim();
    const loadingSpinner = document.getElementById('loadingSpinner');
    const buttonText = document.getElementById('buttonText');
    const addButton = document.getElementById('addButton');
    const resultSection = document.getElementById('resultSection');

    if (!english && !french) {
        alert('Please fill in at least one field');
        return;
    }

    try {
        // Show loading state
        loadingSpinner.style.display = 'inline-block';
        buttonText.textContent = 'Adding...';
        addButton.disabled = true;
        resultSection.style.display = 'none';

        const response = await fetch('/entries', {
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
            // Display the complete result
            document.getElementById('resultEnglish').textContent = data.english || english;
            document.getElementById('resultFrench').textContent = data.french || french;
            document.getElementById('resultContext').textContent = data.context || '';
            resultSection.style.display = 'block';

            clearInputs();
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
        const response = await fetch('/entries');
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

async function loadRandomEntry() {
    try {
        const button = document.getElementById('nextChallengeButton');
        button.disabled = true;
        button.innerHTML = 'Loading...';

        const response = await fetch('/random-entry');
        if (!response.ok) {
            throw new Error('Failed to load random entry');
        }
        
        const entry = await response.json();
        
        // Display the entry data
        document.getElementById('challengeEnglish').textContent = entry.english || '';
        document.getElementById('challengeFrench').textContent = entry.french || '';
        document.getElementById('challengeContext').textContent = entry.context || '';
        
    } catch (error) {
        console.error('Error loading random entry:', error);
        alert('Error loading random entry');
    } finally {
        const button = document.getElementById('nextChallengeButton');
        button.disabled = false;
        button.innerHTML = 'Next Challenge →';
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
        
        // Format the timestamp
        const date = new Date(entry.timestamp * 1000);
        const formattedDate = date.toLocaleString();

        // Create the edit button
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
            <td><small class="text-muted">${formattedDate}</small></td>
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
        const response = await fetch(`/entries/${id}`, {
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
        const response = await fetch(`/entries/${id}`, {
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