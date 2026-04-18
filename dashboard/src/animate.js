/**
 * Animates a numeric value from `from` to `to` over `duration` ms.
 * Calls `onUpdate(currentValue)` on each animation frame.
 * Uses an ease-out cubic curve.
 */
export function animateValue(from, to, duration, onUpdate) {
  if (from === to) { onUpdate(to); return; }
  const start = performance.now();
  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    onUpdate(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
