(() => {
  if (window.parent === window) return;
  const card = document.querySelector('.card');
  let frame;
  const reportHeight = () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      // Only the content height is shared; no location or weather data.
      window.parent.postMessage({
        type: 'weather:resize',
        height: Math.ceil(card.getBoundingClientRect().height),
      }, '*');
    });
  };
  const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(reportHeight);
  observer?.observe(card);
  window.addEventListener('resize', reportHeight);
  window.addEventListener('load', reportHeight);
  window.addEventListener('pagehide', () => {
    observer?.disconnect();
    cancelAnimationFrame(frame);
    window.removeEventListener('resize', reportHeight);
    window.removeEventListener('load', reportHeight);
  }, { once: true });
  reportHeight();
})();
