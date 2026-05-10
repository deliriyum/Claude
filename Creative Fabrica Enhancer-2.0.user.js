// ==UserScript==
// @name         Creative Fabrica Enhancer
// @namespace    http://tampermonkey.net/
// @version      2.1 - 2026-03-04 - Regex fix for URL extraction; ensure script loads
// @description  Remove annoying banner, add product modal preview, and batch download all visible items
// @author       Emily
// @match        https://www.creativefabrica.com/*
// @match        https://*.creativefabrica.com/*
// @grant        GM_addStyle
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    // ============================================
    // PART 1: MURDER THE BANNER (AGGRESSIVE MODE)
    // ============================================

    // JavaScript banner assassin - actively hunts and destroys banners
    function destroyBanners() {
        let bannersKilled = 0;

        // Strategy 1: Kill elements containing banner images
        const bannerImages = document.querySelectorAll('img[src*="CF_homepage_banner"], img[src*="banner"], img[alt*="Banner"], img[alt="Studio AI"]');
        bannerImages.forEach(img => {
            // Kill the image and its parent containers
            let parent = img.parentElement;
            let depth = 0;
            while (parent && depth < 5) {
                // If parent has banner-like characteristics, kill it
                const rect = parent.getBoundingClientRect();
                if (rect.height > 100 && rect.height < 500 && rect.width > 500) {
                    parent.remove();
                    bannersKilled++;
                    return;
                }
                parent = parent.parentElement;
                depth++;
            }
            // If we didn't find a good parent, just kill the image
            img.remove();
            bannersKilled++;
        });

        // Strategy 2: Kill variant renderer spans that contain promotional content
        const variantSpans = document.querySelectorAll('span[data-rendering-id], span[id*="rid-"]');
        variantSpans.forEach(span => {
            const text = span.textContent.toLowerCase();
            // Check for promotional keywords
            if (text.includes('trial') ||
                text.includes('upgrade') ||
                text.includes('million+') ||
                text.includes('studio ai') ||
                text.includes('creative assets')) {

                // Check if it's banner-sized
                const rect = span.getBoundingClientRect();
                if (rect.height > 80 && rect.width > 400) {
                    span.remove();
                    bannersKilled++;
                }
            }
        });

        // Strategy 3: Kill picture elements with absolute positioning (common banner pattern)
        const absolutePictures = document.querySelectorAll('picture.absolute, picture[class*="inset"]');
        absolutePictures.forEach(pic => {
            const rect = pic.getBoundingClientRect();
            if (rect.height > 100 && rect.height < 500) {
                pic.remove();
                bannersKilled++;
            }
        });

        // Strategy 4: Kill divs with bg-cover that are banner-sized
        const bgCoverDivs = document.querySelectorAll('div[class*="bg-cover"], div[class*="bg-center"]');
        bgCoverDivs.forEach(div => {
            const rect = div.getBoundingClientRect();
            // Banner-like dimensions
            if (rect.height > 100 && rect.height < 500 && rect.width > 500) {
                const hasPromoText = div.textContent.toLowerCase().includes('trial') ||
                                   div.textContent.toLowerCase().includes('upgrade') ||
                                   div.textContent.toLowerCase().includes('million');
                if (hasPromoText) {
                    div.remove();
                    bannersKilled++;
                }
            }
        });

        if (bannersKilled > 0) {
            console.log(`Destroyed ${bannersKilled} banner element(s)`);
        }
    }

    // CSS fallback - belt and suspenders approach
    GM_addStyle(`
        /* Hide the banner - targeting multiple possible containers */
        div.relative.flex.flex-col.justify-between[class*="gap"][class*="overflow-hidden"][class*="bg-cover"],
        div[class*="banner"],
        div[id*="banner"],
        span[id^="r1d-"] > span[class*="yearly-extend-other"],
        picture.absolute.inset-0 {
            display: none !important;
        }

        /* If there's a parent container that creates space for the banner, collapse it */
        div:has(> picture.absolute.inset-0) {
            display: none !important;
        }

        /* Hide the homepage banner with "12 Million+ Creative Assets" */
        img[alt="Creative Fabrica Homepage Banner"],
        img[src*="CF_homepage_banner"],
        div:has(> img[alt="Creative Fabrica Homepage Banner"]),
        div:has(> img[src*="CF_homepage_banner"]),
        span[data-rendering-id]:has(img[alt*="Homepage Banner"]),
        span.inline-static-variant-element:has(img[alt*="Homepage Banner"]),
        span[id*="rid-"]:has(div.relative.flex-col) {
            display: none !important;
        }

        /* Hide the "Studio AI" trial banner */
        img[alt="Studio AI"],
        div:has(> img[alt="Studio AI"]),
        div.bg-primary-100:has(img[alt="Studio AI"]),
        div:has(h2:contains("Start your free AI Studio trial")),
        span[data-rendering-id*="rid-"]:has(img[alt="Studio AI"]) {
            display: none !important;
        }

        /* Custom button styling for our new buttons */
        .cf-custom-btn {
            position: absolute;
            top: 8px;
            padding: 8px 14px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            z-index: 100;
            transition: all 0.2s ease, transform 0.1s ease;
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }

        .cf-custom-btn:hover {
            background: rgba(0, 0, 0, 0.95);
            border-color: rgba(255, 255, 255, 0.7);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .cf-custom-btn:active {
            transform: translateY(0) scale(0.95);
        }

        .cf-favorite-btn {
            right: 8px;
        }

        .cf-favorite-btn.is-favorited {
            background: rgba(239, 68, 68, 0.8);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .cf-favorite-btn.is-favorited:hover {
            background: rgba(220, 38, 38, 0.95);
        }

        .cf-download-btn {
            right: 8px;
            top: 48px;
        }

        /* Only show buttons on hover of the parent item container */
        .cf-item-container .cf-custom-btn {
            opacity: 0;
            pointer-events: none;
        }

        .cf-item-container:hover .cf-custom-btn {
            opacity: 1;
            pointer-events: auto;
        }

        /* If item is already favorited (has green checkmark), make sure we can detect it */
        .cf-item-container[data-favorited="true"] .cf-favorite-btn {
            background: rgba(239, 68, 68, 0.8);
        }

        /* Modal overlay styles */
        .cf-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: transparent;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            padding: 20px;
            pointer-events: none;
        }

        .cf-modal-overlay.cf-modal-visible {
            opacity: 1;
            pointer-events: auto;
        }

        .cf-modal-container {
            position: relative;
            width: 500px;
            max-width: 90%;
            max-height: 70vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            overflow: hidden;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }

        .cf-modal-overlay.cf-modal-visible .cf-modal-container {
            transform: scale(1);
        }

        .cf-modal-header {
            position: absolute;
            top: 0;
            right: 0;
            z-index: 10;
            padding: 12px;
        }

        .cf-modal-close {
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 24px;
            font-weight: bold;
            line-height: 1;
            transition: all 0.2s ease;
        }

        .cf-modal-close:hover {
            background: rgba(239, 68, 68, 0.9);
            border-color: rgba(255, 255, 255, 0.6);
            transform: rotate(90deg);
        }

        .cf-modal-content {
            width: 100%;
            height: 100%;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .cf-modal-product-image {
            width: 100%;
            max-height: 250px;
            object-fit: contain;
            border-radius: 8px;
            background: #f5f5f5;
        }

        .cf-modal-product-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin: 0;
            line-height: 1.3;
        }

        .cf-modal-product-desc {
            font-size: 13px;
            color: #666;
            line-height: 1.4;
            display: none;
        }

        .cf-modal-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .cf-modal-actions button,
        .cf-modal-actions a {
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .cf-modal-loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            color: #666;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }

        .cf-modal-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-top-color: #333;
            border-radius: 50%;
            animation: cf-spin 1s linear infinite;
        }

        @keyframes cf-spin {
            to { transform: rotate(360deg); }
        }

        /* Batch download button styles */
        .cf-batch-download-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 16px 24px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            z-index: 999998;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            user-select: none;
        }

        .cf-batch-download-btn:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(16, 185, 129, 0.5);
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }

        .cf-batch-download-btn:active {
            transform: translateY(-2px);
        }

        .cf-batch-download-btn.cf-downloading {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            cursor: wait;
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
        }

        .cf-batch-download-btn.cf-paused {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
        }

        .cf-batch-download-btn.cf-completed {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        }

        /* Progress indicator */
        .cf-progress-container {
            position: fixed;
            bottom: 90px;
            right: 24px;
            background: white;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            z-index: 999997;
            min-width: 300px;
            display: none;
        }

        .cf-progress-container.cf-visible {
            display: block;
        }

        .cf-progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .cf-progress-title {
            font-size: 14px;
            font-weight: 700;
            color: #333;
        }

        .cf-progress-count {
            font-size: 13px;
            color: #666;
        }

        .cf-progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .cf-progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
        }

        .cf-progress-current {
            font-size: 12px;
            color: #666;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .cf-progress-controls {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }

        .cf-progress-controls button {
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .cf-progress-pause-btn {
            background: #f59e0b;
            color: white;
        }

        .cf-progress-pause-btn:hover {
            background: #d97706;
        }

        .cf-progress-cancel-btn {
            background: #ef4444;
            color: white;
        }

        .cf-progress-cancel-btn:hover {
            background: #dc2626;
        }

        .cf-progress-resume-btn {
            background: #10b981;
            color: white;
        }

        .cf-progress-resume-btn:hover {
            background: #059669;
        }
    `);

    // ============================================
    // PART 2: MODAL FOR PRODUCT PREVIEW
    // ============================================

    let currentModal = null;

    async function showProductModal(url) {
        // Close existing modal if any
        if (currentModal) {
            closeProductModal();
        }

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'cf-modal-overlay';

        // Create modal container
        const container = document.createElement('div');
        container.className = 'cf-modal-container';

        // Create close button
        const header = document.createElement('div');
        header.className = 'cf-modal-header';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'cf-modal-close';
        closeBtn.innerHTML = '×';
        closeBtn.title = 'Close (ESC)';

        header.appendChild(closeBtn);
        container.appendChild(header);

        // Create loading indicator
        const loading = document.createElement('div');
        loading.className = 'cf-modal-loading';
        loading.innerHTML = '<div class="cf-modal-spinner"></div><div>Fetching product...</div>';
        container.appendChild(loading);

        // Create content container
        const content = document.createElement('div');
        content.className = 'cf-modal-content';
        content.style.display = 'none';
        container.appendChild(content);

        overlay.appendChild(container);
        document.body.appendChild(overlay);

        // Trigger animation
        requestAnimationFrame(() => {
            overlay.classList.add('cf-modal-visible');
        });

        // Close handler
        const closeModal = () => {
            overlay.classList.remove('cf-modal-visible');
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
                currentModal = null;
            }, 300);
        };

        closeBtn.onclick = closeModal;

        // Close on ESC key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        // Close when clicking outside
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                closeModal();
            }
        };

        container.onclick = (e) => {
            e.stopPropagation();
        };

        currentModal = overlay;

        // Fetch and parse the product page
        try {
            const response = await fetch(url);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Extract product information
            const productImage = doc.querySelector('img[src*="creativefabrica"], img[class*="product"], img[alt]');
            // Be more specific - h1 is usually the actual product name
            const productTitle = doc.querySelector('h1') || doc.querySelector('[class*="product-title"]');
            const productDesc = doc.querySelector('[class*="description"], [class*="excerpt"], p');

            // Find download button (exclude social media share buttons)
            const downloadButtons = doc.querySelectorAll(
                'a[href*="download"], ' +
                'button[class*="download"], ' +
                'a[class*="download"]'
            );

            // Filter out Pinterest, Facebook, Twitter, etc.
            let downloadButton = null;
            for (const btn of downloadButtons) {
                const href = btn.href || btn.getAttribute('href') || '';
                // Skip social media share buttons
                if (!href.includes('pinterest.com') &&
                    !href.includes('facebook.com') &&
                    !href.includes('twitter.com') &&
                    !href.includes('linkedin.com')) {
                    downloadButton = btn;
                    break;
                }
            }

            // Build modal content
            let contentHTML = '';

            if (productImage) {
                const imgSrc = productImage.src || productImage.getAttribute('data-src');
                if (imgSrc) {
                    contentHTML += `<img src="${imgSrc}" class="cf-modal-product-image" alt="Product" />`;
                }
            }

            if (productTitle) {
                contentHTML += `<h2 class="cf-modal-product-title">${productTitle.textContent.trim()}</h2>`;
            }

            if (productDesc && productDesc.textContent.trim().length > 0) {
                const descText = productDesc.textContent.trim().substring(0, 200);
                contentHTML += `<p class="cf-modal-product-desc">${descText}...</p>`;
            }

            // Add action buttons
            contentHTML += '<div class="cf-modal-actions">';

            if (downloadButton) {
                const downloadHref = downloadButton.href || downloadButton.getAttribute('href');
                if (downloadHref) {
                    contentHTML += `<a href="${downloadHref}" target="_blank" style="background: #10b981; color: white; border: none;">⬇️ Download</a>`;
                }
            }

            contentHTML += `<a href="${url}" target="_blank" style="background: #6366f1; color: white; border: none;">🔗 View Full Page</a>`;
            contentHTML += '</div>';

            content.innerHTML = contentHTML;

            // Add click handlers to close modal when clicking action buttons
            const actionButtons = content.querySelectorAll('.cf-modal-actions a');
            actionButtons.forEach(button => {
                button.addEventListener('click', () => {
                    // Close modal after a brief delay to let the link open
                    setTimeout(closeModal, 100);
                });
            });

            // Show content, hide loading
            loading.style.display = 'none';
            content.style.display = 'flex';

        } catch (error) {
            console.error('Error loading product page:', error);
            loading.innerHTML = `
                <div style="color: #ef4444; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 12px;">❌</div>
                    <div>Failed to load product</div>
                    <a href="${url}" target="_blank" style="display: inline-block; margin-top: 12px; padding: 8px 16px; background: #6366f1; color: white; text-decoration: none; border-radius: 6px;">Open in New Tab</a>
                </div>
            `;
        }
    }

    function closeProductModal() {
        if (currentModal) {
            currentModal.classList.remove('cf-modal-visible');
            setTimeout(() => {
                if (currentModal.parentNode) {
                    currentModal.parentNode.removeChild(currentModal);
                }
                currentModal = null;
            }, 300);
        }
    }

    // ============================================
    // PART 3: BATCH DOWNLOAD FUNCTIONALITY
    // ============================================

    let batchDownloadState = {
        isRunning: false,
        isPaused: false,
        currentIndex: 0,
        items: [],
        totalCount: 0,
        successCount: 0,
        failedCount: 0
    };

    function collectAllItems() {
        const selectors = [
            'a[href*="/product/"]:has(img)',
            'a[href*="/design/"]:has(img)',
            'a[href*="/graphic/"]:has(img)'
        ].join(', ');

        const items = [];

        document.querySelectorAll(selectors).forEach(element => {
            const url = element.href;
            const img = element.querySelector('img');
            const title = img?.alt || 'Unknown';

            if (url && !items.find(item => item.url === url)) {
                items.push({ url, title, element });
            }
        });

        // fallback: some pages (search) don't wrap cards in <a>, they may use data-href or onclick
        const altSelector = '[data-href*="/product/"], [data-href*="/design/"], [data-href*="/graphic/"]';
        document.querySelectorAll(altSelector).forEach(el => {
            const url = el.getAttribute('data-href');
            const img = el.querySelector('img');
            const title = img?.alt || 'Unknown';
            if (url && !items.find(item => item.url === url)) {
                items.push({ url, title, element: el });
            }
        });

        // another fallback: onclick handlers containing product path
        document.querySelectorAll('[onclick]').forEach(el => {
            const handler = el.getAttribute('onclick');
            if (handler && handler.includes('/product/')) {
                // try to extract url from string
                const match = handler.match(/['"](https?:\/\/[^'"]+)['"]/);
                if (match) {
                    const url = match[1];
                    const img = el.querySelector('img');
                    const title = img?.alt || 'Unknown';
                    if (url && !items.find(item => item.url === url)) {
                        items.push({ url, title, element: el });
                    }
                }
            }
        });

        return items;
    }

    async function downloadSingleItem(item, index, total) {
        updateProgress(index, total, `Downloading ${index + 1}/${total}: ${item.title}`);

        try {
            // Fetch the product page
            const response = await fetch(item.url);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Find download button (same logic as modal)
            const downloadButtons = doc.querySelectorAll(
                'a[href*="download"], ' +
                'button[class*="download"], ' +
                'a[class*="download"]'
            );

            // Filter out social media share buttons
            let downloadButton = null;
            for (const btn of downloadButtons) {
                const href = btn.href || btn.getAttribute('href') || '';
                if (!href.includes('pinterest.com') &&
                    !href.includes('facebook.com') &&
                    !href.includes('twitter.com') &&
                    !href.includes('linkedin.com')) {
                    downloadButton = btn;
                    break;
                }
            }

            if (downloadButton) {
                const downloadUrl = downloadButton.href || downloadButton.getAttribute('href');
                if (downloadUrl) {
                    // Trigger download by creating a hidden link and clicking it
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = ''; // Suggest download instead of navigation
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    batchDownloadState.successCount++;
                    console.log(`✓ Downloaded: ${item.title}`);
                    return true;
                }
            }

            console.warn(`✗ No download link found for: ${item.title}`);
            batchDownloadState.failedCount++;
            return false;

        } catch (error) {
            console.error(`✗ Error downloading ${item.title}:`, error);
            batchDownloadState.failedCount++;
            return false;
        }
    }

    async function startBatchDownload() {
        if (batchDownloadState.isRunning) {
            return;
        }

        // Collect all items
        const items = collectAllItems();
        console.log(`Batch downloader found ${items.length} item(s)`);
        if (items.length === 0) {
            alert('No items found on this page to download!');
            return;
        }

        // log matching urls for debugging
        items.forEach((it, idx) => console.log(`${idx+1}/${items.length}: ${it.url}`));

        // Confirm with user
        const confirmed = confirm(
            `Found ${items.length} item(s) on this page.\n\n` +
            `This will download them all with a 5-second delay between each.\n\n` +
            `Make sure you're in the correct download folder before continuing.\n\n` +
            `Continue?`
        );

        if (!confirmed) {
            return;
        }

        // Reset state
        batchDownloadState = {
            isRunning: true,
            isPaused: false,
            currentIndex: 0,
            items: items,
            totalCount: items.length,
            successCount: 0,
            failedCount: 0
        };

        // Update UI
        updateBatchButton('downloading', '⏸️ Pause');
        showProgress();

        // Process items one by one
        for (let i = 0; i < items.length; i++) {
            // Check if paused
            while (batchDownloadState.isPaused && batchDownloadState.isRunning) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // Check if cancelled
            if (!batchDownloadState.isRunning) {
                break;
            }

            batchDownloadState.currentIndex = i;
            await downloadSingleItem(items[i], i, items.length);

            // Wait 5 seconds before next download (unless it's the last one)
            if (i < items.length - 1 && batchDownloadState.isRunning) {
                for (let j = 0; j < 10; j++) {
                    // Check for pause/cancel during wait
                    if (!batchDownloadState.isRunning) break;
                    while (batchDownloadState.isPaused && batchDownloadState.isRunning) {
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
        }

        // Finished
        if (batchDownloadState.isRunning) {
            const message = `Batch download complete!\n\n` +
                `✓ Success: ${batchDownloadState.successCount}\n` +
                `✗ Failed: ${batchDownloadState.failedCount}\n` +
                `Total: ${batchDownloadState.totalCount}`;

            updateProgress(
                batchDownloadState.totalCount,
                batchDownloadState.totalCount,
                message.replace(/\n/g, ' ')
            );
            updateBatchButton('completed', '✓ Complete');

            setTimeout(() => {
                alert(message);
                resetBatchDownload();
            }, 1000);
        } else {
            resetBatchDownload();
        }
    }

    function pauseBatchDownload() {
        if (!batchDownloadState.isRunning) return;

        batchDownloadState.isPaused = !batchDownloadState.isPaused;

        if (batchDownloadState.isPaused) {
            updateBatchButton('paused', '▶️ Resume');
            updatePauseButton('▶️ Resume');
        } else {
            updateBatchButton('downloading', '⏸️ Pause');
            updatePauseButton('⏸️ Pause');
        }
    }

    function cancelBatchDownload() {
        if (!batchDownloadState.isRunning) return;

        const confirmed = confirm(
            `Cancel batch download?\n\n` +
            `Progress: ${batchDownloadState.currentIndex + 1}/${batchDownloadState.totalCount}\n` +
            `Success: ${batchDownloadState.successCount}\n` +
            `Failed: ${batchDownloadState.failedCount}`
        );

        if (confirmed) {
            batchDownloadState.isRunning = false;
            resetBatchDownload();
        }
    }

    function resetBatchDownload() {
        batchDownloadState = {
            isRunning: false,
            isPaused: false,
            currentIndex: 0,
            items: [],
            totalCount: 0,
            successCount: 0,
            failedCount: 0
        };

        updateBatchButton('idle', '📥 Batch Download');
        hideProgress();
    }

    // ============================================
    // PART 4: ADD BUTTONS TO PREVIEW IMAGES
    // ============================================

    function addButtonsToItem(itemElement) {
        // Skip if we've already processed this item
        if (itemElement.classList.contains('cf-processed')) {
            return;
        }
        itemElement.classList.add('cf-processed', 'cf-item-container');

        // Make sure the item has relative positioning for absolute button placement
        if (getComputedStyle(itemElement).position === 'static') {
            itemElement.style.position = 'relative';
        }

        // Check if item is already favorited (solid heart vs outline heart)
        // Look for heart icon and determine if it's filled
        const heartElement = itemElement.querySelector(
            'svg[class*="heart"], ' +
            'path[d*="M20.84"], ' +
            '[class*="favorite"] svg, ' +
            '[aria-label*="favorite"] svg'
        );

        let isFavorited = false;
        if (heartElement) {
            // Check if the heart is filled (multiple detection methods)
            const parent = heartElement.closest('button, a, div');
            const computedStyle = window.getComputedStyle(heartElement);
            const hasFill = heartElement.getAttribute('fill') && heartElement.getAttribute('fill') !== 'none';
            const hasFilledClass = heartElement.className.toString().match(/fill|solid|active|favorited/i);
            const hasRedColor = computedStyle.fill?.includes('rgb(255') || computedStyle.color?.includes('rgb(255');

            isFavorited = !!(hasFill || hasFilledClass || hasRedColor);
        }

        if (isFavorited) {
            itemElement.setAttribute('data-favorited', 'true');
        }

        // Get the item's link for navigation
        // If this element itself is a link, use it directly
        let itemUrl = null;
        if (itemElement.tagName === 'A' && itemElement.href &&
            (itemElement.href.includes('/product/') || itemElement.href.includes('/design/') || itemElement.href.includes('/graphic/'))) {
            itemUrl = itemElement.href;
        } else {
            // Otherwise, find the first product link within this item
            const itemLink = itemElement.querySelector('a[href*="/product/"], a[href*="/design/"], a[href*="/graphic/"]');
            itemUrl = itemLink ? itemLink.href : null;
        }

        // Click-to-preview functionality
        if (itemUrl) {
            // Show modal on click
            itemElement.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent default navigation
                e.stopPropagation(); // Stop event from bubbling
                showProductModal(itemUrl);
            });

            // Add visual feedback - cursor pointer on hover
            itemElement.style.cursor = 'pointer';
        }

        // REMOVED: Favorite/Download buttons on cards (click modal replaced this functionality)
        // The click modal provides a cleaner UX without cluttering the cards with buttons
    }

    // Function to find and process item containers
    function processItems() {
        // Creative Fabrica uses various selectors for item cards depending on the view
        // Let's be comprehensive and catch everything
        // IMPORTANT: Only select the <a> links themselves, not parent containers
        // This prevents multiple nested elements from all triggering hover events
        const selectors = [
            // Product links with images (most specific - use these!)
            'a[href*="/product/"]:has(img)',
            'a[href*="/design/"]:has(img)',
            'a[href*="/graphic/"]:has(img)'
        ].join(', ');

        const items = document.querySelectorAll(selectors);

        let processedCount = 0;
        let skippedCount = 0;

        items.forEach(item => {
            // Make sure this element contains an image (final validation)
            // Accept any image, including lazy-loaded ones
            const hasImage = item.querySelector('img');
            const alreadyProcessed = item.classList.contains('cf-processed');

            if (!hasImage) {
                skippedCount++;
            } else if (alreadyProcessed) {
                skippedCount++;
            } else {
                addButtonsToItem(item);
                processedCount++;
            }
        });
    }

    // ============================================
    // PART 5: UI CREATION AND HELPERS
    // ============================================

    let batchButton = null;
    let progressContainer = null;

    function createBatchDownloadUI() {
        // Create batch download button
        batchButton = document.createElement('button');
        batchButton.className = 'cf-batch-download-btn';
        batchButton.innerHTML = '📥 Batch Download';
        batchButton.onclick = handleBatchButtonClick;
        document.body.appendChild(batchButton);

        // Create progress indicator
        progressContainer = document.createElement('div');
        progressContainer.className = 'cf-progress-container';
        progressContainer.innerHTML = `
            <div class="cf-progress-header">
                <div class="cf-progress-title">Batch Download</div>
                <div class="cf-progress-count">0/0</div>
            </div>
            <div class="cf-progress-bar">
                <div class="cf-progress-bar-fill"></div>
            </div>
            <div class="cf-progress-current">Ready...</div>
            <div class="cf-progress-controls">
                <button class="cf-progress-pause-btn">⏸️ Pause</button>
                <button class="cf-progress-cancel-btn">✕ Cancel</button>
            </div>
        `;
        document.body.appendChild(progressContainer);

        // Add event listeners to progress controls
        const pauseBtn = progressContainer.querySelector('.cf-progress-pause-btn');
        const cancelBtn = progressContainer.querySelector('.cf-progress-cancel-btn');

        pauseBtn.onclick = pauseBatchDownload;
        cancelBtn.onclick = cancelBatchDownload;
    }

    function handleBatchButtonClick() {
        if (batchDownloadState.isRunning) {
            pauseBatchDownload();
        } else {
            startBatchDownload();
        }
    }

    function updateBatchButton(state, text) {
        if (!batchButton) return;

        batchButton.className = 'cf-batch-download-btn';
        if (state === 'downloading') {
            batchButton.classList.add('cf-downloading');
        } else if (state === 'paused') {
            batchButton.classList.add('cf-paused');
        } else if (state === 'completed') {
            batchButton.classList.add('cf-completed');
        }

        batchButton.innerHTML = text;
    }

    function updatePauseButton(text) {
        if (!progressContainer) return;
        const pauseBtn = progressContainer.querySelector('.cf-progress-pause-btn');
        if (pauseBtn) {
            pauseBtn.innerHTML = text;
        }
    }

    function showProgress() {
        if (progressContainer) {
            progressContainer.classList.add('cf-visible');
        }
    }

    function hideProgress() {
        if (progressContainer) {
            progressContainer.classList.remove('cf-visible');
        }
    }

    function updateProgress(current, total, message) {
        if (!progressContainer) return;

        const countEl = progressContainer.querySelector('.cf-progress-count');
        const fillEl = progressContainer.querySelector('.cf-progress-bar-fill');
        const currentEl = progressContainer.querySelector('.cf-progress-current');

        if (countEl) {
            countEl.textContent = `${current + 1}/${total}`;
        }

        if (fillEl) {
            const percent = ((current + 1) / total) * 100;
            fillEl.style.width = `${percent}%`;
        }

        if (currentEl) {
            currentEl.textContent = message;
        }
    }

    // Watch for dynamically loaded content
    const observer = new MutationObserver((mutations) => {
        destroyBanners(); // Kill banners on every DOM change
        processItems();
        ensureBatchUI(); // keep the button around if site wiped it out
    });

    // Start observing when DOM is ready
    function init() {
        destroyBanners(); // Initial banner destruction
        processItems();
        createBatchDownloadUI(); // Create batch download button

        // Observe the whole document for new items
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // helper to ensure UI exists
    function ensureBatchUI() {
        if (!batchButton || !document.body.contains(batchButton)) {
            console.log('Re-creating batch download UI');
            createBatchDownloadUI();
        }
    }

    // Run banner destroyer immediately (before DOM is even ready)
    destroyBanners();

    // Run when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Also run on any navigation changes (for SPAs)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            destroyBanners(); // Kill banners on navigation
            setTimeout(() => {
                processItems();
                ensureBatchUI();
            }, 500);
        }
    }).observe(document, {subtree: true, childList: true});

    // Nuclear option: Run banner destroyer every 2 seconds
    setInterval(destroyBanners, 2000);

    console.log('Creative Fabrica Enhancer v2.1 loaded! Features: Banner removal, click-to-preview, and batch download.');
})();
