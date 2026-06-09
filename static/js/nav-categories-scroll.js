(function () {
    const DESKTOP_MIN = 992;
    const SCROLL_EDGE = 4;

    function initNavScroll(wrap) {
        const scrollEl = wrap.querySelector('[data-nav-scroll]');
        const prevBtn = wrap.querySelector('[data-nav-scroll-prev]');
        const nextBtn = wrap.querySelector('[data-nav-scroll-next]');
        if (!scrollEl || !prevBtn || !nextBtn) {
            return;
        }

        function isMobileTablet() {
            return window.matchMedia('(max-width: 991.98px)').matches;
        }

        function scrollAmount() {
            return Math.max(scrollEl.clientWidth * 0.65, 120);
        }

        function updateControls() {
            if (!isMobileTablet()) {
                wrap.classList.remove('is-scrollable', 'can-scroll-start', 'can-scroll-end');
                prevBtn.hidden = true;
                nextBtn.hidden = true;
                return;
            }

            const maxScroll = scrollEl.scrollWidth - scrollEl.clientWidth;
            const canScroll = maxScroll > SCROLL_EDGE;

            wrap.classList.toggle('is-scrollable', canScroll);

            if (!canScroll) {
                wrap.classList.remove('can-scroll-start', 'can-scroll-end');
                prevBtn.hidden = true;
                nextBtn.hidden = true;
                return;
            }

            const atStart = scrollEl.scrollLeft <= SCROLL_EDGE;
            const atEnd = scrollEl.scrollLeft >= maxScroll - SCROLL_EDGE;

            prevBtn.hidden = atStart;
            nextBtn.hidden = atEnd;

            wrap.classList.toggle('can-scroll-start', !atStart);
            wrap.classList.toggle('can-scroll-end', !atEnd);
        }

        function scrollByDirection(direction) {
            scrollEl.scrollBy({
                left: direction * scrollAmount(),
                behavior: 'smooth',
            });
        }

        prevBtn.addEventListener('click', function () {
            scrollByDirection(-1);
        });

        nextBtn.addEventListener('click', function () {
            scrollByDirection(1);
        });

        scrollEl.addEventListener('scroll', updateControls, { passive: true });

        window.addEventListener('resize', updateControls);

        if (typeof ResizeObserver !== 'undefined') {
            const ro = new ResizeObserver(updateControls);
            ro.observe(scrollEl);
            Array.from(scrollEl.children).forEach(function (child) {
                ro.observe(child);
            });
        }

        updateControls();
    }

    document.querySelectorAll('[data-nav-scroll-wrap]').forEach(initNavScroll);
})();
