/**
 * Immich Snapchat Importer - Enhanced JavaScript
 * Improved progress tracking and WebSocket handling
 */

let uploadedFilename = null;
let ws = null;
let currentJobId = null;
let currentRepairJobId = null;
let currentProcessJobId = null;
let repairMetadataFilename = null;
let repairConnectionStatus = false;
let repairMetadataReady = false;

// Tab switching
function switchTab(tabName, buttonElement) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabContent = document.getElementById(tabName + 'Tab');
    if (tabContent) {
        tabContent.classList.add('active');
    }
    
    // Activate the clicked button
    if (buttonElement) {
        buttonElement.classList.add('active');
    }
    
    // Load metadata files for repair and process tabs
    if (tabName === 'repair' || tabName === 'process') {
        loadMetadataFiles();
    }
}

// Load available metadata files
async function loadMetadataFiles() {
    try {
        const response = await fetch('/api/metadata/list');
        const data = await response.json();
        
        const repairSelect = document.getElementById('repairMetadataFile');
        const processSelect = document.getElementById('processMetadataFile');
        
        // Clear existing options (except first)
        repairSelect.innerHTML = '<option value="">-- Select existing metadata file --</option>';
        processSelect.innerHTML = '<option value="">-- Select metadata file --</option>';
        
        data.files.forEach(file => {
            const option1 = document.createElement('option');
            option1.value = file.filename;
            option1.textContent = `${file.filename} (${(file.size / 1024).toFixed(1)} KB)`;
            repairSelect.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = file.filename;
            option2.textContent = `${file.filename} (${(file.size / 1024).toFixed(1)} KB)`;
            processSelect.appendChild(option2);
        });
    } catch (error) {
        console.error('Failed to load metadata files:', error);
    }
}

// Initialize WebSocket
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed, reconnecting...');
        setTimeout(initWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    // Send heartbeat
    setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
        }
    }, 30000);
}

function handleWebSocketMessage(data) {
    // Determine job type from job_id prefix
    const jobType = data.job_id.split('_')[0]; // 'import', 'repair', or 'process'
    
    // Check if this message is for our current job
    let isOurJob = false;
    if (jobType === 'import' && data.job_id === currentJobId) {
        isOurJob = true;
    } else if (jobType === 'repair' && data.job_id === currentRepairJobId) {
        isOurJob = true;
    } else if (jobType === 'process' && data.job_id === currentProcessJobId) {
        isOurJob = true;
    }
    
    if (!isOurJob) return;
    
    if (data.type === 'progress') {
        if (jobType === 'repair') {
            updateRepairProgress(data.progress, data.message, data.details || null);
        } else if (jobType === 'process') {
            updateProcessProgress(data.progress, data.message, data.details || null);
        } else {
            updateProgress(data.progress, data.message, data.details || null);
        }
    } else if (data.type === 'complete') {
        if (jobType === 'repair') {
            updateRepairProgress(100, data.message, data.stats || null);
            if (data.stats) {
                displayRepairStats(data.stats);
            }
            document.getElementById('checkMetadataBtn').disabled = false;
            document.getElementById('applyFixesBtn').disabled = false;
        } else if (jobType === 'process') {
            updateProcessProgress(100, data.message, data.stats || null);
            if (data.stats) {
                displayProcessStats(data.stats);
            }
        } else {
            updateProgress(100, data.message, data.stats || null);
            if (data.stats) {
                displayStats(data.stats);
            }
            document.getElementById('startBtn').disabled = false;
        }
    } else if (data.type === 'error') {
        if (jobType === 'repair') {
            addRepairStatusMessage('error', data.message);
            hideSpinner('repairProgressSpinner');
            document.getElementById('checkMetadataBtn').disabled = false;
            document.getElementById('applyFixesBtn').disabled = false;
        } else if (jobType === 'process') {
            addProcessStatusMessage('error', data.message);
            hideSpinner('processProgressSpinner');
        } else {
            addStatusMessage('error', data.message);
            hideSpinner('progressSpinner');
            document.getElementById('startBtn').disabled = false;
        }
    }
}

