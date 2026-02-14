/**
 * Modern Custom Dropdown Component
 * Converts native select elements into stylish, interactive dropdowns
 */

class CustomDropdown {
    constructor(selectElement) {
        this.select = selectElement;
        this.options = Array.from(this.select.options);
        this.selectedIndex = this.select.selectedIndex;
        this.isOpen = false;
        
        this.createCustomDropdown();
        this.bindEvents();
    }

    createCustomDropdown() {
        // Create wrapper
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'custom-dropdown-wrapper';
        
        // Create custom dropdown
        this.customDropdown = document.createElement('div');
        this.customDropdown.className = 'custom-dropdown';
        
        // Create selected display
        this.selectedDisplay = document.createElement('div');
        this.selectedDisplay.className = 'custom-dropdown-selected';
        this.selectedDisplay.innerHTML = `
            <span class="selected-text">${this.options[this.selectedIndex].text}</span>
            <svg class="dropdown-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
        
        // Create dropdown menu
        this.dropdownMenu = document.createElement('div');
        this.dropdownMenu.className = 'custom-dropdown-menu';
        
        // Add search input if there are many options
        if (this.options.length > 5) {
            this.searchInput = document.createElement('input');
            this.searchInput.type = 'text';
            this.searchInput.className = 'dropdown-search';
            this.searchInput.placeholder = 'Search...';
            this.dropdownMenu.appendChild(this.searchInput);
        }
        
        // Create options list
        this.optionsList = document.createElement('div');
        this.optionsList.className = 'dropdown-options';
        
        this.options.forEach((option, index) => {
            const optionItem = document.createElement('div');
            optionItem.className = 'dropdown-option';
            if (index === this.selectedIndex) {
                optionItem.classList.add('selected');
            }
            optionItem.textContent = option.text;
            optionItem.dataset.value = option.value;
            optionItem.dataset.index = index;
            this.optionsList.appendChild(optionItem);
        });
        
        this.dropdownMenu.appendChild(this.optionsList);
        this.customDropdown.appendChild(this.selectedDisplay);
        this.customDropdown.appendChild(this.dropdownMenu);
        this.wrapper.appendChild(this.customDropdown);
        
        // Replace select with custom dropdown
        this.select.style.display = 'none';
        this.select.parentNode.insertBefore(this.wrapper, this.select);
    }

    bindEvents() {
        // Toggle dropdown
        this.selectedDisplay.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Select option
        this.optionsList.addEventListener('click', (e) => {
            if (e.target.classList.contains('dropdown-option')) {
                this.selectOption(e.target);
            }
        });
        
        // Search functionality
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.filterOptions(e.target.value);
            });
            
            this.searchInput.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Keyboard navigation
        this.customDropdown.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        this.isOpen = true;
        this.customDropdown.classList.add('open');
        this.dropdownMenu.style.display = 'block';
        
        // Focus search input if available
        if (this.searchInput) {
            setTimeout(() => this.searchInput.focus(), 100);
        }
        
        // Animate options
        const options = this.optionsList.querySelectorAll('.dropdown-option');
        options.forEach((option, index) => {
            option.style.animationDelay = `${index * 0.02}s`;
        });
    }

    closeDropdown() {
        this.isOpen = false;
        this.customDropdown.classList.remove('open');
        
        setTimeout(() => {
            this.dropdownMenu.style.display = 'none';
            if (this.searchInput) {
                this.searchInput.value = '';
                this.filterOptions('');
            }
        }, 200);
    }

    selectOption(optionElement) {
        const index = parseInt(optionElement.dataset.index);
        const value = optionElement.dataset.value;
        
        // Update selected state
        this.optionsList.querySelectorAll('.dropdown-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        optionElement.classList.add('selected');
        
        // Update display
        this.selectedDisplay.querySelector('.selected-text').textContent = optionElement.textContent;
        
        // Update original select
        this.select.selectedIndex = index;
        this.select.value = value;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        this.select.dispatchEvent(event);
        
        this.closeDropdown();
    }

    filterOptions(searchTerm) {
        const term = searchTerm.toLowerCase();
        const options = this.optionsList.querySelectorAll('.dropdown-option');
        
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            if (text.includes(term)) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });
    }

    handleKeyboard(e) {
        if (!this.isOpen) return;
        
        const visibleOptions = Array.from(
            this.optionsList.querySelectorAll('.dropdown-option:not([style*="display: none"])')
        );
        const currentIndex = visibleOptions.findIndex(opt => opt.classList.contains('selected'));
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (currentIndex < visibleOptions.length - 1) {
                    this.selectOption(visibleOptions[currentIndex + 1]);
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if (currentIndex > 0) {
                    this.selectOption(visibleOptions[currentIndex - 1]);
                }
                break;
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0) {
                    this.selectOption(visibleOptions[currentIndex]);
                }
                break;
            case 'Escape':
                e.preventDefault();
                this.closeDropdown();
                break;
        }
    }
}

// Initialize all custom dropdowns
function initCustomDropdowns() {
    // Target filter-select class and sort-select class, and selects in forms with specific IDs
    const selects = document.querySelectorAll('.filter-select, .sort-select, #type, #directory_id, #request_type');
    selects.forEach(select => {
        new CustomDropdown(select);
    });
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCustomDropdowns);
} else {
    initCustomDropdowns();
}
