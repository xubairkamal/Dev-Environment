/**
 * main.js - User Management CRUD Logic
 * Updated: 2026-01-26 (Username & Password Support)
 */

console.log("main.js initialized...");

// --- DELETE USER LOGIC ---
function deleteUser(userId, versionHex) {
    if (confirm("Are you sure you want to PERMANENTLY DELETE this user? This action cannot be undone.")) {
        const csrfToken = getCookie('csrftoken');

        fetch('/setup/users/delete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                user_id: userId,
                version_hex: versionHex
            })
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.status === 'success') location.reload();
            })
            .catch(error => {
                console.error('Delete Error:', error);
                alert("Server error: Could not complete the delete operation.");
            });
    }
}

// --- UPDATE USER LOGIC ---
function openUserEditModal(id, username, name, statusId, statusName, versionHex) {
    console.log("Opening Edit Modal for:", username);

    // Form fields populate karein
    document.getElementById('editUserId').value = id;
    document.getElementById('editUsername').value = username; // Naya: Username field
    document.getElementById('editFullName').value = name;
    document.getElementById('editPassword').value = ""; // Security ke liye password field hamesha empty rahe
    document.getElementById('editVersionHex').value = versionHex;

    // Select2 for Status
    var $statusSelect = $('#editStatus');
    if ($statusSelect.find("option[value='" + statusId + "']").length === 0) {
        var newOption = new Option(statusName, statusId, true, true);
        $statusSelect.append(newOption).trigger('change');
    } else {
        $statusSelect.val(statusId).trigger('change');
    }

    var editModal = new bootstrap.Modal(document.getElementById('editUserModal'));
    editModal.show();
}

function saveUserChanges() {
    const payload = {
        user_id: document.getElementById('editUserId').value,
        username: document.getElementById('editUsername').value, // windows_username -> username
        full_name: document.getElementById('editFullName').value,
        password: document.getElementById('editPassword').value, // Optional password
        status_id: $('#editStatus').val(),
        version_hex: document.getElementById('editVersionHex').value
    };

    if (!payload.username || !payload.full_name || !payload.status_id) {
        alert("Username, Full Name and Status are required.");
        return;
    }

    fetch('/setup/users/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    })
        .then(r => r.json())
        .then(data => {
            alert(data.message);
            if (data.status === 'success') location.reload();
        })
        .catch(err => console.error("Update Error:", err));
}

// --- ADD USER LOGIC ---
function openAddUserModal() {
    document.getElementById('addUserForm').reset();
    $('#addStatus').val(null).trigger('change');

    var addModal = new bootstrap.Modal(document.getElementById('addUserModal'));
    addModal.show();
}

function saveNewUser() {
    const payload = {
        username: document.getElementById('addUsername').value, // windows_username -> username
        full_name: document.getElementById('addFullName').value,
        password: document.getElementById('addPassword').value, // Naya: Password field
        status_id: $('#addStatus').val()
    };

    // Validation: Add mein password lazmi rakhte hain
    if (!payload.username || !payload.full_name || !payload.password || !payload.status_id) {
        alert("Please fill all fields, including password.");
        return;
    }

    fetch('/setup/users/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    })
        .then(r => r.json())
        .then(data => {
            alert(data.message);
            if (data.status === 'success') location.reload();
        })
        .catch(err => console.error("Add Error:", err));
}

// --- UTILITIES ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}