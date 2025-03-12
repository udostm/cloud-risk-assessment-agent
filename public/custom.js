(function() {
  // Function to simulate the click after a delay if the URL is "/"
  function handlePageLoad() {
    if (window.location.pathname !== "/") {
      return; // Exit if not on the root page
    }
    setTimeout(function () {
      var readmeButton = document.getElementById('readme-button');
      if (readmeButton) {
        readmeButton.click();
      }
    }, 1000); // 1-second delay
  }

  // Run when the DOM is initially loaded
  document.addEventListener('DOMContentLoaded', handlePageLoad);

  // Monkey-patch history methods to dispatch a custom "locationchange" event
  (function(history) {
    var pushState = history.pushState;
    var replaceState = history.replaceState;

    history.pushState = function() {
      var ret = pushState.apply(history, arguments);
      window.dispatchEvent(new Event('locationchange'));
      return ret;
    };

    history.replaceState = function() {
      var ret = replaceState.apply(history, arguments);
      window.dispatchEvent(new Event('locationchange'));
      return ret;
    };

    // Listen for back/forward events
    window.addEventListener('popstate', function() {
      window.dispatchEvent(new Event('locationchange'));
    });
  })(window.history);

  // Listen for URL changes and only invoke handlePageLoad if at root "/"
  window.addEventListener('locationchange', handlePageLoad);
})();

