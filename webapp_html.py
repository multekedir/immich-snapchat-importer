"""
Improved HTML interface with enhanced progress tracking
"""

def get_improved_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Immich Snapchat Importer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab-button {
            flex: 1;
            padding: 15px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }
        
        .tab-button:hover {
            background: #e9ecef;
            color: #333;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f8f9ff;
        }
        
        .upload-area.dragging {
            border-color: #764ba2;
            background: #f0f0ff;
        }
        
        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #555;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            width: 100%;
        }
        
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        /* IMPROVED PROGRESS BAR STYLES */
        .progress-section {
            display: none;
            margin-top: 30px;
        }
        
        .progress-section.active {
            display: block;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .progress-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .progress-percentage {
            font-size: 18px;
            font-weight: 700;
            color: #667eea;
        }
        
        .progress-bar-container {
            background: #f0f0f0;
            border-radius: 12px;
            height: 40px;
            overflow: hidden;
            margin-bottom: 15px;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-bar::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.3),
                transparent
            );
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .progress-details {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .progress-detail-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .progress-detail-row:last-child {
            border-bottom: none;
        }
        
        .progress-detail-label {
            font-weight: 500;
            color: #666;
        }
        
        .progress-detail-value {
            font-weight: 600;
            color: #333;
        }
        
        .progress-current-item {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
            font-style: italic;
        }
        
        .status-message {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .status-message.info {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #1976d2;
        }
        
        .status-message.success {
            background: #e8f5e9;
            color: #388e3c;
            border-left: 4px solid #388e3c;
        }
        
        .status-message.error {
            background: #ffebee;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #dee2e6;
            transition: transform 0.2s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
        }
        
        .alert.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            margin-top: 10px;
        }
        
        .status-indicator.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-indicator.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-indicator.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .status-icon {
            font-size: 18px;
        }
        
        /* Spinner animation */
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 Immich Snapchat Importer</h1>
            <p>Import your Snapchat Memories to Immich with metadata preservation</p>
        </div>
        
        <!-- Tab Navigation -->
        <script>
        // Define switchTab immediately so it's available for onclick handlers
        function switchTab(tabName, buttonElement) {
            console.log('switchTab called with:', tabName, buttonElement);
            
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
                console.log('Activated tab:', tabName);
            } else {
                console.error('Tab content not found:', tabName + 'Tab');
            }
            
            // Activate the clicked button
            if (buttonElement) {
                buttonElement.classList.add('active');
            }
            
            // Load metadata files will be handled by the main script if available
            if (typeof loadMetadataFiles === 'function') {
                if (tabName === 'repair' || tabName === 'process') {
                    loadMetadataFiles();
                }
            }
        }
        window.switchTab = switchTab;
        </script>
        
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('import', this)">
                Import New
            </button>
            <button class="tab-button" onclick="switchTab('repair', this)">
                Repair Immich
            </button>
            <button class="tab-button" onclick="switchTab('process', this)">
                Process Only
            </button>
        </div>
        
        <!-- Tab Content: Import -->
        <div class="tab-content active" id="importTab">
            <div class="content">
                <!-- Upload Section -->
                <div class="section">
                    <div class="section-title">1. Upload Snapchat Export</div>
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📁</div>
                        <p style="margin-bottom: 8px;">
                            <strong>Drag & drop your file here</strong>
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            or click to browse (JSON or HTML)
                        </p>
                        <input type="file" id="fileInput" accept=".json,.html" style="display: none;">
                    </div>
                    <div id="uploadAlert" class="alert"></div>
                    <div id="uploadedFile" style="margin-top: 15px; display: none;">
                        <strong>Selected file:</strong> <span id="fileName"></span>
                    </div>
                </div>
                
                <!-- Configuration Section -->
                <div class="section">
                    <div class="section-title">2. Configure Immich Settings</div>
                    <div class="form-group">
                        <label for="immichUrl">Immich Server URL</label>
                        <input type="text" id="immichUrl" placeholder="http://localhost:2283/api">
                    </div>
                    <div class="form-group">
                        <label for="apiKey">Immich API Key</label>
                        <input type="password" id="apiKey" placeholder="Your API key from Immich settings">
                    </div>
                    <div class="form-group">
                        <label for="delay">Download Delay (seconds)</label>
                        <input type="number" id="delay" value="2.0" min="0.5" step="0.5">
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="skipUpload">
                        <label for="skipUpload" style="margin-bottom: 0;">Skip Immich upload (process only)</label>
                    </div>
                </div>
                
                <!-- Start Import Button -->
                <div class="section">
                    <button class="btn" id="startBtn" disabled>Upload a file to start</button>
                </div>
                
                <!-- IMPROVED PROGRESS SECTION -->
                <div class="progress-section" id="progressSection">
                    <div class="progress-header">
                        <span class="progress-title">Import Progress</span>
                        <span class="progress-percentage" id="progressPercentage">0%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="progressBar" style="width: 0%">
                            <span class="spinner" id="progressSpinner" style="display: none;"></span>
                        </div>
                    </div>
                    <div class="progress-current-item" id="progressCurrentItem"></div>
                    <div id="statusMessages"></div>
                    <div id="statsSection" style="display: none;">
                        <div class="section-title">Import Statistics</div>
                        <div class="stats-grid" id="statsGrid"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab Content: Repair Immich -->
        <div class="tab-content" id="repairTab">
            <div class="content">
                <div class="section">
                    <div class="section-title">Repair Metadata in Immich</div>
                    <p style="color: #666; margin-bottom: 20px;">
                        Fix GPS coordinates and dates for photos already uploaded to Immich
                    </p>
                    
                    <div class="form-group">
                        <label>Metadata JSON File</label>
                        <div style="margin-bottom: 10px;">
                            <div class="upload-area" id="repairUploadArea" style="padding: 20px; cursor: pointer;">
                                <div class="upload-icon">📁</div>
                                <p style="margin-bottom: 8px;">
                                    <strong>Drag & drop JSON metadata file here</strong>
                                </p>
                                <p style="color: #666; font-size: 14px;">
                                    or click to browse
                                </p>
                                <input type="file" id="repairFileInput" accept=".json" style="display: none;">
                            </div>
                        </div>
                        <p style="text-align: center; color: #666; margin: 10px 0;">OR</p>
                        <select id="repairMetadataFile">
                            <option value="">-- Select existing metadata file --</option>
                        </select>
                        <div id="repairMetadataStatus" style="margin-top: 10px; display: none;" class="status-indicator">
                            <span id="repairMetadataStatusIcon" class="status-icon"></span>
                            <span id="repairMetadataStatusText"></span>
                        </div>
                        <div id="repairUploadedFile" style="margin-top: 10px; display: none; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; color: #155724;">
                            <strong>✓ Metadata file uploaded:</strong> <span id="repairFileName"></span>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="repairImmichUrl">Immich Server URL</label>
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="repairImmichUrl" placeholder="http://localhost:2283/api" style="flex: 1;">
                            <button class="btn" id="testConnectionBtn" style="flex: 0 0 auto; width: auto; padding: 12px 20px;">
                                Test Connection
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="repairApiKey">Immich API Key</label>
                        <input type="password" id="repairApiKey" placeholder="Your API key">
                    </div>
                    
                    <div id="repairConnectionStatus" style="margin-bottom: 20px; display: none;" class="status-indicator">
                        <span id="repairConnectionStatusIcon" class="status-icon"></span>
                        <span id="repairConnectionStatusText"></span>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button class="btn" id="checkMetadataBtn" style="flex: 1;" disabled>
                            Check Metadata (Dry Run)
                        </button>
                        <button class="btn" id="applyFixesBtn" style="flex: 1;" disabled>
                            Apply Fixes
                        </button>
                    </div>
                </div>
                
                <!-- IMPROVED REPAIR PROGRESS -->
                <div class="progress-section" id="repairProgressSection">
                    <div class="progress-header">
                        <span class="progress-title">Repair Progress</span>
                        <span class="progress-percentage" id="repairProgressPercentage">0%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="repairProgressBar" style="width: 0%">
                            <span class="spinner" id="repairProgressSpinner" style="display: none;"></span>
                        </div>
                    </div>
                    <div class="progress-current-item" id="repairProgressCurrentItem"></div>
                    <div id="repairStatusMessages"></div>
                    <div id="repairStatsSection" style="display: none;">
                        <div class="stats-grid" id="repairStatsGrid"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab Content: Process Only -->
        <div class="tab-content" id="processTab">
            <div class="content">
                <div class="section">
                    <div class="section-title">Process Already Downloaded Files</div>
                    <p style="color: #666; margin-bottom: 20px;">
                        Process files that are already downloaded (skips download phase)
                    </p>
                    
                    <div class="form-group">
                        <label for="processMetadataFile">Metadata JSON File</label>
                        <select id="processMetadataFile">
                            <option value="">-- Select metadata file --</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="processImmichUrl">Immich Server URL (optional)</label>
                        <input type="text" id="processImmichUrl" placeholder="http://localhost:2283/api">
                    </div>
                    
                    <div class="form-group">
                        <label for="processApiKey">Immich API Key (optional)</label>
                        <input type="password" id="processApiKey" placeholder="Leave empty to skip upload">
                    </div>
                    
                    <button class="btn" id="processStartBtn">
                        Start Processing
                    </button>
                </div>
                
                <!-- IMPROVED PROCESS PROGRESS -->
                <div class="progress-section" id="processProgressSection">
                    <div class="progress-header">
                        <span class="progress-title">Processing Progress</span>
                        <span class="progress-percentage" id="processProgressPercentage">0%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="processProgressBar" style="width: 0%">
                            <span class="spinner" id="processProgressSpinner" style="display: none;"></span>
                        </div>
                    </div>
                    <div class="progress-current-item" id="processProgressCurrentItem"></div>
                    <div id="processStatusMessages"></div>
                    <div id="processStatsSection" style="display: none;">
                        <div class="stats-grid" id="processStatsGrid"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    /**
     * Immich Snapchat Importer - Enhanced JavaScript (INLINE VERSION)
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
                progressCurrentItem.textContent = `Checking: ${details.filename}`;
                progressCurrentItem.style.display = 'block';
            } else if (details.index && details.total) {
                progressCurrentItem.textContent = `Checking ${details.index} of ${details.total} memories`;
                progressCurrentItem.style.display = 'block';
            } else {
                progressCurrentItem.textContent = message || '';
            }
        } else if (progressCurrentItem && message) {
            progressCurrentItem.textContent = message;
        }
        
        if (message) {
            addRepairStatusMessage('info', message);
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

    function addRepairStatusMessage(type, message) {
        const messagesDiv = document.getElementById('repairStatusMessages');
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
            addStatCard('repairStatsGrid', 'Checked', stats.checked);
            addStatCard('repairStatsGrid', 'Needs Repair', stats.needs_repair);
            if (!stats.dry_run) {
                addStatCard('repairStatsGrid', 'Repaired', stats.repaired);
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
        const valueDiv = document.createElement('div');
        valueDiv.className = 'stat-value';
        valueDiv.textContent = value;
        const labelDiv = document.createElement('div');
        labelDiv.className = 'stat-label';
        labelDiv.textContent = label;
        card.appendChild(valueDiv);
        card.appendChild(labelDiv);
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

    // Initialize all handlers on page load
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Page loaded, initializing...');
        // Tab switching uses onclick handlers, so no need for initTabHandlers
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
    </script>
</body>
</html>
    """