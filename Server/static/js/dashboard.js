// Dashboard JavaScript for Farmware
let farmers = [];
let advisories = [];

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateLastUpdated();
    loadInitialData();
    setupEventListeners();
});

function updateLastUpdated() {
    document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
}

function loadInitialData() {
    refreshFarmers();
    refreshAdvisories();
}

function setupEventListeners() {
    // Form submission
    document.getElementById('sendAdvisoryForm').addEventListener('submit', handleSendAdvisory);
    
    // Dropdown change events for preview
    document.getElementById('messageId').addEventListener('change', updatePreview);
    document.getElementById('phoneNumber').addEventListener('change', updatePreview);
}

// Refresh farmers data
async function refreshFarmers() {
    try {
        showLoading('farmersTableBody');
        
        const response = await fetch('/api/farmers');
        const data = await response.json();
        
        if (data.success) {
            farmers = data.farmers;
            displayFarmers(farmers);
            populateFarmerDropdown(farmers);
            document.getElementById('farmersCount').textContent = farmers.length;
        } else {
            showError('farmersTableBody', 'Failed to load farmers: ' + data.error);
        }
    } catch (error) {
        console.error('Error fetching farmers:', error);
        showError('farmersTableBody', 'Error loading farmers');
    }
}

// Refresh advisories data
async function refreshAdvisories() {
    try {
        showLoading('advisoriesTableBody');
        
        const response = await fetch('/api/advisories');
        const data = await response.json();
        
        if (data.success) {
            advisories = data.advisories;
            displayAdvisories(advisories);
            populateAdvisoryDropdown(advisories);
            document.getElementById('advisoriesCount').textContent = advisories.length;
        } else {
            showError('advisoriesTableBody', 'Failed to load advisories: ' + data.error);
        }
    } catch (error) {
        console.error('Error fetching advisories:', error);
        showError('advisoriesTableBody', 'Error loading advisories');
    }
}

// Display farmers in table
function displayFarmers(farmersData) {
    const tbody = document.getElementById('farmersTableBody');
    
    if (farmersData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No farmers found</td></tr>';
        return;
    }
    
    tbody.innerHTML = farmersData.map(farmer => `
        <tr>
            <td><strong>${farmer.id}</strong></td>
            <td>
                <i class="fas fa-phone text-success"></i> 
                ${farmer.phone}
            </td>
            <td>
                <span class="secret-key">${farmer.secret_key_preview}</span>
            </td>
            <td>
                <small class="text-muted">${formatDate(farmer.created_at)}</small>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="selectFarmer('${farmer.phone}')">
                    <i class="fas fa-mouse-pointer"></i> Select
                </button>
            </td>
        </tr>
    `).join('');
}

// Display advisories in table
function displayAdvisories(advisoriesData) {
    const tbody = document.getElementById('advisoriesTableBody');
    
    if (advisoriesData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No advisories found</td></tr>';
        return;
    }
    
    tbody.innerHTML = advisoriesData.map(advisory => `
        <tr>
            <td><strong>${advisory.id}</strong></td>
            <td>
                <strong>${advisory.title}</strong>
            </td>
            <td>
                <span class="message-preview" title="${advisory.message}">
                    ${advisory.message.substring(0, 50)}${advisory.message.length > 50 ? '...' : ''}
                </span>
            </td>
            <td>
                <small class="text-muted">${formatDate(advisory.created_at)}</small>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="selectAdvisory('${advisory.id}')">
                    <i class="fas fa-mouse-pointer"></i> Select
                </button>
            </td>
        </tr>
    `).join('');
}

// Populate farmer dropdown
function populateFarmerDropdown(farmersData) {
    const select = document.getElementById('phoneNumber');
    select.innerHTML = '<option value="">Select Farmer...</option>';
    
    farmersData.forEach(farmer => {
        const option = document.createElement('option');
        option.value = farmer.phone;
        option.textContent = `${farmer.phone} (ID: ${farmer.id})`;
        select.appendChild(option);
    });
}

