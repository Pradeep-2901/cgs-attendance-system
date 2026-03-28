-- =============================================
-- UNIFIED GEOFENCING SYSTEM - MISSING TABLES ONLY
-- Only create tables that don't exist yet
-- =============================================

USE cgs;

-- =============================================
-- 1. SITES TABLE (for on-site visit locations)
-- =============================================
CREATE TABLE IF NOT EXISTS sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL,
    site_address VARCHAR(255) NOT NULL,
    site_lat DECIMAL(10,8) NOT NULL,
    site_lon DECIMAL(11,8) NOT NULL,
    site_radius INT DEFAULT 200,
    site_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- =============================================
-- 2. SITE VISITS TABLE (employee visit requests)
-- =============================================
CREATE TABLE IF NOT EXISTS site_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    site_id INT NOT NULL,
    visit_date DATE NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    admin_notes TEXT,
    approved_by VARCHAR(10),
    approved_date TIMESTAMP NULL,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (site_id) REFERENCES sites(id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id),
    
    UNIQUE KEY unique_user_date (user_id, visit_date)
);

-- =============================================
-- 3. ADD MISSING COMPANY SETTINGS
-- =============================================
INSERT IGNORE INTO company_settings (setting_name, setting_value) VALUES
('geofencing_enabled', 'true');

-- =============================================
-- 4. ADD SAMPLE SITES
-- =============================================
INSERT IGNORE INTO sites (site_name, site_address, site_lat, site_lon, created_by) VALUES
('Client Office - Tech Park', 'IT Corridor, OMR, Chennai, Tamil Nadu', 12.9698, 80.2434, 'adm001'),
('Project Site - Guindy', 'Guindy Industrial Estate, Chennai, Tamil Nadu', 13.0067, 80.2206, 'adm001'),
('Regional Office - Coimbatore', 'RS Puram, Coimbatore, Tamil Nadu', 11.0168, 76.9558, 'adm001');

-- =============================================
-- VERIFICATION QUERIES
-- =============================================
SELECT 'Company Settings:' as Info;
SELECT setting_name, setting_value FROM company_settings WHERE setting_name LIKE '%office%' OR setting_name = 'geofencing_enabled';

SELECT 'Sites Created:' as Info;
SELECT site_name, site_address, is_active FROM sites;

SELECT 'Schema Ready!' as Status;