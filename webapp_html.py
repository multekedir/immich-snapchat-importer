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
        <div class="tabs">
            <button class="tab-button active" data-tab="import">
                Import New
            </button>
            <button class="tab-button" data-tab="repair">
                Repair Immich
            </button>
            <button class="tab-button" data-tab="process">
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
    
    <script src="/static/app.js"></script>
</body>
</html>
"""