// IMPROVED PROGRESS FUNCTIONS
function updateProgress(percent, message, details) {
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressCurrentItem = document.getElementById('progressCurrentItem');
    const progressSpinner = document.getElementById('progressSpinner');
    
    if (progressBar) {
        progressBar.style.width = `${percent}%`;
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${percent}%`;
    }
    
    // Show/hide spinner
    if (progressSpinner) {
        if (percent > 0 && percent < 100) {
            progressSpinner.style.display = 'inline-block';
        } else {
            progressSpinner.style.display = 'none';
        }
    }
    
    // Update current item display
    if (progressCurrentItem && details) {
        if (details.filename) {
            progressCurrentItem.textContent = `Processing: ${details.filename}`;
            progressCurrentItem.style.display = 'block';
        } else if (details.index && details.total) {
            progressCurrentItem.textContent = `Item ${details.index} of ${details.total}`;
            progressCurrentItem.style.display = 'block';
        } else {
            progressCurrentItem.textContent = message || '';
        }
    } else if (progressCurrentItem && message) {
        progressCurrentItem.textContent = message;
    }
    
    if (message) {
        addStatusMessage('info', message);
    }
}

function updateRepairProgress(percent, message, details) {
    const progressBar = document.getElementById('repairProgressBar');
    const progressPercentage = document.getElementById('repairProgressPercentage');
    const progressCurrentItem = document.getElementById('repairProgressCurrentItem');
    const progressSpinner = document.getElementById('repairProgressSpinner');
    
    if (progressBar) {
        progressBar.style.width = `${percent}%`;
    }
    
    if (progressPercentage) {
        if (details && typeof details === 'object' && details.total) {
            const index = details.index || 0;
            const total = details.total || 0;
            progressPercentage.textContent = `${percent}% (${index}/${total})`;
        } else {
            progressPercentage.textContent = `${percent}%`;
        }
    }
    
    // Show/hide spinner
    if (progressSpinner) {
        if (percent > 0 && percent < 100) {
            progressSpinner.style.display = 'inline-block';
        } else {
            progressSpinner.style.display = 'none';
        }
    }
    
    // Update current item display
    if (progressCurrentItem && details) {
        if (details.filename) {
            progressCurrentItem.textContent = `Checking: ${details.filename}`;
            progressCurrentItem.style.display = 'block';
        } else if (details.index && details.total) {
            progressCurrentItem.textContent = `Checking ${details.index} of ${details.total} memories`;
            progressCurrentItem.style.display = 'block';
        } else if (typeof details === 'object') {
            const index = details.index || 0;
            const total = details.total || 0;
            const found = details.found_in_immich || 0;
            const notFound = details.not_found || 0;
            const needsFix = details.needs_fix || 0;
            const repaired = details.repaired || 0;
            
            let detailText = '';
            if (total > 0) {
                detailText = `Processing: ${index}/${total} memories`;
                if (found > 0 || notFound > 0) {
                    detailText += ` | Found: ${found}`;
                    if (notFound > 0) detailText += ` | Not found: ${notFound}`;
                }
                if (needsFix > 0) detailText += ` | Needs repair: ${needsFix}`;
                if (repaired > 0) detailText += ` | Repaired: ${repaired}`;
            }
            progressCurrentItem.textContent = detailText || message || '';
            progressCurrentItem.style.display = detailText ? 'block' : 'none';
        } else {
            progressCurrentItem.textContent = message || '';
        }
    } else if (progressCurrentItem && message) {
        progressCurrentItem.textContent = message;
    }
    
    if (message) {
        addRepairStatusMessage('info', message, details);
    }
}

function updateProcessProgress(percent, message, details) {
    const progressBar = document.getElementById('processProgressBar');
    const progressPercentage = document.getElementById('processProgressPercentage');
    const progressCurrentItem = document.getElementById('processProgressCurrentItem');
    const progressSpinner = document.getElementById('processProgressSpinner');
    
    if (progressBar) {
        progressBar.style.width = `${percent}%`;
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${percent}%`;
    }
    
    // Show/hide spinner
    if (progressSpinner) {
        if (percent > 0 && percent < 100) {
            progressSpinner.style.display = 'inline-block';
        } else {
            progressSpinner.style.display = 'none';
        }
    }
    
    // Update current item display
    if (progressCurrentItem && details) {
        if (details.filename) {
            progressCurrentItem.textContent = `Processing: ${details.filename}`;
            progressCurrentItem.style.display = 'block';
        } else {
            progressCurrentItem.textContent = message || '';
        }
    } else if (progressCurrentItem && message) {
        progressCurrentItem.textContent = message;
    }
    
    if (message) {
        addProcessStatusMessage('info', message);
    }
}

