// Switch Game Repository - Reactive Search
(function() {
    'use strict';
    
    let allEntries = [];
    let filteredEntries = [];
    
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const resultsGrid = document.getElementById('results-grid');
    const resultsCount = document.getElementById('results-count');
    const loadingState = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');
    
    // Initialize the application
    async function init() {
        // Auto-focus search input
        if (searchInput) {
            searchInput.focus();
        }
        
        // Load entries from API
        await loadEntries();
        
        // Set up event listeners
        if (searchInput) {
            searchInput.addEventListener('input', handleSearch);
        }
    }
    
    // Load all entries from the API
    async function loadEntries() {
        try {
            showLoading();
            
            const response = await fetch('/api/list');
            if (!response.ok) {
                throw new Error('Failed to fetch entries');
            }
            
            const data = await response.json();
            allEntries = data.entries || [];
            filteredEntries = allEntries;
            
            hideLoading();
            renderResults();
            
        } catch (error) {
            console.error('Error loading entries:', error);
            hideLoading();
            showError('Failed to load entries. Please try again later.');
        }
    }
    
    // Handle search input
    function handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            // Show all entries if search is empty
            filteredEntries = allEntries;
        } else {
            // Filter entries by name
            filteredEntries = allEntries.filter(entry => {
                return entry.name.toLowerCase().includes(searchTerm);
            });
        }
        
        renderResults();
    }
    
    // Render the results
    function renderResults() {
        if (!resultsGrid || !resultsCount) return;
        
        // Update count
        const count = filteredEntries.length;
        resultsCount.textContent = `${count} ${count === 1 ? 'result' : 'results'} found`;
        
        // Clear previous results
        resultsGrid.innerHTML = '';
        
        // Show empty state if no results
        if (count === 0) {
            showEmptyState();
            return;
        }
        
        hideEmptyState();
        
        // Render each result
        filteredEntries.forEach(entry => {
            const card = createResultCard(entry);
            resultsGrid.appendChild(card);
        });
    }
    
    // Create a result card element
    function createResultCard(entry) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const title = document.createElement('div');
        title.className = 'result-title';
        title.textContent = entry.name;
        
        const meta = document.createElement('div');
        meta.className = 'result-meta';
        
        // File type badge
        const fileTypeBadge = document.createElement('span');
        fileTypeBadge.className = `file-type-badge file-type-${entry.file_type}`;
        fileTypeBadge.textContent = entry.file_type.toUpperCase();
        
        const fileTypeItem = document.createElement('div');
        fileTypeItem.className = 'meta-item';
        fileTypeItem.appendChild(fileTypeBadge);
        
        // Size
        const sizeItem = document.createElement('div');
        sizeItem.className = 'meta-item';
        sizeItem.innerHTML = `📦 ${formatSize(entry.size)}`;
        
        // Type (filepath or url)
        const typeItem = document.createElement('div');
        typeItem.className = 'meta-item';
        typeItem.innerHTML = `📍 ${entry.type}`;
        
        // Created at
        const dateItem = document.createElement('div');
        dateItem.className = 'meta-item';
        dateItem.innerHTML = `📅 ${formatDate(entry.created_at)}`;
        
        meta.appendChild(fileTypeItem);
        meta.appendChild(sizeItem);
        meta.appendChild(typeItem);
        meta.appendChild(dateItem);
        
        card.appendChild(title);
        card.appendChild(meta);
        
        return card;
    }
    
    // Format file size
    function formatSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Format date
    function formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
            if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
            
            return date.toLocaleDateString();
        } catch (error) {
            return dateString;
        }
    }
    
    // Show loading state
    function showLoading() {
        if (loadingState) {
            loadingState.classList.remove('hidden');
        }
        if (resultsGrid) {
            resultsGrid.classList.add('hidden');
        }
        hideEmptyState();
    }
    
    // Hide loading state
    function hideLoading() {
        if (loadingState) {
            loadingState.classList.add('hidden');
        }
        if (resultsGrid) {
            resultsGrid.classList.remove('hidden');
        }
    }
    
    // Show empty state
    function showEmptyState() {
        if (emptyState) {
            emptyState.classList.remove('hidden');
        }
    }
    
    // Hide empty state
    function hideEmptyState() {
        if (emptyState) {
            emptyState.classList.add('hidden');
        }
    }
    
    // Show error message
    function showError(message) {
        if (resultsGrid) {
            resultsGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <div class="empty-state-title">Error</div>
                    <div class="empty-state-message">${message}</div>
                </div>
            `;
            resultsGrid.classList.remove('hidden');
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
