// OpenClaw UI Markdown Streaming Fix
// Paste this in Chrome DevTools Console to test
//
// Problem: During streaming, markdown is fully re-parsed on every token
// Fix: Debounce markdown rendering during streaming

(function() {
  // Intercept the marked.parse function
  if (typeof marked === 'undefined') {
    console.log('[md-fix] marked not found on window, trying to patch DOMPurify.sanitize instead');
  }
  
  // Debounce wrapper for expensive operations
  let lastRender = 0;
  let pendingRender = null;
  const DEBOUNCE_MS = 100; // Only render every 100ms during streaming
  
  // Patch DOMPurify.sanitize which is always called
  if (typeof DOMPurify !== 'undefined') {
    const origSanitize = DOMPurify.sanitize.bind(DOMPurify);
    let callCount = 0;
    
    DOMPurify.sanitize = function(dirty, config) {
      callCount++;
      const now = performance.now();
      
      // Log every 10th call to see frequency
      if (callCount % 10 === 0) {
        console.log(`[md-fix] DOMPurify.sanitize called ${callCount} times, input length: ${dirty?.length || 0}`);
      }
      
      return origSanitize(dirty, config);
    };
    
    console.log('[md-fix] DOMPurify.sanitize instrumented - watching call frequency');
  } else {
    console.log('[md-fix] DOMPurify not found');
  }
  
  console.log('[md-fix] Patch loaded. Send a message and watch the console for sanitize call frequency.');
})();