function hideSpinner(spinnerId) {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function addStatusMessage(type, message) {
    const messagesDiv = document.getElementById('statusMessages');
    if (!messagesDiv) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.textContent = message;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Keep only last 10 messages
    while (messagesDiv.children.length > 10) {
        messagesDiv.removeChild(messagesDiv.firstChild);
    }
}

function addRepairStatusMessage(type, message, details) {
    const messagesDiv = document.getElementById('repairStatusMessages');
    if (!messagesDiv) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    
    let fullMessage = message;
    
    // Add details if provided
    if (details && typeof details === 'object') {
        if (details.filename) {
            fullMessage += ` - File: ${details.filename}`;
        }
        if (details.date_issue && details.expected_date && details.asset_date) {
            fullMessage += ` | Date: Expected ${details.expected_date}, Found ${details.asset_date}`;
        }
        if (details.gps_issue && details.expected_gps && details.asset_gps) {
            fullMessage += ` | GPS: Expected [${details.expected_gps.lat}, ${details.expected_gps.lon}], Found [${details.asset_gps.lat}, ${details.asset_gps.lon}]`;
        }
    }
    
    messageDiv.textContent = fullMessage;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Keep only last 10 messages
    while (messagesDiv.children.length > 10) {
        messagesDiv.removeChild(messagesDiv.firstChild);
    }
}

function addProcessStatusMessage(type, message) {
    const messagesDiv = document.getElementById('processStatusMessages');
    if (!messagesDiv) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.textContent = message;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Keep only last 10 messages
    while (messagesDiv.children.length > 10) {
        messagesDiv.removeChild(messagesDiv.firstChild);
    }
}

function displayStats(stats) {
    const statsSection = document.getElementById('statsSection');
    const statsGrid = document.getElementById('statsGrid');
    
    if (!statsGrid) return;
    
    statsGrid.innerHTML = '';
    
    if (stats.summary) {
        addStatCard('statsGrid', 'Total Files', stats.summary.total_files);
        addStatCard('statsGrid', 'With GPS', stats.summary.with_gps);
        addStatCard('statsGrid', 'GPS Coverage', `${stats.summary.gps_coverage_percent}%`);
    }
    
    if (stats.file_sizes) {
        addStatCard('statsGrid', 'Total Size', `${stats.file_sizes.total_mb} MB`);
    }
    
    if (statsSection) {
        statsSection.style.display = 'block';
    }
}

function displayRepairStats(stats) {
    const statsSection = document.getElementById('repairStatsSection');
    const statsGrid = document.getElementById('repairStatsGrid');
    
    if (!statsGrid) return;
    
    statsGrid.innerHTML = '';
    
    if (stats) {
        addStatCard('repairStatsGrid', 'Checked', stats.checked || 0);
        addStatCard('repairStatsGrid', 'Needs Repair', stats.needs_repair || 0);
        if (!stats.dry_run && stats.repaired !== undefined) {
            addStatCard('repairStatsGrid', 'Repaired', stats.repaired || 0);
        }
    }
    
    if (statsSection) {
        statsSection.style.display = 'block';
    }
}

function displayProcessStats(stats) {
    const statsSection = document.getElementById('processStatsSection');
    const statsGrid = document.getElementById('processStatsGrid');
    
    if (!statsGrid) return;
    
    statsGrid.innerHTML = '';
    
    if (stats.summary) {
        addStatCard('processStatsGrid', 'Total Files', stats.summary.total_files);
        addStatCard('processStatsGrid', 'With GPS', stats.summary.with_gps);
        addStatCard('processStatsGrid', 'GPS Coverage', `${stats.summary.gps_coverage_percent}%`);
    }
    
    if (stats.file_sizes) {
        addStatCard('processStatsGrid', 'Total Size', `${stats.file_sizes.total_mb} MB`);
    }
    
    if (statsSection) {
        statsSection.style.display = 'block';
    }
}

function addStatCard(gridId, label, value) {
    const statsGrid = document.getElementById(gridId);
    if (!statsGrid) return;
    
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.innerHTML = `
        <div class="stat-value">${value}</div>
        <div class="stat-label">${label}</div>
    `;
    statsGrid.appendChild(card);
}

// File upload handling
function initUploadHandlers() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!uploadArea || !fileInput) return;
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    });
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFileSelect(file);
    });
}

