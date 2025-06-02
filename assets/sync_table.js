// dash_multi_tab_dashboard/assets/synchronized_scroll.js

// Ensure this script runs after the DOM is fully loaded
window.addEventListener('DOMContentLoaded', (event) => {
    // We will use a MutationObserver to detect when new sync table containers are added to the DOM,
    // especially relevant for dynamically created tabs.
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(node => {
                    // Check if the added node is a container for synchronized tables
                    // or if it contains such a container.
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const containers = node.querySelectorAll('[data-table-ids]');
                        containers.forEach(container => {
                            initializeSyncScrollForContainer(container);
                        });
                        // If the node itself is a container
                        if (node.matches && node.matches('[data-table-ids]')) {
                             initializeSyncScrollForContainer(node);
                        }
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Initial check for any tables present on page load
    document.querySelectorAll('[data-table-ids]').forEach(container => {
        initializeSyncScrollForContainer(container);
    });
});


function initializeSyncScrollForContainer(containerElement) {
    const tableIdsString = containerElement.getAttribute('data-table-ids');
    if (!tableIdsString || containerElement.dataset.syncInitialized === 'true') {
        return; // Already initialized or no table IDs
    }

    const tableIds = tableIdsString.split(',');
    if (tableIds.length < 2) return; // Need at least two tables to sync

    const tables = tableIds.map(id => document.getElementById(id));
    const masterTableEl = tables[0] ? tables[0].querySelector('.dash-spreadsheet-container .dash-spreadsheet-inner') : null;
    const slaveTableEls = tables.slice(1).map(table => table ? table.querySelector('.dash-spreadsheet-container .dash-spreadsheet-inner') : null).filter(el => el !== null);

    if (!masterTableEl || slaveTableEls.length === 0) {
        console.warn("Synchronized tables: Master or slave table scrollable elements not found for container:", containerElement, "with IDs:", tableIds);
        return;
    }

    // console.log("Initializing sync scroll for master:", masterTableEl, "and slaves:", slaveTableEls);

    let scrolling = false; // Flag to prevent scroll event loops

    masterTableEl.addEventListener('scroll', function() {
        if (scrolling) return;
        scrolling = true;
        const scrollTop = this.scrollTop;
        slaveTableEls.forEach(slave => {
            if (slave.scrollTop !== scrollTop) {
                slave.scrollTop = scrollTop;
            }
        });
        requestAnimationFrame(() => { scrolling = false; }); // Reset flag in next frame
    });

    slaveTableEls.forEach(slave => {
        slave.addEventListener('scroll', function() {
            if (scrolling) return;
            scrolling = true;
            const scrollTop = this.scrollTop;
            if (masterTableEl.scrollTop !== scrollTop) {
                masterTableEl.scrollTop = scrollTop;
            }
            // Sync other slaves as well
            slaveTableEls.forEach(otherSlave => {
                if (otherSlave !== this && otherSlave.scrollTop !== scrollTop) {
                    otherSlave.scrollTop = scrollTop;
                }
            });
            requestAnimationFrame(() => { scrolling = false; });
        });
    });
    containerElement.dataset.syncInitialized = 'true'; // Mark as initialized
    // console.log("Sync scroll initialized for container:", containerElement);
}
