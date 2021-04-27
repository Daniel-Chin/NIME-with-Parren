const MSPF = 50;

let theSpan;
let last_millis = null;

window.onload = () => {
  window.addEventListener("deviceorientation", handleOrientation, true);
  theSpan = document.getElementById('the-span');
};

const handleOrientation = ({
  absolute, alpha, beta, gamma
}) => {
  const now = new Date();
  if (last_millis === null) {
    last_millis = now;
  }
  if (now - last_millis >= MSPF) {
    last_millis = now;
    const msg = `${absolute},${alpha},${beta},${gamma}`;
    // console.log({ absolute, alpha, beta, gamma });
    send(msg);
    theSpan.innerHTML = msg
      .replace(',', '<br />')
      .replace(',', '<br />')
      .replace(',', '<br />');
  }
};

const send = (x) => {
  const xhttp = new XMLHttpRequest();
  xhttp.open("GET", x, true);
  xhttp.send();
};