async function handleFileSelect(file) {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        uploadedFilename = data.filename;
        
        document.getElementById('fileName').textContent = data.filename;
        document.getElementById('uploadedFile').style.display = 'block';
        document.getElementById('startBtn').textContent = 'Start Import';
        document.getElementById('startBtn').disabled = false;
        
        showAlert('uploadAlert', 'success', `File uploaded successfully: ${data.filename}`);
    } catch (error) {
        showAlert('uploadAlert', 'error', `Upload failed: ${error.message}`);
    }
}

function showAlert(elementId, type, message) {
    const alert = document.getElementById(elementId);
    if (!alert) return;
    
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Start import
function initImportButton() {
    const startBtn = document.getElementById('startBtn');
    if (!startBtn) return;
    
    startBtn.addEventListener('click', async () => {
        if (!uploadedFilename) return;
        
        const config = {
            immich_url: document.getElementById('immichUrl').value,
            api_key: document.getElementById('apiKey').value,
            delay: parseFloat(document.getElementById('delay').value),
            skip_upload: document.getElementById('skipUpload').checked
        };
        
        try {
            startBtn.disabled = true;
            document.getElementById('progressSection').classList.add('active');
            document.getElementById('statusMessages').innerHTML = '';
            document.getElementById('statsSection').style.display = 'none';
            updateProgress(0, 'Starting import...', null);
            
            const response = await fetch('/api/import/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: uploadedFilename,
                    config: config
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to start import');
            }
            
            const data = await response.json();
            currentJobId = data.job_id;
            addStatusMessage('info', `Import job started: ${data.job_id}`);
            
        } catch (error) {
            addStatusMessage('error', `Failed to start import: ${error.message}`);
            startBtn.disabled = false;
            hideSpinner('progressSpinner');
        }
    });
}

// Repair handlers
function initRepairHandlers() {
    const checkBtn = document.getElementById('checkMetadataBtn');
    const applyBtn = document.getElementById('applyFixesBtn');
    
    if (checkBtn) {
        checkBtn.addEventListener('click', () => startRepair(true));
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', () => startRepair(false));
    }
}

async function startRepair(dryRun) {
    const metadataFile = repairMetadataFilename || document.getElementById('repairMetadataFile')?.value;
    const immichUrl = document.getElementById('repairImmichUrl').value;
    const apiKey = document.getElementById('repairApiKey').value;
    
    if (!metadataFile) {
        alert('Please select or upload a metadata file');
        return;
    }
    
    if (!immichUrl || !apiKey) {
        alert('Please enter Immich URL and API key');
        return;
    }
    
    try {
        document.getElementById('repairProgressSection').classList.add('active');
        document.getElementById('repairStatusMessages').innerHTML = '';
        document.getElementById('repairStatsSection').style.display = 'none';
        updateRepairProgress(0, dryRun ? 'Starting dry run...' : 'Starting repair...', null);
        
        const response = await fetch('/api/repair/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                metadata_file: metadataFile,
                immich_url: immichUrl,
                api_key: apiKey,
                dry_run: dryRun
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start repair');
        }
        
        const data = await response.json();
        currentRepairJobId = data.job_id;
        addRepairStatusMessage('info', `Repair job started: ${data.job_id}`);
    } catch (error) {
        addRepairStatusMessage('error', `Failed to start repair: ${error.message}`);
        hideSpinner('repairProgressSpinner');
    }
}

// Process Only handler
function initProcessHandlers() {
    const processBtn = document.getElementById('processStartBtn');
    if (!processBtn) return;
    
    processBtn.addEventListener('click', async () => {
        const metadataFile = document.getElementById('processMetadataFile').value;
        const immichUrl = document.getElementById('processImmichUrl').value;
        const apiKey = document.getElementById('processApiKey').value;
        
        if (!metadataFile) {
            alert('Please select a metadata file');
            return;
        }
        
        try {
            document.getElementById('processProgressSection').classList.add('active');
            document.getElementById('processStatusMessages').innerHTML = '';
            document.getElementById('processStatsSection').style.display = 'none';
            updateProcessProgress(0, 'Starting processing...', null);
            
            const response = await fetch('/api/process/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    metadata_file: metadataFile,
                    immich_url: immichUrl || null,
                    api_key: apiKey || null
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to start processing');
            }
            
            const data = await response.json();
            currentProcessJobId = data.job_id;
            addProcessStatusMessage('info', `Processing job started: ${data.job_id}`);
        } catch (error) {
            addProcessStatusMessage('error', `Failed to start processing: ${error.message}`);
            hideSpinner('processProgressSpinner');
        }
    });
}

// Repair file upload handlers
function initRepairUploadHandlers() {
    const repairUploadArea = document.getElementById('repairUploadArea');
    const repairFileInput = document.getElementById('repairFileInput');
    
    if (!repairUploadArea || !repairFileInput) return;
    
    repairUploadArea.addEventListener('click', () => repairFileInput.click());
    
    repairUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        repairUploadArea.classList.add('dragging');
    });
    
    repairUploadArea.addEventListener('dragleave', () => {
        repairUploadArea.classList.remove('dragging');
    });
    
    repairUploadArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        repairUploadArea.classList.remove('dragging');
        const file = e.dataTransfer.files[0];
        if (file) await handleRepairMetadataUpload(file);
    });
    
    repairFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) await handleRepairMetadataUpload(file);
    });
}

