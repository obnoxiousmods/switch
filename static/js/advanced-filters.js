/**
 * Advanced Filters Module
 * Handles advanced filtering functionality for search results
 */

(function() {
    'use strict';
    
    // Filter state
    let activeFilters = {
        fileType: 'all',
        size: 'all',
        date: 'all',
        downloads: 'all'
    };
    
    // DOM Elements
    let filtersToggle;
    let filtersContent;
    let fileTypeFilter;
    let sizeFilter;
    let dateFilter;
    let downloadsFilter;
    let applyFiltersBtn;
    let clearFiltersBtn;
    
    // Initialize the module
    function init() {
        // Get DOM elements
        filtersToggle = document.getElementById('filters-toggle');
        filtersContent = document.getElementById('filters-content');
        fileTypeFilter = document.getElementById('file-type-filter');
        sizeFilter = document.getElementById('size-filter');
        dateFilter = document.getElementById('date-filter');
        downloadsFilter = document.getElementById('downloads-filter');
        applyFiltersBtn = document.getElementById('apply-filters');
        clearFiltersBtn = document.getElementById('clear-filters');
        
        if (!filtersToggle || !filtersContent) return;
        
        // Load saved filters from localStorage
        loadSavedFilters();
        
        // Set up event listeners
        filtersToggle.addEventListener('click', toggleFiltersPanel);
        applyFiltersBtn.addEventListener('click', applyFilters);
        clearFiltersBtn.addEventListener('click', clearFilters);
        
        // Apply filters on initialization if any are active
        if (hasActiveFilters()) {
            applyFilters(true);
            updateActiveIndicator();
        }
    }
    
    // Toggle filters panel
    function toggleFiltersPanel() {
        filtersToggle.classList.toggle('active');
        filtersContent.classList.toggle('open');
        
        // Save state to localStorage
        const isOpen = filtersContent.classList.contains('open');
        localStorage.setItem('filtersOpen', isOpen);
    }
    
    // Apply filters
    function applyFilters(silent = false) {
        // Get current filter values
        activeFilters.fileType = fileTypeFilter.value;
        activeFilters.size = sizeFilter.value;
        activeFilters.date = dateFilter.value;
        activeFilters.downloads = downloadsFilter.value;
        
        // Save to localStorage
        localStorage.setItem('activeFilters', JSON.stringify(activeFilters));
        
        // Visual feedback
        if (!silent) {
            applyFiltersBtn.classList.add('applying');
            setTimeout(() => {
                applyFiltersBtn.classList.remove('applying');
            }, 1000);
        }
        
        // Trigger filter application in main search
        if (window.applyAdvancedFilters) {
            window.applyAdvancedFilters(activeFilters);
        }
        
        // Update active indicator
        updateActiveIndicator();
    }
    
    // Clear all filters
    function clearFilters() {
        fileTypeFilter.value = 'all';
        sizeFilter.value = 'all';
        dateFilter.value = 'all';
        downloadsFilter.value = 'all';
        
        // Reset filter state
        activeFilters = {
            fileType: 'all',
            size: 'all',
            date: 'all',
            downloads: 'all'
        };
        
        // Clear from localStorage
        localStorage.removeItem('activeFilters');
        
        // Apply cleared filters
        if (window.applyAdvancedFilters) {
            window.applyAdvancedFilters(activeFilters);
        }
        
        // Update active indicator
        updateActiveIndicator();
    }
    
    // Load saved filters from localStorage
    function loadSavedFilters() {
        const savedFilters = localStorage.getItem('activeFilters');
        if (savedFilters) {
            try {
                activeFilters = JSON.parse(savedFilters);
                
                // Apply to select elements
                if (fileTypeFilter) fileTypeFilter.value = activeFilters.fileType || 'all';
                if (sizeFilter) sizeFilter.value = activeFilters.size || 'all';
                if (dateFilter) dateFilter.value = activeFilters.date || 'all';
                if (downloadsFilter) downloadsFilter.value = activeFilters.downloads || 'all';
            } catch (e) {
                console.error('Error loading saved filters:', e);
            }
        }
        
        // Load panel state
        const filtersOpen = localStorage.getItem('filtersOpen');
        if (filtersOpen === 'true') {
            filtersContent.classList.add('open');
            filtersToggle.classList.add('active');
        }
    }
    
    // Check if any filters are active
    function hasActiveFilters() {
        return activeFilters.fileType !== 'all' ||
               activeFilters.size !== 'all' ||
               activeFilters.date !== 'all' ||
               activeFilters.downloads !== 'all';
    }
    
    // Update active indicator on toggle button
    function updateActiveIndicator() {
        const existing = filtersToggle.querySelector('.active-indicator');
        
        if (hasActiveFilters()) {
            if (!existing) {
                const indicator = document.createElement('span');
                indicator.className = 'active-indicator';
                indicator.title = 'Filters are active';
                filtersToggle.appendChild(indicator);
            }
        } else {
            if (existing) {
                existing.remove();
            }
        }
    }
    
    // Export function to get current filters
    window.getActiveFilters = function() {
        return activeFilters;
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
