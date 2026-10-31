// Timing of the board, the verdicts and the B-roll beats, on the ORIGINAL (uploaded timeline) clock.
// index.html reads it for the animation; composite.py reads the board windows as its split windows.
window.BEATS = {
  // board (split) windows: the item is introduced, then rated
  board: [[1.2, 7.0], [21.3, 27.5], [39.3, 45.4], [57.1, 64.0], [90.2, 95.0], [106.6, 113.5], [121.6, 128.0], [141.0, 143.5]],
  // [element, appears, verdict spoken, side g/b]
  items: [["#i1", 1.3, 3.2, "b"], ["#i2", 21.6, 24.3, "g"], ["#i3", 39.5, 42.3, "g"], ["#i4", 57.3, 60.6, "b"],
          ["#i5", 90.4, 92.6, "b"], ["#i6", 106.9, 110.6, "g"], ["#i7", 121.9, 124.0, "g"]],
  // full-screen B-roll beats: [start, ...cue times..., end]
  scenes: {
    b1: [7.0, 8.0, 16.4, 21.3],
    b2: [27.5, 33.1, 36.4, 39.3],
    b3: [45.4, 48.6, 54.3, 57.1],
    b4: [64.0, 76.4, 81.6, 88.0, 90.2],
    b5: [95.0, 96.7, 102.0, 104.4, 106.6],
    b6: [113.5, 115.9, 118.8, 121.6],
    b7: [128.0, [135.1, 137.2, 138.6, 139.6, 140.3], 140.6, 141.0],
  },
};
BEATS.modes = [
  ...BEATS.board.map(([a, b]) => ["split", a, b]),
  ...Object.values(BEATS.scenes).map((v) => ["broll", v[0], v[v.length - 1]]),
];
