/**
 * FinTrack - Client-side Interactive Behaviors
 * Handles Theme Toggling (Dark/Light), Mobile Nav, Category Select Filtering, and Modals.
 */

// 1. THEME TOGGLE (Dark / Light Mode)
(function initTheme() {
    const savedTheme = localStorage.getItem('fintrack-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('fintrack-theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('fintrack-theme', 'dark');
            }
        });
    }

    // 2. MOBILE MENU TOGGLE
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 3. ESC KEY CLOSES MODALS
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAddModal();
        }
    });
});

// 4. ADD TRANSACTION MODAL CONTROLS
function openAddModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeAddModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// 5. DYNAMIC CATEGORY OPTIONS TOGGLE (Income vs Expense)
function toggleCategoryOptions(selectedType) {
    const expenseGroup = document.getElementById('expenseOptGroup');
    const incomeGroup = document.getElementById('incomeOptGroup');
    const categorySelect = document.getElementById('categorySelect');

    if (!expenseGroup || !incomeGroup || !categorySelect) return;

    if (selectedType === 'Expense') {
        expenseGroup.classList.remove('hidden');
        incomeGroup.classList.add('hidden');
        // Select first expense item
        if (expenseGroup.firstElementChild) {
            categorySelect.value = expenseGroup.firstElementChild.value;
        }
    } else {
        incomeGroup.classList.remove('hidden');
        expenseGroup.classList.add('hidden');
        // Select first income item
        if (incomeGroup.firstElementChild) {
            categorySelect.value = incomeGroup.firstElementChild.value;
        }
    }
}
