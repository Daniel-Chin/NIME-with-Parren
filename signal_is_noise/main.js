const WIGGLE = 0;
const ZOOMY = .3;
const TOP = 150;
const WIDTH = 640;
const HEIGHT = 120;
const SCALE = .3;

const TEXT = [
  'your ', 
  'sig', 
  'nal ', 
  'is ', 
  'oth', 
  'er ', 
  'peo', 
  'ples ', 
  'noise ', 
];

let stop = false;
let cursor = 0;
let text_i = 0;
let _zoomy = 0.02;
let mode = 0;
let acc = 0;

function setup() {
  createCanvas(WIDTH, HEIGHT + TOP);
  background(128);
  noStroke();
  frameRate(10);
}

function draw() {
  if (stop) return;
  // print('y', 100, 100);
}

function keyPressed() {
  if (key === 'q') {
    stop = true;
  } else if (key === ']') {
    acc ++;
    if (acc == 9 * 4 + 1) {
      _zoomy = ZOOMY;
      mode = 1;
    }
    for (const char of TEXT[text_i]) {
      cursor += print(char, cursor, TOP);
      cursor %= (WIDTH - 60 * SCALE);
    }
    text_i ++;
    if (text_i == TEXT.length) {
      text_i = 0;
      if (mode == 0) {
        cursor = 0;
      }
    }
  }
}

const print = (char, char_x, char_y) => {
  const _scale = SCALE * (1 + random(_zoomy));
  const letter = [...VERDANA[char]];
  const char_width = letter.shift() * _scale;
  fill(255, 0, 0);
  stroke(255, 0, 0)
  for (const _bihua of letter) {
    const bihua = [..._bihua];
    const do_close = bihua.shift() === CLOSE;
    let first = null;
    let lax, lay, lbx, lby;
    for (let [ ax, ay, bx, by ] of bihua) {
      ax += random(WIGGLE);
      ay += random(WIGGLE);
      bx += random(WIGGLE);
      by += random(WIGGLE);
      ax *= _scale;
      ay *= _scale;
      bx *= _scale;
      by *= _scale;
      if (first === null) {
        first = [ ax, ay, bx, by ];
      } else {
        quad(lbx, lby, lax, lay, ax, ay, bx, by);
      }
      [ lax, lay, lbx, lby ] = [ ax, ay, bx, by ];
    }
    if (do_close) {
      quad(lbx, lby, lax, lay, ...first);
    }
  }
  let y = 0;
  while (y < 100 + WIGGLE) {
    let x = 0;
    while (x <= char_width + WIGGLE) {
      if (get(x, y)[0] === 255) {
        const dest_x = char_x + x;
        const dest_y = char_y + y;
        if (get(dest_x, dest_y)[0] === 0) {
          fill(255);
          stroke(255);
        } else {
          fill(0);
          stroke(0);
        }
        rect(dest_x, dest_y, -1, -1);
      }
      x ++;
    }
    y ++;
  }
  fill(0);
  stroke(0);
  rect(0, 0, WIDTH, 100 + WIGGLE);
  return char_width + random(WIGGLE);
};
