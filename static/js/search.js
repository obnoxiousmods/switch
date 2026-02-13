// Switch Game Repository - Reactive Search
(function() {
    'use strict';
    
    let allEntries = [];
    let filteredEntries = [];
    let currentPage = 1;
    let itemsPerPage = 10;
    
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
        
        // Reset to first page when search changes
        currentPage = 1;
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
        
        // Calculate pagination
        const totalPages = Math.ceil(count / itemsPerPage);
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const paginatedEntries = filteredEntries.slice(startIndex, endIndex);
        
        // Render each result for current page
        paginatedEntries.forEach(entry => {
            const card = createResultCard(entry);
            resultsGrid.appendChild(card);
        });
        
        // Render pagination controls
        renderPagination(totalPages, count);
    }
    
    // Render pagination controls
    function renderPagination(totalPages, totalCount) {
        // Find or create pagination container
        let paginationContainer = document.getElementById('pagination-controls');
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.id = 'pagination-controls';
            paginationContainer.className = 'pagination-container';
            
            // Insert after results grid
            const resultsSection = document.querySelector('.results-section');
            if (resultsSection) {
                resultsSection.appendChild(paginationContainer);
            }
        }
        
        // Clear existing content
        paginationContainer.innerHTML = '';
        
        // Don't show pagination if only one page
        if (totalPages <= 1) {
            return;
        }
        
        // Create pagination wrapper
        const paginationWrapper = document.createElement('div');
        paginationWrapper.className = 'pagination-wrapper';
        
        // Items per page selector
        const itemsPerPageContainer = document.createElement('div');
        itemsPerPageContainer.className = 'items-per-page-container';
        itemsPerPageContainer.innerHTML = `
            <label for="items-per-page">Items per page:</label>
            <select id="items-per-page" class="items-per-page-select">
                <option value="10" ${itemsPerPage === 10 ? 'selected' : ''}>10</option>
                <option value="25" ${itemsPerPage === 25 ? 'selected' : ''}>25</option>
                <option value="50" ${itemsPerPage === 50 ? 'selected' : ''}>50</option>
                <option value="100" ${itemsPerPage === 100 ? 'selected' : ''}>100</option>
            </select>
        `;
        
        // Page info
        const pageInfo = document.createElement('div');
        pageInfo.className = 'page-info';
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(currentPage * itemsPerPage, totalCount);
        pageInfo.textContent = `Showing ${startItem}-${endItem} of ${totalCount}`;
        
        // Page controls
        const pageControls = document.createElement('div');
        pageControls.className = 'page-controls';
        
        // Previous button
        const prevButton = document.createElement('button');
        prevButton.className = 'page-button';
        prevButton.textContent = '← Previous';
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderResults();
                scrollToTop();
            }
        });
        
        // Page numbers
        const pageNumbers = document.createElement('div');
        pageNumbers.className = 'page-numbers';
        
        // Calculate which page numbers to show
        const maxPageButtons = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);
        
        // Adjust start if we're near the end
        if (endPage - startPage < maxPageButtons - 1) {
            startPage = Math.max(1, endPage - maxPageButtons + 1);
        }
        
        // First page button
        if (startPage > 1) {
            const firstButton = createPageButton(1, 1 === currentPage);
            pageNumbers.appendChild(firstButton);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                pageNumbers.appendChild(ellipsis);
            }
        }
        
        // Page number buttons
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = createPageButton(i, i === currentPage);
            pageNumbers.appendChild(pageButton);
        }
        
        // Last page button
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                pageNumbers.appendChild(ellipsis);
            }
            
            const lastButton = createPageButton(totalPages, totalPages === currentPage);
            pageNumbers.appendChild(lastButton);
        }
        
        // Next button
        const nextButton = document.createElement('button');
        nextButton.className = 'page-button';
        nextButton.textContent = 'Next →';
        nextButton.disabled = currentPage === totalPages;
        nextButton.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderResults();
                scrollToTop();
            }
        });
        
        // Assemble page controls
        pageControls.appendChild(prevButton);
        pageControls.appendChild(pageNumbers);
        pageControls.appendChild(nextButton);
        
        // Assemble pagination wrapper
        paginationWrapper.appendChild(itemsPerPageContainer);
        paginationWrapper.appendChild(pageInfo);
        paginationWrapper.appendChild(pageControls);
        
        paginationContainer.appendChild(paginationWrapper);
        
        // Add event listener for items per page selector
        const itemsPerPageSelect = document.getElementById('items-per-page');
        if (itemsPerPageSelect) {
            itemsPerPageSelect.addEventListener('change', (e) => {
                itemsPerPage = parseInt(e.target.value);
                currentPage = 1;
                renderResults();
                scrollToTop();
            });
        }
    }
    
    // Create a page button
    function createPageButton(pageNum, isActive) {
        const button = document.createElement('button');
        button.className = 'page-number-button' + (isActive ? ' active' : '');
        button.textContent = pageNum;
        button.addEventListener('click', () => {
            currentPage = pageNum;
            renderResults();
            scrollToTop();
        });
        return button;
    }
    
    // Scroll to top of results
    function scrollToTop() {
        const resultsSection = document.querySelector('.results-section');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Create a result card element
    function createResultCard(entry) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Add click handler for download
        card.addEventListener('click', () => {
            handleDownload(entry);
        });
        
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
        
        // Created at
        const dateItem = document.createElement('div');
        dateItem.className = 'meta-item';
        dateItem.innerHTML = `📅 ${formatDate(entry.created_at)}`;
        
        meta.appendChild(fileTypeItem);
        meta.appendChild(sizeItem);
        meta.appendChild(dateItem);
        
        card.appendChild(title);
        card.appendChild(meta);
        
        return card;
    }
    
    // Handle download of an entry
    function handleDownload(entry) {
        // For URLs, open in a new window to trigger download
        if (entry.type === 'url') {
            window.open(entry.source, '_blank');
        } else {
            // For filepaths, use the download API endpoint
            const downloadUrl = `/api/download/${encodeURIComponent(entry.id)}`;
            window.location.href = downloadUrl;
        }
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
            
            // Reset time components for accurate day comparison
            const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            const nowOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const diffTime = nowOnly - dateOnly;
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
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
