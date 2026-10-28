(() => {
  const status = document.getElementById('location-status');
  const search = document.querySelector('.search');
  let searching = false;
  // A pending location callback must not interrupt a visitor's city search.
  search.addEventListener('input', () => { searching = true; });
  search.addEventListener('submit', () => { searching = true; });

  const fallback = () => {
    status.textContent = 'Location unavailable or access denied. Search by city below.';
  };

  if (!navigator.geolocation) {
    fallback();
    return;
  }

  status.textContent = 'Finding your location… You can also search by city.';
  try {
    navigator.geolocation.getCurrentPosition(({ coords }) => {
      if (searching) return;
      const { latitude, longitude } = coords;
      if (!Number.isFinite(latitude) || !Number.isFinite(longitude)
          || Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
        fallback();
        return;
      }
      const url = new URL(window.location.href);
      url.search = new URLSearchParams({ lat: latitude, lon: longitude });
      window.location.replace(url.href);
    }, fallback, { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
  } catch {
    fallback();
  }
})();