// Populate advisory dropdown
function populateAdvisoryDropdown(advisoriesData) {
    const select = document.getElementById('messageId');
    select.innerHTML = '<option value="">Select Advisory...</option>';
    
    advisoriesData.forEach(advisory => {
        const option = document.createElement('option');
        option.value = advisory.id;
        option.textContent = `${advisory.id}: ${advisory.title}`;
        select.appendChild(option);
    });
}

// Select farmer from table
function selectFarmer(phone) {
    document.getElementById('phoneNumber').value = phone;
    updatePreview();
}

// Select advisory from table
function selectAdvisory(advisoryId) {
    document.getElementById('messageId').value = advisoryId;
    updatePreview();
}

// Update preview section
function updatePreview() {
    const messageId = document.getElementById('messageId').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    
    const previewSection = document.getElementById('previewSection');
    
    if (messageId && phoneNumber) {
        const advisory = advisories.find(a => a.id == messageId);
        const farmer = farmers.find(f => f.phone === phoneNumber);
        
        if (advisory && farmer) {
            document.getElementById('selectedAdvisoryTitle').textContent = advisory.title;
            document.getElementById('selectedFarmerPhone').textContent = farmer.phone;
            document.getElementById('selectedAdvisoryMessage').textContent = advisory.message.substring(0, 200) + '...';
            previewSection.style.display = 'block';
        }
    } else {
        previewSection.style.display = 'none';
    }
}

// Handle send advisory form submission
async function handleSendAdvisory(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        message_id: formData.get('message_id'),
        phone_number: formData.get('phone_number')
    };
    
    if (!data.message_id || !data.phone_number) {
        showAlert('Please select both an advisory and a farmer', 'danger');
        return;
    }
    
    try {
        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        const response = await fetch('/send-advisory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // Show results
        displayResults(result);
        
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        if (result.success) {
            showAlert('SMS sent successfully!', 'success');
            resetForm();
        } else {
            showAlert('Failed to send SMS: ' + result.error, 'danger');
        }
        
    } catch (error) {
        console.error('Error sending advisory:', error);
        showAlert('Error sending SMS: ' + error.message, 'danger');
        
        // Reset button
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Advisory SMS';
        submitBtn.disabled = false;
    }
}

// Display results
function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
    
    const statusClass = result.success ? 'success' : 'danger';
    const statusIcon = result.success ? 'check-circle' : 'times-circle';
    
    resultsContent.innerHTML = `
        <div class="alert alert-${statusClass}">
            <h6><i class="fas fa-${statusIcon}"></i> SMS Sending Result</h6>
            <p><strong>Status:</strong> ${result.success ? 'SUCCESS' : 'FAILED'}</p>
            ${result.message_id ? `<p><strong>Advisory ID:</strong> ${result.message_id}</p>` : ''}
            ${result.phone_number ? `<p><strong>Phone:</strong> ${result.phone_number}</p>` : ''}
            ${result.advisory_title ? `<p><strong>Advisory:</strong> ${result.advisory_title}</p>` : ''}
            ${result.verification_code ? `<p><strong>Verification Code:</strong> <code>${result.verification_code}</code></p>` : ''}
            ${result.sms_content ? `<p><strong>SMS Content:</strong> ${result.sms_content}</p>` : ''}
            ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
            ${result.step ? `<p><strong>Failed at:</strong> ${result.step}</p>` : ''}
        </div>
        
        ${result.sms_details ? `
            <div class="mt-3">
                <h6>SMS Provider Details:</h6>
                <pre class="bg-light p-2 rounded"><code>${JSON.stringify(result.sms_details, null, 2)}</code></pre>
            </div>
        ` : ''}
    `;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Reset form
function resetForm() {
    document.getElementById('sendAdvisoryForm').reset();
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
}

// Utility functions
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </td>
        </tr>
    `;
}

function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `
        <tr>
            <td colspan="5" class="text-center text-danger">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </td>
        </tr>
    `;
}

function showAlert(message, type) {
    // You can implement a toast notification here
    alert(message);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
}

// Auto-refresh every 30 seconds
setInterval(() => {
    updateLastUpdated();
}, 30000);