async function handleRepairMetadataUpload(file) {
    if (!file.name.endsWith('.json')) {
        showRepairMetadataStatus('error', '❌ Please upload a JSON file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showRepairMetadataStatus('info', '⏳ Uploading metadata file...');
        
        const response = await fetch('/api/upload/metadata', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({detail: 'Upload failed'}));
            throw new Error(errorData.detail || 'Upload failed');
        }
        
        const data = await response.json();
        repairMetadataFilename = data.filename;
        
        const fileNameEl = document.getElementById('repairFileName');
        const uploadedFileEl = document.getElementById('repairUploadedFile');
        const metadataSelect = document.getElementById('repairMetadataFile');
        
        if (fileNameEl) fileNameEl.textContent = data.filename;
        if (uploadedFileEl) uploadedFileEl.style.display = 'block';
        if (metadataSelect) metadataSelect.value = '';
        
        showRepairMetadataStatus('success', `✓ Metadata file uploaded: ${data.filename}`);
        checkRepairReady();
    } catch (error) {
        showRepairMetadataStatus('error', `❌ Upload failed: ${error.message}`);
    }
}

function showRepairMetadataStatus(type, message) {
    const statusDiv = document.getElementById('repairMetadataStatus');
    if (!statusDiv) return;
    
    const iconSpan = document.getElementById('repairMetadataStatusIcon');
    const textSpan = document.getElementById('repairMetadataStatusText');
    
    statusDiv.style.display = 'flex';
    statusDiv.className = `status-indicator ${type}`;
    
    if (iconSpan) {
        iconSpan.textContent = type === 'success' ? '✓' : type === 'error' ? '❌' : '⏳';
    }
    if (textSpan) {
        textSpan.textContent = message;
    }
}

function showRepairConnectionStatus(type, message) {
    const statusDiv = document.getElementById('repairConnectionStatus');
    if (!statusDiv) return;
    
    const iconSpan = document.getElementById('repairConnectionStatusIcon');
    const textSpan = document.getElementById('repairConnectionStatusText');
    
    statusDiv.style.display = 'flex';
    statusDiv.className = `status-indicator ${type}`;
    
    if (iconSpan) {
        iconSpan.textContent = type === 'success' ? '✓' : type === 'error' ? '❌' : '⏳';
    }
    if (textSpan) {
        textSpan.textContent = message;
    }
}

