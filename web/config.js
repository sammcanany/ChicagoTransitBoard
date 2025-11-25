// Chicago Transit Board - Config Portal
// Loaded from jsDelivr CDN: https://cdn.jsdelivr.net/gh/sammcanany/ChicagoTransitBoard@main/web/config.js

(function() {
    'use strict';

    let config = {};
    let status = {};
    let currentPage = 'main-page';
    let pageStack = [];

    // Station/Line data
    const METRA_LINES = [
        {id: 'UP-N', name: 'Union Pacific North'},
        {id: 'UP-NW', name: 'Union Pacific Northwest'},
        {id: 'UP-W', name: 'Union Pacific West'},
        {id: 'MD-N', name: 'Milwaukee District North'},
        {id: 'MD-W', name: 'Milwaukee District West'},
        {id: 'NCS', name: 'North Central Service'},
        {id: 'BNSF', name: 'BNSF Railway'},
        {id: 'HC', name: 'Heritage Corridor'},
        {id: 'ME', name: 'Metra Electric'},
        {id: 'RI', name: 'Rock Island'},
        {id: 'SWS', name: 'SouthWest Service'}
    ];

    const CTA_LINES = [
        {id: 'Red', name: 'Red Line'},
        {id: 'Blue', name: 'Blue Line'},
        {id: 'Brown', name: 'Brown Line'},
        {id: 'Green', name: 'Green Line'},
        {id: 'Orange', name: 'Orange Line'},
        {id: 'Pink', name: 'Pink Line'},
        {id: 'Purple', name: 'Purple Line'},
        {id: 'Yellow', name: 'Yellow Line'}
    ];

    const METRA_STATIONS = [
        {id: 'RAVENSWOOD', name: 'Ravenswood', lines: 'UP-N'},
        {id: 'CLYBOURN', name: 'Clybourn', lines: 'UP-N, UP-NW, UP-W'},
        {id: 'OTC', name: 'Ogilvie Transportation Center', lines: 'UP-N, UP-NW, UP-W'},
        {id: 'CUS', name: 'Chicago Union Station', lines: 'BNSF, HC, MD-N, MD-W, NCS, SWS'},
        {id: 'MILLENNIUM', name: 'Millennium Station', lines: 'ME'},
        {id: 'LAKEFOREST', name: 'Lake Forest', lines: 'UP-N'},
        {id: 'EVANSTON', name: 'Evanston (Davis St)', lines: 'UP-N'},
        {id: 'WILMETTE', name: 'Wilmette', lines: 'UP-N'},
        {id: 'GLENCOE', name: 'Glencoe', lines: 'UP-N'},
        {id: 'WINNETKA', name: 'Winnetka', lines: 'UP-N'},
        {id: 'ARLINGTON', name: 'Arlington Heights', lines: 'UP-NW'},
        {id: 'PALATINE', name: 'Palatine', lines: 'UP-NW'},
        {id: 'BARRINGTON', name: 'Barrington', lines: 'UP-NW'},
        {id: 'CRYSTAL', name: 'Crystal Lake', lines: 'UP-NW'},
        {id: 'ELMHURST', name: 'Elmhurst', lines: 'UP-W'},
        {id: 'DOWNERS', name: 'Downers Grove', lines: 'BNSF'},
        {id: 'NAPERVILLE', name: 'Naperville', lines: 'BNSF'},
        {id: 'AURORA', name: 'Aurora', lines: 'BNSF'},
        {id: 'JOLIET', name: 'Joliet', lines: 'HC, RI'},
        {id: 'GLENVIEW', name: 'Glenview', lines: 'MD-N'},
        {id: 'LIBERTYVILLE', name: 'Libertyville', lines: 'MD-N'}
    ];

    const CTA_STATIONS = [
        {id: '40900', name: 'Howard', lines: 'Red, Purple, Yellow'},
        {id: '41450', name: '95th/Dan Ryan', lines: 'Red'},
        {id: '40730', name: "O'Hare", lines: 'Blue'},
        {id: '40890', name: 'Forest Park', lines: 'Blue'},
        {id: '30249', name: 'Kimball', lines: 'Brown'},
        {id: '41290', name: 'Harlem/Lake', lines: 'Green'},
        {id: '40130', name: '63rd/Ashland', lines: 'Green'},
        {id: '40960', name: 'Midway', lines: 'Orange'},
        {id: '40580', name: '54th/Cermak', lines: 'Pink'},
        {id: '40090', name: 'Linden', lines: 'Purple'},
        {id: '40140', name: 'Dempster-Skokie', lines: 'Yellow'}
    ];

    function buildLineOptions(selectedId, type) {
        const lines = type === 'cta' ? CTA_LINES : METRA_LINES;
        return lines.map(l => 
            `<option value="${l.id}|${l.name}" ${selectedId === l.id ? 'selected' : ''}>${l.name} (${l.id})</option>`
        ).join('');
    }

    function buildStationOptions(selectedId, type) {
        const stations = type === 'cta' ? CTA_STATIONS : METRA_STATIONS;
        return stations.map(s => 
            `<option value="${s.id}|${s.name}" ${selectedId === s.id ? 'selected' : ''}>${s.name} (${s.lines})</option>`
        ).join('');
    }

    document.addEventListener('DOMContentLoaded', init);

    // Fetch with retry logic
    async function fetchWithRetry(url, retries = 3, delay = 500) {
        for (let i = 0; i < retries; i++) {
            try {
                const res = await fetch(url);
                if (res.ok) return res;
            } catch (e) {
                if (i === retries - 1) throw e;
            }
            await new Promise(r => setTimeout(r, delay));
        }
        throw new Error('Failed after retries');
    }

    async function init() {
        try {
            document.getElementById('app').innerHTML = '<div class="loading">Loading configuration...</div>';
            
            // Fetch sequentially (board can't handle parallel requests well)
            const configRes = await fetchWithRetry('/api/config');
            config = await configRes.json();
            
            // Small delay between requests
            await new Promise(r => setTimeout(r, 100));
            
            const statusRes = await fetchWithRetry('/api/status');
            status = await statusRes.json();
            
            render();
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (error) {
            document.getElementById('app').innerHTML = `
                <div class="error">
                    <h2>Connection Error</h2>
                    <p>Could not connect to board</p>
                    <p>${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>`;
        }
    }

    function render() {
        const c = config;
        const s = status;
        const rotationMode = c.rotation_mode || 'direction';
        const transitType = c.transit_type || 'metra';
        const secondaryTransitType = c.secondary_transit_type || 'metra';
        
        document.getElementById('app').innerHTML = `
            <div id="main-page" class="page">
                <div class="header">
                    <div class="header-title">Settings</div>
                </div>
                <div class="status-card">
                    <div class="status-grid">
                        <div class="status-item"><div class="status-label">Status</div><div class="status-value ${s.wifi_connected?'online':''}">${s.wifi_connected?'Online':'Offline'}</div></div>
                        <div class="status-item"><div class="status-label">Version</div><div class="status-value">${s.version||'?'}</div></div>
                        <div class="status-item"><div class="status-label">Uptime</div><div class="status-value">${s.uptime||'0m'}</div></div>
                        <div class="status-item"><div class="status-label">Memory</div><div class="status-value">${s.memory_pct||0}%</div></div>
                    </div>
                </div>
                <div class="menu-list">
                    <div class="menu-item" onclick="TC.nav('wifi')">
                        <div class="menu-icon" style="background:#e3f2fd;color:#1976d2;"><i data-lucide="wifi"></i></div>
                        <div class="menu-content"><div class="menu-title">WiFi</div><div class="menu-subtitle">${c.wifi_ssid||'Not set'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('api')">
                        <div class="menu-icon" style="background:#fff3e0;color:#f57c00;"><i data-lucide="key"></i></div>
                        <div class="menu-content"><div class="menu-title">API Keys</div><div class="menu-subtitle">Metra & CTA</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('transit')">
                        <div class="menu-icon" style="background:#e8f5e9;color:#388e3c;"><i data-lucide="train-front"></i></div>
                        <div class="menu-content"><div class="menu-title">Transit</div><div class="menu-subtitle">${c.line_name||'Not set'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('display')">
                        <div class="menu-icon" style="background:#f3e5f5;color:#7b1fa2;"><i data-lucide="monitor"></i></div>
                        <div class="menu-content"><div class="menu-title">Display</div><div class="menu-subtitle">Brightness & timing</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('features')">
                        <div class="menu-icon" style="background:#fce4ec;color:#c2185b;"><i data-lucide="settings"></i></div>
                        <div class="menu-content"><div class="menu-title">Features</div><div class="menu-subtitle">Alerts & updates</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('weather')">
                        <div class="menu-icon" style="background:#e0f7fa;color:#0097a7;"><i data-lucide="cloud-sun"></i></div>
                        <div class="menu-content"><div class="menu-title">Weather</div><div class="menu-subtitle">${c.enable_weather?'Enabled':'Disabled'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('system')">
                        <div class="menu-icon" style="background:#fff9c4;color:#f57f17;"><i data-lucide="cpu"></i></div>
                        <div class="menu-content"><div class="menu-title">System</div><div class="menu-subtitle">LED, sleep & power</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="location.reload()">Refresh</button>
                    <button class="btn btn-primary" onclick="TC.save()">Save All</button>
                </div>
            </div>

            <div id="wifi" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">WiFi</div></div>
                <div class="form-section">
                    <div class="form-group"><label>Network Name</label><input type="text" id="wifi_ssid" value="${c.wifi_ssid||''}"></div>
                    <div class="form-group"><label>Password</label><input type="password" id="wifi_password" placeholder="Leave blank to keep current"></div>
                </div>
            </div>

            <div id="api" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">API Keys</div></div>
                <div class="form-section">
                    <div class="section-title">Metra</div>
                    <div class="form-group"><label>API Token</label><input type="text" id="metra_token" value="${c.metra_token||''}"><div class="help-text">Get from metra.com/developers</div></div>
                </div>
                <div class="form-section">
                    <div class="section-title">CTA</div>
                    <div class="form-group"><label>API Key</label><input type="text" id="cta_token" value="${c.cta_token||''}"><div class="help-text">Get from transitchicago.com/developers</div></div>
                </div>
            </div>

            <div id="transit" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Transit Lines</div></div>
                
                <div class="form-section">
                    <div class="section-title">Display Mode</div>
                    <div class="form-group">
                        <label>Rotation Mode</label>
                        <select id="rotation_mode" onchange="TC.toggleRotationMode()">
                            <option value="direction" ${rotationMode==='direction'?'selected':''}>Direction Rotation (1-2 lines)</option>
                            <option value="station" ${rotationMode==='station'?'selected':''}>Station Rotation (3+ stations)</option>
                        </select>
                        <div class="help-text">Direction: show inbound/outbound. Station: cycle through stations</div>
                    </div>
                </div>

                <!-- Direction Mode Fields -->
                <div id="direction-mode-fields" style="${rotationMode==='direction'?'':'display:none'}">
                    <div class="form-section">
                        <div class="section-title">Primary Line</div>
                        <div class="form-group">
                            <label>Transit Type</label>
                            <select id="primary_transit_type" onchange="TC.updateTransitType('primary')">
                                <option value="metra" ${transitType==='metra'?'selected':''}>Metra</option>
                                <option value="cta" ${transitType==='cta'?'selected':''}>CTA</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Line</label>
                            <select id="line_select" onchange="TC.updateLine()">
                                <option value="">-- Select a Line --</option>
                                <optgroup label="Metra Lines" id="metra_lines_primary" ${transitType==='cta'?'style="display:none"':''}>
                                    ${buildLineOptions(c.line_id, 'metra')}
                                </optgroup>
                                <optgroup label="CTA Lines" id="cta_lines_primary" ${transitType==='metra'?'style="display:none"':''}>
                                    ${buildLineOptions(c.line_id, 'cta')}
                                </optgroup>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Station</label>
                            <select id="station_select" onchange="TC.updateStation()">
                                <option value="">-- Select a Station --</option>
                                <optgroup label="Metra Stations" id="metra_stations_primary" ${transitType==='cta'?'style="display:none"':''}>
                                    ${buildStationOptions(c.station_id, 'metra')}
                                </optgroup>
                                <optgroup label="CTA Stations" id="cta_stations_primary" ${transitType==='metra'?'style="display:none"':''}>
                                    ${buildStationOptions(c.station_id, 'cta')}
                                </optgroup>
                            </select>
                        </div>
                        <input type="hidden" id="line_id" value="${c.line_id||''}">
                        <input type="hidden" id="line_name" value="${c.line_name||''}">
                        <input type="hidden" id="station_id" value="${c.station_id||''}">
                        <input type="hidden" id="station_name" value="${c.station_name||''}">
                    </div>

                    <div class="form-section">
                        <div class="toggle-group">
                            <label class="toggle-label">Enable Secondary Line</label>
                            <label class="toggle-switch">
                                <input type="checkbox" id="enable_secondary" ${c.enable_secondary?'checked':''} onchange="TC.toggleSecondary()">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="help-text">Show a second transit line</div>

                        <div id="secondary-fields" style="${c.enable_secondary?'':'display:none'}; margin-top: 16px;">
                            <div class="form-group">
                                <label>Transit Type</label>
                                <select id="secondary_transit_type" onchange="TC.updateTransitType('secondary')">
                                    <option value="metra" ${secondaryTransitType==='metra'?'selected':''}>Metra</option>
                                    <option value="cta" ${secondaryTransitType==='cta'?'selected':''}>CTA</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Line</label>
                                <select id="secondary_line_select" onchange="TC.updateSecondaryLine()">
                                    <option value="">-- Select a Line --</option>
                                    <optgroup label="Metra Lines" id="metra_lines_secondary" ${secondaryTransitType==='cta'?'style="display:none"':''}>
                                        ${buildLineOptions(c.secondary_line_id, 'metra')}
                                    </optgroup>
                                    <optgroup label="CTA Lines" id="cta_lines_secondary" ${secondaryTransitType==='metra'?'style="display:none"':''}>
                                        ${buildLineOptions(c.secondary_line_id, 'cta')}
                                    </optgroup>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Station</label>
                                <select id="secondary_station_select" onchange="TC.updateSecondaryStation()">
                                    <option value="">-- Select a Station --</option>
                                    <optgroup label="Metra Stations" id="metra_stations_secondary" ${secondaryTransitType==='cta'?'style="display:none"':''}>
                                        ${buildStationOptions(c.secondary_station_id, 'metra')}
                                    </optgroup>
                                    <optgroup label="CTA Stations" id="cta_stations_secondary" ${secondaryTransitType==='metra'?'style="display:none"':''}>
                                        ${buildStationOptions(c.secondary_station_id, 'cta')}
                                    </optgroup>
                                </select>
                            </div>
                            <input type="hidden" id="secondary_line_id" value="${c.secondary_line_id||''}">
                            <input type="hidden" id="secondary_line_name" value="${c.secondary_line_name||''}">
                            <input type="hidden" id="secondary_station_id" value="${c.secondary_station_id||''}">
                            <input type="hidden" id="secondary_station_name" value="${c.secondary_station_name||''}">
                        </div>
                    </div>
                </div>

                <!-- Station Rotation Mode Fields -->
                <div id="station-mode-fields" style="${rotationMode==='station'?'':'display:none'}">
                    <div class="form-section">
                        <div class="section-title">Station 1</div>
                        <div class="form-group">
                            <label>Transit Type</label>
                            <select id="station1_transit_type" onchange="TC.updateTransitType('station1')">
                                <option value="metra">Metra</option>
                                <option value="cta">CTA</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Line</label>
                            <select id="station1_line_select" onchange="TC.updateStationLine(1)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_lines_station1">${buildLineOptions(c.station1_line_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_lines_station1" style="display:none">${buildLineOptions(c.station1_line_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Station</label>
                            <select id="station1_station_select" onchange="TC.updateStationInfo(1)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_stations_station1">${buildStationOptions(c.station1_station_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_stations_station1" style="display:none">${buildStationOptions(c.station1_station_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <input type="hidden" id="station1_line_id" value="${c.station1_line_id||''}">
                        <input type="hidden" id="station1_station_id" value="${c.station1_station_id||''}">
                    </div>
                    <div class="form-section">
                        <div class="section-title">Station 2</div>
                        <div class="form-group">
                            <label>Transit Type</label>
                            <select id="station2_transit_type" onchange="TC.updateTransitType('station2')">
                                <option value="metra">Metra</option>
                                <option value="cta">CTA</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Line</label>
                            <select id="station2_line_select" onchange="TC.updateStationLine(2)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_lines_station2">${buildLineOptions(c.station2_line_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_lines_station2" style="display:none">${buildLineOptions(c.station2_line_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Station</label>
                            <select id="station2_station_select" onchange="TC.updateStationInfo(2)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_stations_station2">${buildStationOptions(c.station2_station_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_stations_station2" style="display:none">${buildStationOptions(c.station2_station_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <input type="hidden" id="station2_line_id" value="${c.station2_line_id||''}">
                        <input type="hidden" id="station2_station_id" value="${c.station2_station_id||''}">
                    </div>
                    <div class="form-section">
                        <div class="section-title">Station 3</div>
                        <div class="form-group">
                            <label>Transit Type</label>
                            <select id="station3_transit_type" onchange="TC.updateTransitType('station3')">
                                <option value="metra">Metra</option>
                                <option value="cta">CTA</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Line</label>
                            <select id="station3_line_select" onchange="TC.updateStationLine(3)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_lines_station3">${buildLineOptions(c.station3_line_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_lines_station3" style="display:none">${buildLineOptions(c.station3_line_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Station</label>
                            <select id="station3_station_select" onchange="TC.updateStationInfo(3)">
                                <option value="">-- Select --</option>
                                <optgroup label="Metra" id="metra_stations_station3">${buildStationOptions(c.station3_station_id, 'metra')}</optgroup>
                                <optgroup label="CTA" id="cta_stations_station3" style="display:none">${buildStationOptions(c.station3_station_id, 'cta')}</optgroup>
                            </select>
                        </div>
                        <input type="hidden" id="station3_line_id" value="${c.station3_line_id||''}">
                        <input type="hidden" id="station3_station_id" value="${c.station3_station_id||''}">
                    </div>
                    <div class="help-text" style="text-align:center;padding:16px;color:#666;">
                        Configure 3+ stations to rotate through.
                    </div>
                </div>
            </div>

            <div id="display" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Display</div></div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Brightness</label>
                        <div style="display:flex;align-items:center;gap:12px;">
                            <input type="range" id="brightness" min="0.1" max="1.0" step="0.1" value="${c.brightness||0.5}" oninput="document.getElementById('bv').textContent=Math.round(this.value*100)+'%'" style="flex:1">
                            <span id="bv" style="min-width:45px;font-weight:600">${Math.round((c.brightness||0.5)*100)}%</span>
                        </div>
                    </div>
                    <div class="form-group"><label>Rotation Time (sec)</label><input type="number" id="rotation_time" min="1" max="30" value="${c.rotation_time||5}"></div>
                    <div class="form-group"><label>Update Interval (sec)</label><input type="number" id="update_interval" min="10" max="300" value="${c.update_interval||30}"></div>
                    <div class="form-group"><label>Trains to Show</label><input type="number" id="num_trains" min="1" max="8" value="${c.num_trains||4}"></div>
                </div>
            </div>

            <div id="features" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Features</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Service Alerts</label><label class="toggle-switch"><input type="checkbox" id="enable_service_alerts" ${c.enable_service_alerts?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Show service disruption alerts</div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Alert Icons</label><label class="toggle-switch"><input type="checkbox" id="enable_alert_icons" ${c.enable_alert_icons?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Show warning icons on affected trains</div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Alert Update Interval (seconds)</label>
                        <input type="number" id="alerts_update_interval" min="60" max="600" value="${c.alerts_update_interval||180}">
                        <div class="help-text">How often to check for alerts (default: 180 = 3 min)</div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Auto-Update</label><label class="toggle-switch"><input type="checkbox" id="enable_auto_update" ${c.enable_auto_update?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Automatically check for firmware updates</div>
                    <div class="form-group" style="margin-top:16px;">
                        <label>Update Check Interval</label>
                        <select id="check_update_interval">
                            <option value="86400" ${(c.check_update_interval||86400)==86400?'selected':''}>Daily</option>
                            <option value="604800" ${c.check_update_interval==604800?'selected':''}>Weekly</option>
                            <option value="2592000" ${c.check_update_interval==2592000?'selected':''}>Monthly</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="weather" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Weather</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Enable Weather</label><label class="toggle-switch"><input type="checkbox" id="enable_weather" ${c.enable_weather?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Show weather icon and temperature</div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Weather Service</label>
                        <select id="weather_api_service">
                            <option value="weathergov" ${(c.weather_api_service||'weathergov')==='weathergov'?'selected':''}>Weather.gov (Free, US only)</option>
                            <option value="openweathermap" ${c.weather_api_service==='openweathermap'?'selected':''}>OpenWeatherMap (API key required)</option>
                        </select>
                        <div class="help-text">Choose weather data provider</div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>ZIP Code / Location</label>
                        <input type="text" id="weather_zip_code" value="${c.weather_zip_code||''}" placeholder="60601">
                        <div class="help-text">Your location for weather data</div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>API Key (OpenWeatherMap only)</label>
                        <input type="password" id="weather_api_key" value="${c.weather_api_key||''}">
                        <div class="help-text">Required for OpenWeatherMap</div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Display Mode</label>
                        <select id="weather_display_mode">
                            <option value="icon_only" ${(c.weather_display_mode||'icon_only')==='icon_only'?'selected':''}>Icon only</option>
                            <option value="icon_and_temp" ${c.weather_display_mode==='icon_and_temp'?'selected':''}>Icon + Temperature</option>
                        </select>
                        <div class="help-text">How to show weather on display</div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Update Interval</label>
                        <select id="weather_update_interval">
                            <option value="900" ${c.weather_update_interval==900?'selected':''}>15 minutes</option>
                            <option value="1800" ${(c.weather_update_interval||1800)==1800?'selected':''}>30 minutes</option>
                            <option value="3600" ${c.weather_update_interval==3600?'selected':''}>1 hour</option>
                        </select>
                        <div class="help-text">How often to fetch weather data</div>
                    </div>
                </div>
            </div>

            <div id="system" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">System</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Watchdog Timer</label><label class="toggle-switch"><input type="checkbox" id="enable_watchdog" ${c.enable_watchdog?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Auto-reboot if system hangs (recommended)</div>
                    <div class="form-group" style="margin-top:16px;">
                        <label>Watchdog Timeout</label>
                        <select id="watchdog_timeout">
                            <option value="5000" ${c.watchdog_timeout==5000?'selected':''}>5 seconds</option>
                            <option value="8000" ${(c.watchdog_timeout||8000)==8000?'selected':''}>8 seconds</option>
                            <option value="10000" ${c.watchdog_timeout==10000?'selected':''}>10 seconds</option>
                        </select>
                    </div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Status LED</label><label class="toggle-switch"><input type="checkbox" id="enable_status_led" ${c.enable_status_led?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">RGB LED shows connection status (green=connected, red=error)</div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Sleep Mode</label><label class="toggle-switch"><input type="checkbox" id="enable_sleep_mode" ${c.enable_sleep_mode?'checked':''} onchange="TC.toggleSleep()"><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Dim display during night hours</div>
                    <div id="sleep-fields" style="${c.enable_sleep_mode?'':'display:none'}; margin-top:16px;">
                        <div class="form-group">
                            <label>Sleep Start Hour</label>
                            <select id="sleep_start_hour">
                                <option value="20" ${c.sleep_start_hour==20?'selected':''}>8 PM</option>
                                <option value="21" ${c.sleep_start_hour==21?'selected':''}>9 PM</option>
                                <option value="22" ${(c.sleep_start_hour||22)==22?'selected':''}>10 PM</option>
                                <option value="23" ${c.sleep_start_hour==23?'selected':''}>11 PM</option>
                                <option value="0" ${c.sleep_start_hour==0?'selected':''}>Midnight</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Sleep End Hour</label>
                            <select id="sleep_end_hour">
                                <option value="5" ${c.sleep_end_hour==5?'selected':''}>5 AM</option>
                                <option value="6" ${(c.sleep_end_hour||6)==6?'selected':''}>6 AM</option>
                                <option value="7" ${c.sleep_end_hour==7?'selected':''}>7 AM</option>
                                <option value="8" ${c.sleep_end_hour==8?'selected':''}>8 AM</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Sleep Brightness</label>
                            <div style="display:flex;align-items:center;gap:12px;">
                                <input type="range" id="sleep_brightness" min="0.05" max="0.3" step="0.05" value="${c.sleep_brightness||0.1}" oninput="document.getElementById('sbv').textContent=Math.round(this.value*100)+'%'" style="flex:1">
                                <span id="sbv" style="min-width:45px;font-weight:600">${Math.round((c.sleep_brightness||0.1)*100)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Adaptive Brightness</label><label class="toggle-switch"><input type="checkbox" id="enable_adaptive_brightness" ${c.enable_adaptive_brightness?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Auto-adjust brightness by time of day</div>
                    <div class="help-text" style="margin-top:8px;color:#999;">Day: 100% | Evening: 70% | Night: 30%</div>
                    <div class="help-text" style="margin-top:4px;color:#f57c00;">⚠️ Cannot use with Sleep Mode</div>
                </div>
            </div>
        `;
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    function nav(pageId) {
        const cur = document.getElementById(currentPage);
        const next = document.getElementById(pageId);
        pageStack.push(currentPage);
        next.classList.remove('hidden');
        next.style.transform = 'translateX(100%)';
        setTimeout(() => { cur.classList.add('slide-left'); next.style.transform = 'translateX(0)'; }, 10);
        setTimeout(() => { cur.classList.add('hidden'); cur.classList.remove('slide-left'); if(typeof lucide!=='undefined')lucide.createIcons(); }, 300);
        currentPage = pageId;
    }

    function back() {
        if (!pageStack.length) return;
        const cur = document.getElementById(currentPage);
        const prev = document.getElementById(pageStack.pop());
        prev.classList.remove('hidden');
        prev.classList.add('slide-left');
        setTimeout(() => { cur.style.transform = 'translateX(100%)'; prev.classList.remove('slide-left'); }, 10);
        setTimeout(() => { cur.classList.add('hidden'); cur.style.transform = 'translateX(0)'; }, 300);
        currentPage = prev.id;
    }

    // Toggle helpers
    function toggleRotationMode() {
        const mode = document.getElementById('rotation_mode').value;
        document.getElementById('direction-mode-fields').style.display = mode === 'direction' ? '' : 'none';
        document.getElementById('station-mode-fields').style.display = mode === 'station' ? '' : 'none';
    }

    function toggleSecondary() {
        const checked = document.getElementById('enable_secondary').checked;
        document.getElementById('secondary-fields').style.display = checked ? '' : 'none';
    }

    function toggleSleep() {
        const checked = document.getElementById('enable_sleep_mode').checked;
        document.getElementById('sleep-fields').style.display = checked ? '' : 'none';
    }

    function updateTransitType(which) {
        const type = document.getElementById(which + '_transit_type').value;
        const isCta = type === 'cta';
        
        // Show/hide line options
        const metraLines = document.getElementById('metra_lines_' + which);
        const ctaLines = document.getElementById('cta_lines_' + which);
        if (metraLines) metraLines.style.display = isCta ? 'none' : '';
        if (ctaLines) ctaLines.style.display = isCta ? '' : 'none';
        
        // Show/hide station options
        const metraStations = document.getElementById('metra_stations_' + which);
        const ctaStations = document.getElementById('cta_stations_' + which);
        if (metraStations) metraStations.style.display = isCta ? 'none' : '';
        if (ctaStations) ctaStations.style.display = isCta ? '' : 'none';
    }

    function updateLine() {
        const v = document.getElementById('line_select').value;
        if (v) { const p = v.split('|'); document.getElementById('line_id').value = p[0]; document.getElementById('line_name').value = p[1]; }
    }

    function updateStation() {
        const v = document.getElementById('station_select').value;
        if (v) { const p = v.split('|'); document.getElementById('station_id').value = p[0]; document.getElementById('station_name').value = p[1]; }
    }

    function updateSecondaryLine() {
        const v = document.getElementById('secondary_line_select').value;
        if (v) { const p = v.split('|'); document.getElementById('secondary_line_id').value = p[0]; document.getElementById('secondary_line_name').value = p[1]; }
    }

    function updateSecondaryStation() {
        const v = document.getElementById('secondary_station_select').value;
        if (v) { const p = v.split('|'); document.getElementById('secondary_station_id').value = p[0]; document.getElementById('secondary_station_name').value = p[1]; }
    }

    function updateStationLine(num) {
        const v = document.getElementById('station' + num + '_line_select').value;
        if (v) { const p = v.split('|'); document.getElementById('station' + num + '_line_id').value = p[0]; }
    }

    function updateStationInfo(num) {
        const v = document.getElementById('station' + num + '_station_select').value;
        if (v) { const p = v.split('|'); document.getElementById('station' + num + '_station_id').value = p[0]; }
    }

    async function save() {
        const data = {};
        // Only send non-empty values and checkboxes that are checked
        document.querySelectorAll('input[type="text"],input[type="password"],input[type="number"],input[type="range"],select').forEach(i => { 
            if(i.id && i.value) data[i.id] = i.value; 
        });
        // Hidden fields - only if they have values
        document.querySelectorAll('input[type="hidden"]').forEach(i => { 
            if(i.id && i.value) data[i.id] = i.value; 
        });
        document.querySelectorAll('input[type="checkbox"]').forEach(i => { 
            if(i.id && i.checked) data[i.id] = true; 
        });
        
        try {
            const res = await fetch('/api/save', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            if (res.ok) { alert('Saved! Restarting...'); setTimeout(() => location.reload(), 3000); }
            else throw new Error('Save failed');
        } catch(e) { alert('Error: ' + e.message); }
    }

    window.TC = { 
        nav, back, 
        toggleRotationMode, toggleSecondary, toggleSleep, updateTransitType,
        updateLine, updateStation, updateSecondaryLine, updateSecondaryStation,
        updateStationLine, updateStationInfo, save 
    };
})();
