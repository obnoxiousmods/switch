// Switch Game Repository - Reactive Search
(function() {
    'use strict';
    
    let allEntries = [];
    let filteredEntries = [];
    let currentPage = 1;
    let itemsPerPage = 10;
    let sortBy = 'name'; // 'name', 'downloads', 'size', or 'recent'
    
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const resultsGrid = document.getElementById('results-grid');
    const resultsCount = document.getElementById('results-count');
    const loadingState = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');
    const sortSelect = document.getElementById('sort-select');
    
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
        
        if (sortSelect) {
            sortSelect.addEventListener('change', handleSortChange);
        }
    }
    
    // Load all entries from the API
    async function loadEntries() {
        try {
            showLoading();
            
            // Include sort_by parameter
            const sortParam = sortBy !== 'name' ? `?sort_by=${sortBy}` : '';
            const response = await fetch(`/api/list${sortParam}`);
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
    
    // Handle sort change
    function handleSortChange(event) {
        sortBy = event.target.value;
        currentPage = 1;
        loadEntries();
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
        
        // File modified date (use file_modified_at if available, otherwise created_at)
        const dateItem = document.createElement('div');
        dateItem.className = 'meta-item';
        const dateToShow = entry.file_modified_at || entry.created_at;
        dateItem.innerHTML = `📅 ${formatDate(dateToShow)}`;
        dateItem.title = entry.file_modified_at ? `File modified: ${dateToShow}` : `Added: ${dateToShow}`;
        
        // Download count
        const downloadItem = document.createElement('div');
        downloadItem.className = 'meta-item';
        const downloadCount = entry.download_count || 0;
        downloadItem.innerHTML = `⬇️ ${downloadCount} download${downloadCount !== 1 ? 's' : ''}`;
        
        meta.appendChild(fileTypeItem);
        meta.appendChild(sizeItem);
        meta.appendChild(dateItem);
        meta.appendChild(downloadItem);
        
        // Report warning badge if there are open reports
        if (entry.report_count && entry.report_count > 0) {
            const reportBadge = document.createElement('div');
            reportBadge.className = 'report-warning-badge';
            reportBadge.innerHTML = `⚠️ ${entry.report_count} report${entry.report_count !== 1 ? 's' : ''}`;
            reportBadge.title = 'This file has been reported as broken or corrupted';
            card.appendChild(reportBadge);
        }
        
        // Action buttons container
        const actions = document.createElement('div');
        actions.className = 'result-actions';
        
        // Download button
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn-download';
        downloadBtn.textContent = '⬇️ Download';
        downloadBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            handleDownload(entry);
        });
        
        // Info button
        const infoBtn = document.createElement('button');
        infoBtn.className = 'btn-info';
        infoBtn.textContent = 'ℹ️ Info';
        infoBtn.title = 'View detailed information';
        infoBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showFileInfo(entry);
        });
        
        // Report button
        const reportBtn = document.createElement('button');
        reportBtn.className = 'btn-report';
        reportBtn.textContent = '⚠️ Report';
        reportBtn.title = 'Report this file as broken or corrupted';
        reportBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            handleReport(entry);
        });
        
        actions.appendChild(downloadBtn);
        actions.appendChild(infoBtn);
        actions.appendChild(reportBtn);
        
        card.appendChild(title);
        card.appendChild(meta);
        card.appendChild(actions);
        
        return card;
    }
    
    // Handle download of an entry
    function handleDownload(entry) {
        // For URLs, open in a new window to trigger download
        if (entry.type === 'url') {
            window.open(entry.source, '_blank');
        } else {
            // For filepaths, use the download API endpoint
            const downloadUrl = `/api/download/${encodeURIComponent(entry._key)}`;
            window.location.href = downloadUrl;
        }
    }
    
    // Show detailed file information
    async function showFileInfo(entry) {
        // Fetch the latest entry information from the server
        try {
            const response = await fetch(`/api/entries/${encodeURIComponent(entry._key)}/info`);
            const data = await response.json();
            
            if (data.success && data.entry) {
                // Use the fresh data from the server
                entry = data.entry;
            }
        } catch (error) {
            console.error('Failed to fetch latest entry info:', error);
            // Continue with the existing entry data if fetch fails
        }
        
        const modal = document.createElement('div');
        modal.className = 'info-modal-overlay';
        
        // Format dates
        const addedDate = entry.created_at ? formatFullDate(entry.created_at) : 'N/A';
        const fileCreated = entry.file_created_at ? formatFullDate(entry.file_created_at) : 'N/A';
        const fileModified = entry.file_modified_at ? formatFullDate(entry.file_modified_at) : 'N/A';
        
        // Check if hashes exist or are being processed
        const hasMD5 = entry.md5_hash && entry.md5_hash !== 'processing' && entry.md5_hash.length > 0;
        const hasSHA256 = entry.sha256_hash && entry.sha256_hash !== 'processing' && entry.sha256_hash.length > 0;
        const isProcessing = entry.md5_hash === 'processing' || entry.sha256_hash === 'processing';
        const canComputeHashes = entry.type === 'filepath';
        
        modal.innerHTML = `
            <div class="info-modal">
                <div class="info-modal-header">
                    <h3>📋 File Information</h3>
                    <button class="modal-close" onclick="this.closest('.info-modal-overlay').remove()">✕</button>
                </div>
                <div class="info-modal-body">
                    <h4 class="info-file-name">${entry.name}</h4>
                    
                    <div class="info-section">
                        <div class="info-row">
                            <span class="info-label">File Type:</span>
                            <span class="info-value">
                                <span class="file-type-badge file-type-${entry.file_type}">${entry.file_type.toUpperCase()}</span>
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">File Size:</span>
                            <span class="info-value">${formatSize(entry.size)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Downloads:</span>
                            <span class="info-value">${entry.downloads || entry.download_count || 0} times</span>
                        </div>
                        ${entry.report_count > 0 ? `
                        <div class="info-row warning">
                            <span class="info-label">⚠️ Reports:</span>
                            <span class="info-value">${entry.report_count} open report${entry.report_count !== 1 ? 's' : ''}</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="info-section">
                        <h5>📅 Dates</h5>
                        <div class="info-row">
                            <span class="info-label">Added to Library:</span>
                            <span class="info-value">${addedDate}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">File Created:</span>
                            <span class="info-value">${fileCreated}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Last Modified:</span>
                            <span class="info-value">${fileModified}</span>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h5>🔐 File Hashes</h5>
                        <div id="hash-section-${entry._key}">
                            ${isProcessing ? `
                            <div class="info-row">
                                <span class="info-label">MD5:</span>
                                <span class="info-value"><em>Processing...</em></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">SHA256:</span>
                                <span class="info-value"><em>Processing...</em></span>
                            </div>
                            <div class="info-row">
                                <span class="info-value" style="color: #5a9fd4;">⏳ Hash computation in progress. Please wait...</span>
                            </div>
                            ` : hasMD5 || hasSHA256 ? `
                            ${hasMD5 ? `
                            <div class="info-row">
                                <span class="info-label">MD5:</span>
                                <span class="info-value hash-value">${entry.md5_hash}</span>
                            </div>
                            ` : ''}
                            ${hasSHA256 ? `
                            <div class="info-row">
                                <span class="info-label">SHA256:</span>
                                <span class="info-value hash-value">${entry.sha256_hash}</span>
                            </div>
                            ` : ''}
                            ${canComputeHashes ? `
                            <div class="info-row" style="margin-top: 10px;">
                                <button class="btn-compute-hash" onclick="computeHashes('${entry._key}')">🔐 Recompute Hashes</button>
                            </div>
                            ` : ''}
                            ` : `
                            <div class="info-row">
                                <span class="info-value">
                                    ${canComputeHashes ? 
                                        '<button class="btn-compute-hash" onclick="computeHashes(\'' + entry._key + '\')">🔐 Compute Hashes</button>' :
                                        'Hashes not available for URL entries'
                                    }
                                </span>
                            </div>
                            `}
                        </div>
                    </div>
                    
                    ${entry.created_by ? `
                    <div class="info-section">
                        <h5>👤 Uploader</h5>
                        <div class="info-row">
                            <span class="info-label">Added By:</span>
                            <span class="info-value">${entry.created_by}</span>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${entry.metadata && Object.keys(entry.metadata).length > 0 ? `
                    <div class="info-section">
                        <h5>🔧 Additional Details</h5>
                        ${entry.metadata.original_filename ? `
                        <div class="info-row">
                            <span class="info-label">Filename:</span>
                            <span class="info-value small">${entry.metadata.original_filename}</span>
                        </div>
                        ` : ''}
                        ${entry.metadata.directory ? `
                        <div class="info-row">
                            <span class="info-label">Directory:</span>
                            <span class="info-value small">${entry.metadata.directory}</span>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    <div class="info-actions">
                        <button class="btn-download-full" onclick="document.getElementById('download-${entry._key}').click()">
                            ⬇️ Download This File
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // If hashes are processing, start polling for updates
        if (isProcessing) {
            setTimeout(() => pollForHashes(entry._key), 3000);
        }
        
        // Add hidden download trigger
        const downloadTrigger = document.createElement('a');
        downloadTrigger.id = `download-${entry._key}`;
        downloadTrigger.style.display = 'none';
        downloadTrigger.onclick = () => {
            handleDownload(entry);
            modal.remove();
        };
        document.body.appendChild(downloadTrigger);
    }
    
    // Compute hashes for a file
    window.computeHashes = async function(entryId) {
        const hashSection = document.getElementById(`hash-section-${entryId}`);
        if (!hashSection) return;
        
        // Show loading state
        hashSection.innerHTML = `
            <div class="info-row">
                <span class="info-value">⏳ Computing hashes in background... This may take a while for large files.</span>
            </div>
        `;
        
        try {
            const response = await fetch(`/api/entries/${encodeURIComponent(entryId)}/hashes`);
            const data = await response.json();
            
            if (data.success) {
                // Check if hashes are ready or still processing
                if (data.processing) {
                    // Hashes are being computed in background, poll for results
                    hashSection.innerHTML = `
                        <div class="info-row">
                            <span class="info-value">⏳ ${data.message}</span>
                        </div>
                    `;
                    // Poll every 3 seconds to check if hashes are ready
                    setTimeout(() => pollForHashes(entryId), 3000);
                } else if (data.md5 && data.sha256) {
                    // Hashes are ready
                    hashSection.innerHTML = `
                        ${data.cached ? '<div class="info-row"><span class="info-value" style="color: #5a9fd4;">✓ Retrieved from cache</span></div>' : ''}
                        <div class="info-row">
                            <span class="info-label">MD5:</span>
                            <span class="info-value hash-value">${data.md5}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">SHA256:</span>
                            <span class="info-value hash-value">${data.sha256}</span>
                        </div>
                    `;
                }
            } else {
                hashSection.innerHTML = `
                    <div class="info-row warning">
                        <span class="info-value">✗ Error: ${data.error}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-value">
                            <button class="btn-compute-hash" onclick="computeHashes('${entryId}')">🔐 Try Again</button>
                        </span>
                    </div>
                `;
            }
        } catch (error) {
            hashSection.innerHTML = `
                <div class="info-row warning">
                    <span class="info-value">✗ Failed to compute hashes</span>
                </div>
                <div class="info-row">
                    <span class="info-value">
                        <button class="btn-compute-hash" onclick="computeHashes('${entryId}')">🔐 Try Again</button>
                    </span>
                </div>
            `;
        }
    };
    
    // Poll for hash computation results
    async function pollForHashes(entryId, attempts = 0) {
        const hashSection = document.getElementById(`hash-section-${entryId}`);
        if (!hashSection) return;
        
        // Stop polling after 60 attempts at 3-second intervals (3 minutes)
        if (attempts >= 60) {
            hashSection.innerHTML = `
                <div class="info-row warning">
                    <span class="info-value">⏱ Hash computation is taking longer than expected. Please click Info again to check status.</span>
                </div>
                <div class="info-row">
                    <span class="info-value">
                        <button class="btn-compute-hash" onclick="computeHashes('${entryId}')">🔐 Check Again</button>
                    </span>
                </div>
            `;
            return;
        }
        
        try {
            // Fetch updated entry info to get latest hash status
            const response = await fetch(`/api/entries/${encodeURIComponent(entryId)}/info`);
            const data = await response.json();
            
            if (data.success && data.entry) {
                const entry = data.entry;
                const hasMD5 = entry.md5_hash && entry.md5_hash !== 'processing';
                const hasSHA256 = entry.sha256_hash && entry.sha256_hash !== 'processing';
                const isProcessing = entry.md5_hash === 'processing' || entry.sha256_hash === 'processing';
                
                if (hasMD5 && hasSHA256) {
                    // Hashes are ready
                    hashSection.innerHTML = `
                        <div class="info-row">
                            <span class="info-value" style="color: #5a9fd4;">✓ Hashes computed successfully!</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">MD5:</span>
                            <span class="info-value hash-value">${entry.md5_hash}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">SHA256:</span>
                            <span class="info-value hash-value">${entry.sha256_hash}</span>
                        </div>
                        <div class="info-row" style="margin-top: 10px;">
                            <button class="btn-compute-hash" onclick="computeHashes('${entryId}')">🔐 Recompute Hashes</button>
                        </div>
                    `;
                } else if (isProcessing) {
                    // Still processing, update the display and poll again
                    hashSection.innerHTML = `
                        <div class="info-row">
                            <span class="info-label">MD5:</span>
                            <span class="info-value"><em>Processing...</em></span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">SHA256:</span>
                            <span class="info-value"><em>Processing...</em></span>
                        </div>
                        <div class="info-row">
                            <span class="info-value" style="color: #5a9fd4;">⏳ Hash computation in progress (${attempts + 1}/60)...</span>
                        </div>
                    `;
                    setTimeout(() => pollForHashes(entryId, attempts + 1), 3000);
                } else {
                    // Something went wrong, hashes should be available but aren't
                    hashSection.innerHTML = `
                        <div class="info-row warning">
                            <span class="info-value">⚠ Hash computation may have failed</span>
                        </div>
                        <div class="info-row">
                            <span class="info-value">
                                <button class="btn-compute-hash" onclick="computeHashes('${entryId}')">🔐 Try Again</button>
                            </span>
                        </div>
                    `;
                }
            } else {
                // Continue polling on error
                setTimeout(() => pollForHashes(entryId, attempts + 1), 3000);
            }
        } catch (error) {
            // Log error but continue polling
            console.error('Error polling for hashes:', error);
            setTimeout(() => pollForHashes(entryId, attempts + 1), 3000);
        }
    }

    
    // Format full date
    function formatFullDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }
    
    // Handle report of an entry
    function handleReport(entry) {
        // Create modal for report submission
        const modal = document.createElement('div');
        modal.className = 'report-modal-overlay';
        modal.innerHTML = `
            <div class="report-modal">
                <div class="report-modal-header">
                    <h3>Report File Issue</h3>
                    <button class="modal-close" onclick="this.closest('.report-modal-overlay').remove()">✕</button>
                </div>
                <div class="report-modal-body">
                    <p><strong>File:</strong> ${entry.name}</p>
                    <form id="report-form">
                        <div class="form-group">
                            <label for="report-reason">Reason:</label>
                            <select id="report-reason" name="reason" required class="form-select">
                                <option value="">Select a reason...</option>
                                <option value="not_working">File Not Working</option>
                                <option value="corrupted">File Corrupted</option>
                                <option value="wrong_file">Wrong File</option>
                                <option value="missing_updates">Missing Updates/DLC</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="report-description">Additional Details (Optional):</label>
                            <textarea id="report-description" name="description" rows="4" 
                                class="form-textarea" placeholder="Describe the issue..."></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn-cancel" onclick="this.closest('.report-modal-overlay').remove()">
                                Cancel
                            </button>
                            <button type="submit" class="btn-submit">Submit Report</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle form submission
        const form = modal.querySelector('#report-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            formData.append('entry_id', entry._key);
            formData.append('entry_name', entry.name);
            
            const submitBtn = form.querySelector('.btn-submit');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            try {
                const response = await fetch('/api/reports/submit', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    Toast.success('Report submitted successfully. Thank you for helping improve our collection!');
                    setTimeout(() => {
                        modal.remove();
                        // Reload entries to update report counts
                        loadEntries();
                    }, 1500);
                } else {
                    Toast.error(data.error || 'Failed to submit report');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Report';
                }
            } catch (error) {
                Toast.error('Error submitting report. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Report';
            }
        });
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