function checkRepairReady() {
    const metadataFile = repairMetadataFilename || document.getElementById('repairMetadataFile')?.value;
    const hasMetadata = !!metadataFile;
    repairMetadataReady = hasMetadata;
    
    const isReady = repairConnectionStatus && repairMetadataReady;
    
    const checkBtn = document.getElementById('checkMetadataBtn');
    const applyBtn = document.getElementById('applyFixesBtn');
    
    if (checkBtn) checkBtn.disabled = !isReady;
    if (applyBtn) applyBtn.disabled = !isReady;
}

// Test connection
function initTestConnectionHandler() {
    const testBtn = document.getElementById('testConnectionBtn');
    if (!testBtn) return;
    
    testBtn.addEventListener('click', async () => {
        const immichUrl = document.getElementById('repairImmichUrl').value;
        const apiKey = document.getElementById('repairApiKey').value;
        
        if (!immichUrl || !apiKey) {
            showRepairConnectionStatus('error', '❌ Please enter Immich URL and API key');
            repairConnectionStatus = false;
            checkRepairReady();
            return;
        }
        
        try {
            showRepairConnectionStatus('info', '⏳ Testing connection...');
            testBtn.disabled = true;
            
            const response = await fetch('/api/repair/test-connection', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    immich_url: immichUrl,
                    api_key: apiKey
                })
            });
            
            const data = await response.json();
            
            if (data.connected) {
                showRepairConnectionStatus('success', `✓ Connected to Immich as ${data.user || 'user'}`);
                repairConnectionStatus = true;
            } else {
                showRepairConnectionStatus('error', `❌ ${data.message || 'Connection failed'}`);
                repairConnectionStatus = false;
            }
            
            checkRepairReady();
        } catch (error) {
            showRepairConnectionStatus('error', `❌ Connection test failed: ${error.message}`);
            repairConnectionStatus = false;
            checkRepairReady();
        } finally {
            testBtn.disabled = false;
        }
    });
}

// Monitor metadata select changes
function initMetadataSelectHandler() {
    const repairMetadataSelect = document.getElementById('repairMetadataFile');
    if (!repairMetadataSelect) return;
    
    repairMetadataSelect.addEventListener('change', function() {
        if (this.value) {
            repairMetadataFilename = null;
            const uploadedFileEl = document.getElementById('repairUploadedFile');
            if (uploadedFileEl) uploadedFileEl.style.display = 'none';
            showRepairMetadataStatus('success', `✓ Selected: ${this.value}`);
            checkRepairReady();
        } else {
            const statusDiv = document.getElementById('repairMetadataStatus');
            if (statusDiv) statusDiv.style.display = 'none';
            checkRepairReady();
        }
    });
}

// Load config
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        if (config.immich && config.immich.url) {
            const url = config.immich.url;
            const immichUrlInput = document.getElementById('immichUrl');
            const repairImmichUrlInput = document.getElementById('repairImmichUrl');
            const processImmichUrlInput = document.getElementById('processImmichUrl');
            
            if (immichUrlInput) immichUrlInput.value = url;
            if (repairImmichUrlInput) repairImmichUrlInput.value = url;
            if (processImmichUrlInput) processImmichUrlInput.value = url;
        }
        
        if (config.download && config.download.delay) {
            const delayInput = document.getElementById('delay');
            if (delayInput) delayInput.value = config.download.delay;
        }
    } catch (error) {
        console.error('Failed to load config:', error);
    }
}

// Initialize tab button handlers
function initTabHandlers() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            if (tabName) {
                switchTab(tabName, this);
            }
        });
    });
}

// Initialize all handlers on page load
document.addEventListener('DOMContentLoaded', function() {
    initTabHandlers();
    initUploadHandlers();
    initImportButton();
    initRepairHandlers();
    initProcessHandlers();
    initRepairUploadHandlers();
    initTestConnectionHandler();
    initMetadataSelectHandler();
    initWebSocket();
    loadConfig();
});